def permanent_main(config_instance):
    config_instance.hook.sslack_add_hookspec(
        plugin_manager=config_instance.plugin_manager
    )
    config_instance.hook.sslack_main(config=config_instance)
