"""
Renderers for convetional and bulk requests.
"""
from rest_framework import renderers
from . import JSONAPI_VERSION
from .exceptions import JsonApiException
from .utils import api as api_utils

class JsonApiRenderer(renderers.JSONRenderer):
    """
    Extends the DRF JSONRenderer to represent resources/Django model's in accordance with
    the JSON API specification.

    When using this serializer, it's important to carefully consider the Field
    chosen to represent *to-one* and *to-many* relationships.

    This renderer class represents serializer fields defined as ``PrimaryKeyRelatedField``
    and ``ManyRelatedField`` models as simple *Resource Object Identifiers* and does not
    create full resources in the top-level ``included`` member of the JSON API document.
    Serializer fields that are set to be represented through a ``ModelSerializer``
    (whether set to ``many=True`` or not) will have full resources in the ``included``
    top-level member.
    """
    media_type = 'application/vnd.api+json'
    format = 'vnd.api+json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Overrides the DRF JSONRenderer to comply with JSON API specification.

        JSON API requires that relationships (*to-many* and *to-one*) be
        represented as one of the following:

        - 'null' for empty to-one relationships.
        - An empty array ([]) for empty to-many relationships.
        - A single resource identifier object for non-empty to-one relationships.
        - An array of resource identifier objects for non-empty to-many relationships

        Returns:
            JSON response
        """
        view = renderer_context.get('view', None)
        # Check for view
        if not view:
            raise JsonApiException('A view is necessary for JSON API rendering.')
        # The default exception handler prepares an 'errors' JSON API document
        if api_utils.is_errors_view(view):
            jsonapi_document = data
        # Handle 'data' JSON API document
        else:
            jsonapi_document = {}
            if data is not None:
                if api_utils.is_paginated_list_view(data):
                    jsonapi_document = api_utils.list_to_jsonapi_document(data)
                elif api_utils.is_unpaginated_list_view(data):
                    jsonapi_document = api_utils.list_to_jsonapi_document(data, paginated=False)
                elif api_utils.is_single_resource_view(view, data):
                    jsonapi_document = api_utils.resource_to_jsonapi_document(data)
                else:
                    jsonapi_document = data
            jsonapi_document['jsonapi'] = {'version': JSONAPI_VERSION}
        return super(JsonApiRenderer, self).render(jsonapi_document,
                                                   accepted_media_type=accepted_media_type,
                                                   renderer_context=renderer_context)


class JsonApiBulkRenderer(JsonApiRenderer):
    """
    Renderer for JSON API bulk extension requests. It is derived
    from :py:class:`~.JsonApiRenderer` but the media type
    indicates use of the bulk extension.

    Returns:
        JSON response
    """
    media_type = 'application/vnd.api+json; ext="bulk"'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return super(JsonApiBulkRenderer, self).render(data,
                                                       accepted_media_type=accepted_media_type,
                                                       renderer_context=renderer_context)
