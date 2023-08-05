"""
The mixins module is a set of classes that provide action logic
re-used by **drf-ember** generic views.
"""
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response
from .exceptions import JsonApiException

class ListModelMixin(object):
    """
    List a queryset.

    Raises:
        JsonApiException: If ``include`` request parameter present

    Returns:
        Response

    """
    def list(self, request, *args, **kwargs):
        if 'include' in request.query_params:
            raise JsonApiException()
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RetrieveModelMixin(object):
    """
    Retrieve a model instance.

    Raises:
        JsonApiException: If ``include`` request parameter present

    Returns:
        Response
    """
    def retrieve(self, request, *args, **kwargs):
        if 'include' in request.query_params:
            raise JsonApiException()
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DestroyModelMixin(object):
    """
    Destroy a model instance.
    """
    def destroy(self, request, *args, **kwargs):
        """
        Returns:
            Response: Status 204 and a JSON API content type with bulk extension support
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        content_type = 'application/vnd.api+json; supported-ext="bulk"'
        return Response(status=status.HTTP_204_NO_CONTENT, content_type=content_type)

    def perform_destroy(self, instance):
        """
        Hook for aditional delete logic.  By default, just a call to
        delete the passed instance.

        Arguments:
            instance: A Django model.
        """
        instance.delete()


class UpdateModelMixin(object):
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        """
        Handles partial resource update.

        Returns:
            Response: The response object contains status,
                data if there was a server-side update,
                and a JSON API content type with bulk extension support
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        update = self.perform_update(serializer)
        response_data = update['data'] if update['has_server_update'] else None
        content_type = 'application/vnd.api+json; supported-ext="bulk"'
        return Response(data=response_data, status=update['status'], content_type=content_type)

    def perform_update(self, serializer):
        """
        A hook for additional server-side update logic. The base use case
        is for exclusive client-side data updates.  Per the JSON API specification:

            *If a server accepts an update but also changes the resource(s) in ways
            other than those specified by the request (for example, updating the updated-at
            attribute or a computed sha), it MUST return a 200 OK response.
            The response document MUST include a representation of the updated resource(s)
            as if a GET request was made to the request URL.*

            *A server MUST return a 200 OK status code if an update is successful,
            the client's current attributes remain up to date, and the server responds
            only with top-level meta data. In this case the server MUST NOT include
            a representation of the updated resource(s).*

        You can override this hook in views that implement it and return an "update"
        dict with the appropriate data after the server-side changes.

        Arguments:
            serializer: A Django REST Framework ``Serializer``. Remember, it can be
                for an individual resource or a list of resources.

        Returns:
            dict: The key/values of the returned ``dict`` are:

             - ``data``: The current state of the resource(s). Typically,
               represented as Python native datatypes from a serializers
               ``data`` property. By default, the ``data`` attribute
               for the passed serializer is returned; this data consists of
               Python native data types, such as ``datetime.datetime``.

             - ``has_server_update``: A boolean indicating if a
               server-side update was done. ``False`` by default.

             - ``status``: An integer with the HTTP status code the response should provide.
        """
        serializer.save()
        update = {
            'data': serializer.data,
            'has_server_update': False,
            'status': 200
        }
        return update

    def partial_update(self, request, *args, **kwargs):
        """
        Ensures a ``True`` 'partial' kwarg is set before calling ``update`` method.
        """
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)