import inspect
from pluggy import PluginManager


class SslackPluginDiscovery:

    def find_core_plugins(self, package_instance=None):
        if package_instance is None:
            from .. import default_plugins as package_instance

        return inspect.getmembers(package_instance, inspect.ismodule)


class SslackPluginManager(PluginManager):
    plugin_discovery = SslackPluginDiscovery

    def __init__(self, config):
        self.plugin_discovery = self.plugin_discovery()
        self.config = config

        super().__init__(self.config.project_name)

    def register_reachable_plugins(self):
        for _, plugin in self.plugin_discovery.find_core_plugins():
            self.register(plugin)

        self.load_setuptools_entrypoints(self.config.entry_point_name)
