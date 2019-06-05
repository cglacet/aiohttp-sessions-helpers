import asynctools  # 1.

MATH_API_URL = "http://api.mathjs.org/v4"

class MathRequests(asynctools.AbstractSessionContainer):  # 2.

    @asynctools.attach_session  # 3.
    async def get_text(self, url, params, session=None):
        async with session.get(url, params=params) as response:
            return await response.text()

    async def get_square(self, value):
        params = {
            "expr" : f"{value}^2"
        }
        return await self.get_text(MATH_API_URL, params=params)
