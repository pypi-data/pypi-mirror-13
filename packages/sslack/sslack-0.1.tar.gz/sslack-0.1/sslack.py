from libslack.core.config import SslackConfig, hookimpl, hookspec
from libslack.core.entry_point import permanent_main


def main_routine():
    config = SslackConfig()
    permanent_main(config)
