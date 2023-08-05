from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response, FileResponse
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

import logging
import os

def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)

@view_config(
    route_name='favicon',
    permission=NO_PERMISSION_REQUIRED,
)
def favicon(request):
    log= logging.getLogger( "Arf arf" )
    log.debug("HERE IN FAVICON()!!")
    here = os.path.dirname(__file__)
    
    settings = request.registry.settings
    favicon_path = settings.get('favicon_path', None)
    if favicon_path:
        icon = os.path.join(favicon_path, 'favicon.ico')
    else:
        #icon = os.path.join(here, '../', 'static', 'dist', 'favicon.ico')
        icon = os.path.join(here, 'favicon.ico')
    
    return FileResponse(icon, request=request)

if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/hello/{name}')
    config.add_view(hello_world, route_name='hello')
    config.add_route('favicon', '/favicon.ico')
    config.add_view(favicon, route_name='favicon')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
