[![Travis status](https://travis-ci.com/cglacet/aiohttp-sessions-helpers.svg?branch=master)](https://travis-ci.com/cglacet/aiohttp-sessions-helpers)

# Automatically add session management to a class
Some function and classes to help you deal with aiohttp client sessions. This is made after this [discussion](https://github.com/aio-libs/aiohttp/pull/1468). This works for decorating both coroutines and asynchronous generators methods.

## Installation

```bash
pip install aiohttp-asynctools
```

## Usage

Automatically attach an `aiohttp.ClientSession` object to your class in a fast and clean way with the following 3 steps:

1. Import `asynctools`
2. Make your class extend `asynctools.AbstractSessionContainer`
3. Decorate asynchronous methods/generators with `@asynctools.attach_session` to attach a `session` argument.

Optionaly, you can also cutomize the instanciation of `AbstractSessionContainer` in your `__init__` method.
Here is what it looks like for a simple example using a [math API](http://api.mathjs.org/v4):

```python
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
```

You are now ready to instantiate a `MathRequests` context manager and start requesting the math service using a single `aiohttp` `session` (the session is hidden from the `MathRequests` user). Here is how you could build a math server using the new class (basically we wrote a wrapper for the Math API and now we expose our own API).

```python
from aiohttp import web
routes = web.RouteTableDef()

@routes.get('/squares')
async def squares(request):
    values = request.query['values'].split(',')

    async with MathRequests() as maths:
        squares = await asyncio.gather(*(maths.get_square(v) for v in values))

    return {
        'values': values,
        'squares': squares,
    }

maths_app = web.Application()
maths_app.add_routes(routes)

if __name__ == "__main__":
    web.run_app(app)
```

We are now ready to test:
```bash
curl 'http://localhost:8080/squares?values=1,2,3,4,5,6,7,8,9,10'
```

Which should output:
```json
{
  "values": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
  "results": ["1", "4", "9", "16", "25", "36", "49", "64", "81", "100"]
}
```

A more complete example can be found in [example](example).

## Details and explanation

### What?

The goal is to help aiohttp users to build classes that will contain sessions object in an efficient/clean way.

### Why?

If you want to build class that will make requests using **aiohttp client**, at some point you'll have to deal with sessions.
The [quickstart guide for aiohttp client](https://aiohttp.readthedocs.io/en/stable/client_quickstart.html#make-a-request) has an important note about them.

>```python
>import aiohttp
>
>async with aiohttp.ClientSession() as session:
>    async with session.get('http://httpbin.org/get') as resp:
>        print(resp.status)
>        print(await resp.text())
>```
>
> ...
>
> ### Note
> Don’t create a session per request. Most likely you need a session per application which performs all requests altogether.
>
> More complex cases may require a session per site, e.g. one for Github and other one for Facebook APIs. Anyway making a session for every request is a **very bad** idea.
>
>A session contains a connection pool inside. Connection reusage and keep-alives (both are on by default) may speed up total performance.

The goal is to have a single session attached to a given object, this is what this module offers with only 3 (very simple) lines of code.

### How?

The module provides an abstract class `AbstractSessionContainer` and a method decorator `attach_session` that you'll have to use to automatically add session management to an existing class.

Say you have a class `MathRequests` that has a single method `get_square` that returns the square value of the given parameter using an `aiohttp.get` request to the math API service located at http://api.mathjs.org/v4. Here is what your class look like for now:

```python
import asyncio, aiohttp
routes = aiohttp.web.RouteTableDef()

class MathRequests:
    async def get_text(self, url, params):
        # Remember "making a session for every request is a very bad idea"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.text()
    async def get_square(self, value):
        return await self.get_text("http://api.mathjs.org/v4", params={'expr' : '{}^2'.format(value)})

@routes.get('/squares')
async def index(request):
    tasks = []
    data = request.query
    values = data['values'].split(',')
    maths = MathRequests()
    results = await asyncio.gather(*[ maths.get_square(v) for v in values ])
    return web.json_response({ 'values':values, 'results':results })

maths_app = aiohttp.web.Application()
maths_app.add_routes(routes)
```
As `aiohttp` documentation says, this is a bad idea to implement `MathRequests` this way, we need to share a single session for all `get_square` requests.

A simple solution to this would be to store a client session object within `MathRequests`, which you could initiate in the `__init__` method. Saddly this is not a very clean solution as aiohttp sessions should be instantiated in a synchronous way (outside the even loop). See [aiohttp#1468](https://github.com/aio-libs/aiohttp/pull/1468) for more information about _creation a session outside of coroutine_.

Here is the final solution using the provided module `asynctools`:
```python
import asyncio
import asynctools # 1) Import

# 2) Extends the abstract class that will handle the aiohttp session for you:
class MathRequests(asynctools.AbstractSessionContainer):
    def __init__(self):
        # 2') (optional) initilise with any 'aiohttp.ClientSession' argument
        super().__init__(raise_for_status=True)
    # 3) This decorator will automatically fill the session argument:
    @asynctools.attach_session
    async def get_text(self, url, params, session=None):  # 4) Add the 'session' argument
        async with session.get(url, params=params) as response:
            return await response.text()
    async def get_square(self, value):
        return await self.get_text("http://api.mathjs.org/v4", params={'expr' : '{}^2'.format(value)})

from aiohttp import web
routes = web.RouteTableDef()

@routes.get('/squares')
async def index(request):
    tasks = []
    data = request.query
    values = data['values'].split(',')
    async with MathRequests() as maths: # Use the object as a context manager (async with <context_manager> as <name>)
        results = await asyncio.gather(*[ maths.get_square(v) for v in values ])
    return web.json_response({ 'values':values, 'results':results })

maths_app = web.Application()
maths_app.add_routes(routes)
```

Using the `MathRequests` as a [context manager](https://docs.python.org/3/library/stdtypes.html#typecontextmanager) is the best option (as it will make sure the session is correctly started and closed), but it's not the only option, you can also keep your code as it was before:
```python
@routes.get('/squares')
async def index(request):
    tasks = []
    data = request.query
    values = data['values'].split(',')
    maths = MathRequests()
    results = await asyncio.gather(*[ maths.get_square(v) for v in values ])
    return web.json_response({ 'values':values, 'results':results })
```
In this case, no session is attached to the `maths` object and every call to `get_square` will use a different session (which is as bad as it was with the old version of `MathRequests`). What you can do to avoid that is to **explicitly open a "math session"** which will make all `get_square` calls to use the same session (also, don't forget to close the session when you are done):
```python
@routes.get('/maths')
async def index(request):
    tasks = []
    data = request.query
    values = data['values'].split(',')
    maths = MathRequests()
    maths.start_session()
    results = await asyncio.gather(*[ maths.get_square(v) for v in values ])
    maths.close_session()
    return web.json_response({ 'values':values, 'results':results })
```
