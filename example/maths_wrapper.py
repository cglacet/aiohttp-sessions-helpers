from asynctools import AbstractSessionContainer, attach_session

MATH_API_URL = "http://api.mathjs.org/v4"


class MathRequests(AbstractSessionContainer):

    @attach_session  # 3.
    async def get_text(self, url, params, session=None):
        async with session.get(url, params=params) as response:
            return await response.text()

    async def get_square(self, value):
        params = {
            "expr" : f"{value}^2"
        }
        return await self.get_text(MATH_API_URL, params=params)


class AnotherMathRequests(AbstractSessionContainer):

    async def get_square(self, value):
        params = {
            "expr" : f"{value}^2"
        }
        async with self.get(MATH_API_URL, params=params) as response:
            return await response.text()


async def main():
    values = list(range(5))

    async with MathRequests() as maths:
        squares = await asyncio.gather(*(maths.get_square(v) for v in values))
        print(f"Squares of {values} = {squares}")

    async with AnotherMathRequests() as maths:
        squares = await asyncio.gather(*(maths.simpler_get_square(v) for v in values))
        print(f"Squares of {values} = {squares}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())