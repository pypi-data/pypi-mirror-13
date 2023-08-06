# -*- coding: utf-8 -*-

import pyglins


pyglins.scan_for_plugins('test/plugins')
for plugin in pyglins.BasePlugin.plugins:
    loaded_plugin = plugin()
    print('Starting {}'.format(loaded_plugin.name))
    loaded_plugin.run()
