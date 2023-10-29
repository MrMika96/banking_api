from collections import OrderedDict
from typing import Union

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from banking_api.settings import MAX_PAGE_SIZE, PAGE_SIZE_QUERY_PARAM, PAGE_QUERY_PARAM


class DynamicPageNumberPagination(PageNumberPagination):
    """A subclass of PageNumberPagination.
    Adds support for pagination metadata and overrides for
    pagination query parameters.
    """
    page_size_query_param = PAGE_SIZE_QUERY_PARAM
    page_query_param = PAGE_QUERY_PARAM
    max_page_size = MAX_PAGE_SIZE
    page_size = None

    def get_page_metadata(self):
        """
        For customized metadata.
        Override this if you need other fields in pagination
        """
        return {
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page': self.page.number,
            'per_page': self.get_page_size(self.request)
        }

    def get_paginated_data(self, data: Union[ReturnDict, ReturnList]) -> OrderedDict:
        meta = self.get_page_metadata()
        if isinstance(data, list):
            data = OrderedDict([
                ('count', self.page.paginator.count),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('results', data),
                ('meta', meta)
            ])
        else:
            if 'meta' in data:
                data['meta'].update(meta)
            else:
                data['meta'] = meta
        return data

    def get_paginated_response(self, data: Union[ReturnDict, ReturnList]) -> Response:
        return Response(self.get_paginated_data(data))
