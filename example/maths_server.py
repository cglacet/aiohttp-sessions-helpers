import asyncio
from aiohttp import web
import aiohttp_jinja2
import jinja2

from maths_wrapper import MathRequests


def define_routes():
    routes = web.RouteTableDef()

    @routes.get('/squares')
    @aiohttp_jinja2.template('squares.jinja2')
    async def squares(request):
        values = request.query['values'].split(',')

        async with MathRequests() as maths:
            squares = await asyncio.gather(*(maths.get_square(v) for v in values))

        return {
            'values': values,
            'squares': squares,
        }

    return routes


def setup_server():
    app = web.Application()

    # Add static file serving:
    app.router.add_static('/static', 'example/static')

    # Add template file serving:
    jinja_loader = jinja2.FileSystemLoader('example/templates')
    aiohttp_jinja2.setup(app, loader=jinja_loader)

    # Allows to use zip in jinja templates
    env = aiohttp_jinja2.get_env(app)
    env.globals.update(zip=zip)

    app.add_routes(define_routes())

    print('Server ready, try it: http://localhost:8080/squares?values=1,2,3,4,5,6')


    return app


app = setup_server()


if __name__ == "__main__":
    web.run_app(app)