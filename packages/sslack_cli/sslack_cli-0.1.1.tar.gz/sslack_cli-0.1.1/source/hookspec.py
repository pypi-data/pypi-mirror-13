from sslack import hookspec


@hookspec
def sslack_addoption(parser):
    pass


@hookspec
def sslack_main(config):
    pass


@hookspec
def sslack_run(plugin_manager, args):
    pass


@hookspec
def sslack_on_run(plugin_manager, args):
    pass
