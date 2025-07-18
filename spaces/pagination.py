from rest_framework.pagination import LimitOffsetPagination

class StandardLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5
    max_limit     = 2

class GalleryLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 12
    max_limit = 12