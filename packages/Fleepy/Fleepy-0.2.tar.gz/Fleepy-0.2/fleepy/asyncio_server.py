import asyncio
import aiohttp

from fleepy._server import BaseHTTPClient


class AioHTTPClient(BaseHTTPClient):
    @asyncio.coroutine
    def request(cls, method, url, data=None,
                headers=None, cookies=None, files=None):
        method = cls.validate_method(method)

        requester = getattr(aiohttp, method)
        response = yield from requester(
            url,
            data=data,
            headers=headers,
            cookies=cookies
        )
