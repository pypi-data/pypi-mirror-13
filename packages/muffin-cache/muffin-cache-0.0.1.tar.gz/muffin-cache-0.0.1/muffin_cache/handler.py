import asyncio
import pickle

from muffin.handler import Handler, Response
from muffin.utils import abcoroutine


class CacheHandler(Handler):

    CACHED_HTTP_METHODS = ('GET', 'OPTIONS')

    def _build_cache_key(self, request):
        sorted_query_string = '-'.join(
            sorted(request.query_string.split('&'))
        )

        return 'muffin-cache-{method}-{path}-{query}'.format(
            method=request.method,
            path=request.raw_path,
            query=sorted_query_string
        )

    @asyncio.coroutine
    def _get_from_cache(self, request):
        cached_response = (
            yield from self.app.ps.redis.get(
                self._build_cache_key(request)
            )
        )
        if cached_response:
            raw_response = pickle.loads(cached_response)
            response = Response(
                status=raw_response['status'],
                body=raw_response['body'],
                content_type=raw_response['content_type']
            )
            response.charset = self.app.cfg.ENCODING
            return response

    @asyncio.coroutine
    def _set_to_cache(self, request, response):
        cached_value = {
            'status': response.status,
            'body': response.body,
            'content_type': response.content_type or 'text/html'
        }
        yield from self.app.ps.redis.set(
            self._build_cache_key(request),
            pickle.dumps(cached_value),
            self.app.ps.cache.cfg.lifetime
        )

    @abcoroutine
    def dispatch(self, request, view=None, **kwargs):
        if request.method not in self.CACHED_HTTP_METHODS:
            return (yield from super().dispatch(request, view, **kwargs))
        cached_result = (
            yield from self._get_from_cache(request)
        )
        if not cached_result:
            cached_result = (
                yield from super().dispatch(request, view, **kwargs)
            )
            yield from self._set_to_cache(request, cached_result)

        return cached_result
