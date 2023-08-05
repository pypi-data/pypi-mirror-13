from .handler import CacheHandler


def cache_view(view, **kwargs):
    return CacheHandler.from_view(
        view, kwargs.get('methods', '*'), view.__name__
    )
