# __init__.py


def importme(config):
    config.add_route('favicon', '/favicon.ico')

    # settings  = config.registry.settings
    # favicon_folder = settings.get('favicon_folder', None)
    