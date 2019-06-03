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
    def __init__(self, *args, **kwargs):
        self._session = None
        self._args = args
        self._kwargs = kwargs

    async def __aenter__(self):
        self._session = await aiohttp.ClientSession(*self._args, **self._kwargs).__aenter__()
        self._session = await self.session_hook(self._session)
        await self.started(*self._args, **self._kwargs)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._session.__aexit__(*args, **kwargs)
        return await self.closed(*args, **kwargs)

    async def start_session(self, *args, **kwargs):
        self._session = aiohttp.ClientSession(*args, **kwargs)
        self._session = await self.session_hook(self._session)
        return await self.started(*args, **kwargs)

    async def close_session(self, *args, **kwargs):
        if (self._session is not None) and (not self._session.closed):
            await self._session.close()
        self._session = None
        return await self.closed(*args, **kwargs)

    # Hooks, test:
    async def session_hook(self, session):
        """Same as ``set_session_hook``, use it if you inherit the ``AbstractSessionContainer``, for example::
            class RangeB(helpers.AbstractSessionContainer):
                async def session_hook(self, session):
                    session.test = lambda x: x+1
                    return session

                @helpers.attach_session
                async def f(self, session=None):
                    return session

            async with RangeB() as async_range:
                session = await async_range.f()
                assert session.test(3) == 4
        """
        return session

    def set_session_hook(self, hook):
        """You can register a session hook to modify the sesssion object on the fly.
        This can be usefull if you need to modify the default class used for sessions (ie, aiohttp.ClientSession).
            async def test_hook(session):
                session.test = lambda x: x+1
                return session

            async_range = Range()
            async_range.set_session_hook(test_hook)

            async with async_range:
                session = await async_range.named_seesion()
        """
        self.session_hook = hook

    async def started(self, *args, **kwargs):
        pass

    def on_start(self, hook):
        self.started = hook

    async def closed(self, *args, **kwargs):
        pass

    def on_close(self, hook):
        self.closed = hook