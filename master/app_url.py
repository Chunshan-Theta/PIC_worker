import os

import tornado.web
from tornado_swagger.setup import setup_swagger
from handler.api.query.commonToolHandler import GetArchives,dotsHandler
api_base_url = os.getenv("nginx_proxy_path", "/")
proxy_type = os.getenv("proxy_type", "http")


class Application(tornado.web.Application):
    _routes = [
        # tornado.web.url(r"/receive_img", GetArchives),
        tornado.web.url(r"/dots", dotsHandler),
    ]

    def __init__(self, **settings):
        setup_swagger(
            self._routes,
            swagger_url="/docs",
            api_base_url=api_base_url,
            description="",
            api_version="1.0.0",
            title="NLU API",
            contact="name@domain",
            schemes=[proxy_type],
            security_definitions={
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
            },
        )
        super(Application, self).__init__(self._routes, **settings)


# tornado_opentracing.init_tracing()
app = Application()
