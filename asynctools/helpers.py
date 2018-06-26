import asyncio, functools, aiohttp
from abc import ABCMeta, abstractmethod

def attach_session(session_object_name=None):
    if session_object_name is None:
        session_object_name = 'session'
    def decorator(method):
        @functools.wraps(method)
        async def method_with_session(self, *args, **kwargs):
            if self._session is None:
                async with aiohttp.ClientSession() as session:
                    #print("{} using a one shot session.".format(method.__name__))
                    kwargs[session_object_name] = session
                    return await method(self, *args, **kwargs)
            else:
                #print("{} using the long lasting session {}.".format(method.__name__, self.session))
                kwargs[session_object_name] = self._session
                return await method(self, *args, **kwargs)
        return method_with_session
    return decorator

class AbstractSessionContainer(metaclass=ABCMeta):
    @abstractmethod
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