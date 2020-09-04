from .base import BaseProvider


class BaseCustomOnlyProvider(BaseProvider):

    def get_queryset(self):
        iobjs = super().get_queryset()
        return iobjs.filter(
            ident__startswith='custom')
