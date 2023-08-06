import argparse
import sys
from sslack import hookimpl


@hookimpl
def sslack_add_hookspec(plugin_manager):
    from . import hookspec
    plugin_manager.add_hookspecs(hookspec)


@hookimpl
def sslack_addoption(parser):
    parser.add_argument(
        '--list_plugins', '-l', action="store_true",
        help='Show the list of plugins already installed and exits.'
    )


@hookimpl
def sslack_on_run(plugin_manager, args):
    if args.list_plugins:
        print(
            "List plugins installed: %s" % ', '.join(
                plugin_name for plugin_name, _ in
                plugin_manager.list_name_plugin())
        )
        sys.exit()


@hookimpl
def sslack_main(config):
    parser = argparse.ArgumentParser()
    config.hook.sslack_addoption(parser=parser)
    args = parser.parse_args()
    config.hook.sslack_on_run(plugin_manager=config.plugin_manager, args=args)
    config.hook.sslack_run(args=args, plugin_manager=config.plugin_manager)
