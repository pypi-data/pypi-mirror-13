"""
Pagination class for page number-based data set organization.
"""
from collections import OrderedDict
from rest_framework import pagination
from rest_framework.views import Response

class PageNumberPagination(pagination.PageNumberPagination):
    """
    DRF Pagination that supports JSON API specificaiton

    Attributes:
        page_query_param (string): Set to 'page'.
        page_size_query_param (string): Set to 'page-size'.
    """
    page_query_param = 'page'
    page_size_query_param = 'page-size'

    def get_paginated_response(self, data):
        """
        Prepares response data with a ``meta`` object configured to meet
        Gol Web application format expectations. Specifically a dictionary
        with the following key-value pairings:

        - A ``count`` of models from the query set.
        - The current ``page``.
        - The ``next`` page. Can be None if there isn't one.
        - The ``previous`` page. None if there isn't one.
        - The total number of ``pages``, convenient for forwarding to
          the last page.
        - The ``range`` of pages, which is a list (i.e. array) of all the
          possible pages.

        Returns:
            Response object: Returns a Django REST Framework Views Response.
            The response is instantiated with a ``results`` key paired
            with the query set model data, as well as a ``meta`` key
            paired with an *OrderedDict* with the attributes outlined above.
        """
        next_page = None
        previous_page = None
        if self.page.has_next():
            next_page = self.page.next_page_number()
        if self.page.has_previous():
            previous_page = self.page.previous_page_number()
        return Response({
            'results': data,
            'meta': OrderedDict([
                ('count', self.page.paginator.count),
                ('page', self.page.number),
                ('next', next_page),
                ('previous', previous_page),
                ('pages', self.page.paginator.num_pages),
                ('range', self.page.paginator.page_range)
            ])
        })