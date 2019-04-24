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
async def test_documentation():
    assert Range.h.__doc__ == "Documentation"
