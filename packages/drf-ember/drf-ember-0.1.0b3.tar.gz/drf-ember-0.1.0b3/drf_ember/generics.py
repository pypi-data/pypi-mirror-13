"""

Module Overview
---------------

Generic **views** the extend the Django REST Framework's generics to
easily integrate with Ember Data and the JSON API.

Let's discuss the some of the important design choices in this module.

JsonApiView
^^^^^^^^^^^

The ``JsonApiView`` derives from DRF's ``GenericAPIView``. It sets
the parser and renderer to **drf-ember's** JSON API versions. This
is for convenience. Otherwise, the user would have to keep setting
the parser and renderer when using the Frameworks's generics.

Additionally, ``JsonApiView`` overrides the ``finalize_response`` method
to include the JSON API's bulk extension's requirement that responses
include an accepted media type that denotes ``supported-ext="bulk"`` to
the client.

DRF CRUD class extensions
^^^^^^^^^^^^^^^^^^^^^^^^^

DRF provides many useful generic view classes that greatly simplify
create-retrieve-update-delete functionality for resources/models persisted in
database/data store.

This module swaps the DRF ``GenericAPIView`` for this module's ``JsonApiView``
in each of the following DRF generic view classes:
``CreateAPIView``, ``ListAPIView``, ``ListCreateAPIView``, ``RetrieveAPIView``,
``DestroyAPIView``, ``UpdateAPI``, ``RetrieveUpdateAPIView``,
``RetrieveDestroyAPIView``, ``RetrieveUpdateDestroyAPIView``.

For DRF generic view classes with update or destroy functionality,
the framework's mixin is replaced with the **drf-ember** mixin. When
updating, the JSON API requires different response formats if the
server performed changes to a resource in addition to client changes.
The **drf-ember** ``UpdateModelMixin`` provides logic to implement said
requirement, as well as a content type that indicates support for the
"bulk" API extension. Similarly, for view classes that destroy (i.e. delete)
resources, **drf-ember's** ``DestroyModelMixin`` replaces the DRF one
in order to include a content type indicating that the JSON API "bulk"
extension is supported.

CollectionWithBulkAPIView
^^^^^^^^^^^^^^^^^^^^^^^^^

The JSON API provides a "bulk" extension that is quite useful for
client applications that want to reduce the overhead of data transmission.

One potentially tricky developer preference would be for a single endpoint,
such as '/api/persons' or '/api/songs' to handle both the single resource
*and* bulk functionality that the DRF ``ListCreateAPI`` view would typically
handles.

The ``CollectionWithBulkAPIView`` is an attempt at satisfying that preference
in a single view class. The view supports JSON API logic for resource
collections. Specifically:

        - GET (retrieve) of a list of resources
        - single and bulk POST (create)
        - bulk PATCH (update)
        - bulk DELETE (destroy)

However, it **does not support PUT** as the JSON API does not currently identify
a use for PUT's approach. The view logic will internally prepare a response with
a 405 "Method 'PUT' not allowed" which the default **drf_ember** exception
handler will convert to a 400 to avoid unwanted granularity/information leakage
about the API.

View Classes
------------

The public API for this module's view classes.
"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, mixins, status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from .parsers import JsonApiParser
from .renderers import JsonApiRenderer, JsonApiBulkRenderer
from .mixins import DestroyModelMixin, ListModelMixin, \
    RetrieveModelMixin, UpdateModelMixin


class JsonApiView(generics.GenericAPIView):
    """
    Sets parser and renderer classes compatible with the Ember.js
    framework's JSON request and response formats by extending
    the Django REST Frameworks's GenericAPIView.

    Sets parser and renderer to **drf-ember's** JSON API versions. This
    is for convenience. Otherwise, the user would have to keep setting
    the parser and renderer when using the Frameworks's generics.

    Additionally, overrides the ``finalize_response`` method
    to include the JSON API's bulk extension's requirement that responses
    include an accepted media type that denotes ``supported-ext="bulk"`` to
    the client.

    Attributes:
        parser_classes (tuple): Default is a tuple that
            includes :py:class:`~drf_ember.parsers.JsonApiParser`
        renderer_classes (tuple): Default is a tuple that
            includes :py:class:`~drf_ember.renderers.JsonApiRenderer`
    """
    parser_classes = (JsonApiParser,)
    renderer_classes = (JsonApiRenderer,)

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Overrides ``GenericAPIView`` method to denote support for JSON bulk
        extension by including ``suppurted-ext="bulk"`` in response.

        Returns:
            Response: A DRF response object
        """
        response = super(JsonApiView, self).finalize_response(request, response, *args, **kwargs)
        with_supported_extensions = '{0}; supported-ext="bulk"'.format(response.accepted_media_type)
        response.accepted_media_type = with_supported_extensions
        return response


