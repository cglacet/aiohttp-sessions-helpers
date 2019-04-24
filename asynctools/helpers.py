import asyncio, functools, aiohttp
from abc import ABCMeta, abstractmethod
import types


def attach_named_session(session_object_name=None):
    if session_object_name is None:
        session_object_name = 'session'

    def decorator(method):

        @functools.wraps(method)
        def decorated(self, *args, **kwargs):
            kwargs[session_object_name] = self._session
            method_instance = method(self, *args, **kwargs)
            if isinstance(method_instance, types.AsyncGeneratorType):

                async def inner():
                    async for value in method_instance:
                        yield value
            else:

                async def inner():
                    return await method_instance

            return inner()

        return decorated

    return decorator

attach_session = attach_named_session()

class AbstractSessionContainer(metaclass=ABCMeta):
    #@abstractmethod
    def __init__(self, *args, **kwargs):
        self._session = None
        self._args = args
        self._kwargs = kwargs
    async def __aenter__(self):
        self._session = await aiohttp.ClientSession(*self._args, **self._kwargs).__aenter__()
        return self
    async def __aexit__(self, *args, **kwargs):
        await self._session.__aexit__(*args, **kwargs)
    async def start_session(self, *args, **kwargs):
        self._session = aiohttp.ClientSession(*args, **kwargs)
    async def close_session(self, *args, **kwargs):
        if (self._session is not None) and (not self._session.closed):
            await self._session.close()
        self._session = None