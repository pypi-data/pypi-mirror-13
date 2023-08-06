import sys

from pluggy import HookimplMarker, HookspecMarker
from .plugin_management import SslackPluginManager


PROJECT_NAME = 'sslack'


hookimpl = HookimplMarker(PROJECT_NAME)
hookspec = HookspecMarker(PROJECT_NAME)


@hookspec
def sslack_add_hookspec(plugin_manager):
    pass


class SslackConfig:
    project_name = PROJECT_NAME
    entry_point_name = '%s42' % PROJECT_NAME
    plugin_manager = SslackPluginManager

    def __init__(self):
        self.plugin_manager = SslackPluginManager(self)
        self.plugin_manager.add_hookspecs(sys.modules[__name__])
        self.plugin_manager.register_reachable_plugins()

    @property
    def hook(self):
        return self.plugin_manager.hook
