"""
Don't forget to install ``pytest-asyncio`` before running this test::

    pip install pytest pytest-asyncio
    pytest

"""
import asynctools.helpers as helpers
import asyncio
import pytest
import types
import aiohttp


class Range(helpers.AbstractSessionContainer):
    def __init__(self):
        super().__init__(raise_for_status=True)

    @helpers.attach_session
    async def f(self, x, session=None):
        for i in range(x):
            await asyncio.sleep(0.2)
            yield i

    @helpers.attach_session
    async def g(self, x, session=None):
        await asyncio.sleep(1)
        return list(range(x))

    @helpers.attach_session
    async def h(self, session=None):
        """Documentation"""
        return session

    @helpers.attach_session
    async def kwargsf(self, session=None, **kwargs):
        """Documentation"""
        return session, kwargs

    @helpers.attach_named_session("definitely_not_a_session")
    async def named_seesion(self, definitely_not_a_session=None):
        """Documentation"""
        return definitely_not_a_session


@pytest.mark.asyncio
async def test_generator():
    x = 4
    expected = list(range(x))
    async with Range() as async_range:
        async_range_generator = async_range.f(x)
        assert isinstance(async_range_generator, types.AsyncGeneratorType)
        generator_output = [a async for a in async_range_generator]
        assert generator_output == expected


@pytest.mark.asyncio
async def test_coroutine():
    x = 4
    expected = list(range(x))
    async with Range() as async_range:
        async_range_generator = async_range.g(x)
        assert isinstance(async_range_generator, types.CoroutineType)
        generator_output = [a for a in await async_range_generator]
        assert generator_output == expected

@pytest.mark.asyncio
async def test_session_attached():
    async with Range() as async_range:
        session = await async_range.h()
    assert isinstance(session, aiohttp.ClientSession)


@pytest.mark.asyncio
async def test_kwargs():
    kwargs = dict(a=1, b=2, c=3)
    async with Range() as async_range:
        session, res_kwargs = await async_range.kwargsf(**kwargs)
    assert isinstance(session, aiohttp.ClientSession)
    assert res_kwargs == kwargs


@pytest.mark.asyncio
async def test_named_session_attached():
    async with Range() as async_range:
        session = await async_range.named_seesion()
    assert isinstance(session, aiohttp.ClientSession)


@pytest.mark.asyncio
async def test_session_hook():
    async def test_hook(session):
        session.test = lambda x: x+1
        return session

    async_range = Range()
    async_range.set_session_hook(test_hook)

    async with async_range:
        session = await async_range.named_seesion()
    assert isinstance(session, aiohttp.ClientSession)
    assert session.test(3) == 4

@pytest.mark.asyncio
async def test_session_hook_class():
    class RangeB(helpers.AbstractSessionContainer):
        async def session_hook(self, session):
            session.test = lambda x: x+1
            return session

        @helpers.attach_session
        async def f(self, session=None):
            return session

    async with RangeB() as async_range:
        session = await async_range.f()

    assert isinstance(session, aiohttp.ClientSession)
    assert session.test(3) == 4


# @pytest.mark.asyncio
# async def test_hooks():
#     on_start_test_value = None
#     on_close_test_value = None
#     expected_value = "hooked"

#     async def start_hook(*args, **kwargs):
#         nonlocal on_start_test_value
#         on_start_test_value = expected_value

#     async def close_hook(*args, **kwargs):
#         nonlocal on_close_test_value
#         on_close_test_value = expected_value

#     async_range = Range()
#     async_range.on_start(start_hook)
#     async_range.on_close(close_hook)

#     assert on_start_test_value == None
#     assert on_close_test_value == None
#     async with async_range:
#         session = await async_range.named_seesion()
#         assert on_start_test_value == expected_value
#         assert on_close_test_value == None

#     assert on_start_test_value == expected_value
#     assert on_close_test_value == expected_value
#     assert isinstance(session, aiohttp.ClientSession)


@pytest.mark.asyncio
async def test_documentation():
    assert Range.h.__doc__ == "Documentation"
