""" The **drf_ember** JSON API parser."""
from rest_framework import parsers
from .utils import api as api_utils
from .exceptions import JsonApiException


class JsonApiParser(parsers.JSONParser):
    """
    The parser handles the transformation of data sent through POST and PATCH requests.
    These requests typically communicate information about resources. The transmitted
    data must be transformed into the built-in types expected by the Django Rest Framework.

    POST and PATCH requests may represent a single resource or, given the ``bulk`` extension
    to the JSON API, they might have a list of resources.

    The parsed result becomes the `data` property in a request, commonly accessed through
    `request.data` in DRF views.
    """

    media_type = 'application/vnd.api+json'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses a JSON API bytestream.

        Raises:
            JsonApiException

        Returns:
            dict: A dictionary with parsed data
        """
        json_result = super(JsonApiParser, self).parse(
            stream, media_type=media_type, parser_context=parser_context)
        primary_data = json_result.get('data', None)
        if primary_data:
            # check if list
            if isinstance(primary_data, list):
                return api_utils.parse_bulk_resource_objects(primary_data, parser_context)
            elif isinstance(primary_data, dict):
                return api_utils.parse_resource_object(primary_data, parser_context)
            else:
                raise JsonApiException("Document 'data' element invalid")
        else:
            raise JsonApiException("Document did not contain primary, top-level 'data' element")