class CreateAPIView(mixins.CreateModelMixin,
                    JsonApiView):
    """
    Concrete view for creating a model instance.
    """
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(ListModelMixin,
                  JsonApiView):
    """
    Concrete view for listing a queryset.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(RetrieveModelMixin,
                      JsonApiView):
    """
    Concrete view for retrieving a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(DestroyModelMixin,
                     JsonApiView):

    """
    Concrete view for deleting a model instance.
    """
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(UpdateModelMixin,
                    JsonApiView):

    """
    Concrete view for updating a model instance.
    """
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(ListModelMixin,
                        mixins.CreateModelMixin,
                        JsonApiView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CollectionWithBulkAPIView(ListModelMixin,
                                mixins.CreateModelMixin,
                                UpdateModelMixin,
                                DestroyModelMixin,
                                JsonApiView):
    """
    This view supports JSON API logic for resource collections. Specifically:

        - GET (retrieve) of a list of resources
        - single and bulk POST (create)
        - bulk PATCH (update)
        - bulk DELETE (destroy)

    It **does not support PUT** and the view logic will internally prepare a response
    with a 405 "Method 'PUT' not allowed" which the default **drf_ember** exception
    handler will convert to a 400 to avoid unwanted granularity/information leakage
    about the API.
    """
    renderer_classes = (JsonApiRenderer, JsonApiBulkRenderer)

    def get(self, request, *args, **kwargs):
        """
        Lists a queryset for the view.
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Creates an object or a list of objects.

        A single object is created unless a list of objects
        is passed.

        Returns:
            Response: Includes data, headers and cotent type that indicates
                whether or not the bulk extension was utilized.
        """
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            serializer = self.get_serializer(data=request.data, many=True)
            content_type = 'application/vnd.api+json; ext="bulk"; supported-ext="bulk"'
        else:
            serializer = self.get_serializer(data=request.data)
            content_type = 'application/vnd.api+json; supported-ext="bulk"'
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers,
                        content_type=content_type)

    def patch(self, request, *args, **kwargs):
        """
        Updates a list of objects.

        Raises:
            ParseError: ``ParseError`` raised if request's data property is not a list.

        Returns:
            Response: Includes data, headers and cotent type that indicates
                whether or not the bulk extension was utilized.
        """
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(
                queryset,
                data=request.data,
                many=True,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            update = self.perform_update(serializer)
            response_data = update['data'] if update['has_server_update'] else None
            content_type = 'application/vnd.api+json; ext="bulk"; supported-ext="bulk"'
            return Response(response_data, status=status.HTTP_200_OK, content_type=content_type)
        else:
            raise ParseError

    def delete(self, request, *args, **kwargs):
        """
        Deletes a list of objects.

        Raises:
            ParseError: ``ParseError`` raised if request's data property is not a list.

        Returns:
            Response: Includes data, headers and cotent type that indicates
                whether or not the bulk extension was utilized.
        """
        is_bulk = isinstance(request.data, list)
        if is_bulk:
            queryset = self.filter_queryset(self.get_queryset())
            primary_key_field = getattr(self.serializer_class.Meta, 'bulk_lookup_field', 'id')
            destroyable = list()
            for candidate_object in request.data:
                try:
                    identifier_query = {self.lookup_field: candidate_object[primary_key_field]}
                    instance = queryset.get(**identifier_query)
                    destroyable.append(instance)
                except ObjectDoesNotExist:
                    # Since user intent is deletion, a 204 response reflects actual server state
                    # If you disagree with this judgement call, remove pass and
                    # raise exception here
                    pass
            for instance in destroyable:
                self.perform_destroy(instance)
            content_type = 'application/vnd.api+json; ext="bulk"; supported-ext="bulk"'
            return Response(data=None, status=status.HTTP_204_NO_CONTENT, content_type=content_type)
        else:
            raise ParseError


class RetrieveUpdateAPIView(RetrieveModelMixin,
                            UpdateModelMixin,
                            JsonApiView):
    """
    Concrete view for retrieving, updating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(RetrieveModelMixin,
                             DestroyModelMixin,
                             JsonApiView):
    """
    Concrete view for retrieving or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(RetrieveModelMixin,
                                   UpdateModelMixin,
                                   DestroyModelMixin,
                                   JsonApiView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
