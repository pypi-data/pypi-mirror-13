# __init__.py


def importme(config):
    config.add_route('favicon', '/favicon.ico')
    config.scan()