import asyncio, functools, aiohttp
from abc import ABCMeta, abstractmethod

def attach_session(method):
    @functools.wraps(method)
    async def method_with_session(self, *args, **kwargs):
        if self.session is None:
            async with aiohttp.ClientSession() as session:
                #print("{} using a one shot session.".format(method.__name__))
                return await method(self, *args, session=session, **kwargs)
        else:
            #print("{} using the long lasting session {}.".format(method.__name__, self.session))
            return await method(self, *args, session=self.session, **kwargs)
    return method_with_session

class AbstractSessionContainer(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        self.session = None
        self.args = args
        self.kwargs = kwargs
    async def __aenter__(self):
        self.session = await aiohttp.ClientSession(*self.args, **self.kwargs).__aenter__()
        return self
    async def __aexit__(self, *args, **kwargs):
        await self.session.__aexit__(*args, **kwargs)
    async def start_session(self, *args, **kwargs):
        self.session = aiohttp.ClientSession(*args, **kwargs)
    async def close_session(self, *args, **kwargs):
        if (self.session is not None) and (not self.session.closed):
            await self.session.close()
        self.session = None
