# A toy example using both aiohttp client/server

The [API wrapper][API wrapper] make use of the asynctools helpers,
the [server][server] simply serve a web interface for the wrapper.
The server will render a [jinja2 template][squqare template] showing a table of squares.

[API wrapper]: maths_wrapper.py
[server]: maths_server.py
[squqare template]: templates/squares.jinja2
