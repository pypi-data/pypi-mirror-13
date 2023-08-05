# -*- coding: utf-8 -*-
"""Serve the favicon.ico at the application root."""

from pyramid.path import AssetResolver
from pyramid.response import FileResponse
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

import os


@view_config(
    route_name='favicon',
    permission=NO_PERMISSION_REQUIRED,
)
def favicon(request):
    
    settings = request.registry.settings
    favicon_path = settings.get('favicon_path', None)    

    a = AssetResolver()
    if favicon_path:
        #only if an absolute path was given; otherwise, we'll accept
        #package path+'favicon.ico', e.g., 'myproject:static/favicon.ico'
        if os.path.isabs(favicon_path):
            favicon_path = os.path.join(favicon_path, 'favicon.ico')
        resolver = a.resolve(favicon_path)        
    else:
        resolver = a.resolve('favicon.ico')
    
    icon_path = resolver.abspath()
    
    return FileResponse(icon_path   , request=request)
