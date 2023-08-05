# -*- coding: utf-8 -*-
"""Serve the favicon.ico at the application root."""

from pyramid.response import FileResponse
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

import os


@view_config(
    route_name='favicon',
    permission=NO_PERMISSION_REQUIRED,
)
def favicon(request):
	
	here = os.path.dirname(__file__)
	
	settings = request.registry.settings
	favicon_path = settings.get('favicon_path', None)
	if favicon_path:
		icon = os.path.join(favicon_path, 'favicon.ico')
	else:
		icon = os.path.join(here, '../', 'static', 'dist', 'favicon.ico')
	
	return FileResponse(icon, request=request)
