pyglins
=======

Minimal plugin system for Python apps

Using pyglins
-------------

.. code:: python

    import pyglins

    pyglins.scan_for_plugins('test/plugins')
    for plugin in pyglins.BasePlugin.plugins:
        loaded_plugin = plugin()
        loaded_plugin.run()

Installation
------------

::

    pip install git+https://github.com/paxet/pyglins.git

License
-------

Licensed under `MIT license <LICENSE>`__
