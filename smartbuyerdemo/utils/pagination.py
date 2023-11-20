from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    page_size = 10  # per page record
    page_size_query_param = "pagesize"
    page_query_param = "page"
