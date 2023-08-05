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
	favicon_folder = settings.get('favicon_folder', None)
	if favicon_folder:
		icon = os.path.join(favicon_folder, 'favicon.ico')
	else:
		icon = os.path.join(here, '../', 'static', 'dist', 'favicon.ico')
	
	return FileResponse(icon, request=request)
