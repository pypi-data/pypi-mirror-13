# -*- coding: utf-8 -*-

__version__ = '0.1.1.dev1'
__description__ = 'Minimal plugin system for Python apps'

import importlib
import sys
import pathlib


class MetaPlugin(type):
    """
    Metaclass for the plugins Class
    """
    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            cls.plugins = []
        else:
            cls.plugins.append(cls)


class BasePlugin(metaclass=MetaPlugin):
    """
    Base class for plugins. Will contain scanned plugins
    """
    def __init__(self):
        self.name = ''

    def run(self):
        pass


def scan_for_plugins(directory: str):
    """
    This method will scan a directory passed as argument
    searching python files that extends BasePlugin
    Plugins detected will be in BasePlugin.plugins
    """
    base_dir = pathlib.Path(directory)
    if base_dir.exists() and base_dir.is_dir():
        sys.path.append(base_dir.as_posix())
        plugs = [p for p in base_dir.iterdir() if p.is_dir()]
        for plug in plugs:
            importlib.import_module(plug.name)
    else:
        raise ValueError('The argument passed is not a directory')

