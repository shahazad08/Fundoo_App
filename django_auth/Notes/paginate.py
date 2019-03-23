from rest_framework.pagination import (  # Import framework for a limit of a page, and page no.
    LimitOffsetPagination,
    PageNumberPagination,
)


class PostLimitOffsetPagination(LimitOffsetPagination):  # Default Limit
    default_limit = 5
    max_limit = 11


class PostPageNumberPagination(PageNumberPagination):  # No. of contents that is to be display in a page_size
    page_size = 20
