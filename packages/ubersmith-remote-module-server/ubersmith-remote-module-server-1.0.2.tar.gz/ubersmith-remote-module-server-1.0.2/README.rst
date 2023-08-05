.. image:: https://travis-ci.org/internap/python-ubersmith-remote-module-server.svg?branch=master
    :target: https://travis-ci.org/internap/python-ubersmith-remote-module-server

ubersmith-remote-module-server
==============================

Standardizing on the proposed ubersmith webhook format (method, params, env and callback),
this aims to be an easy way to serve any python object as a Übersmith remote module.


Mission
=======

Offer an easy way to write device, order and service modules, in python, with as few lines of code as possible.


Vision
======

A remote "hello world" device module should fit under 20 lines.


Values
======

* Everything should be tested and easy to understand.


Example
=======

>>> from ubersmith_remote_module_server import server
>>> class MyDeviceModule(object):
...   def hello(self, env):
...     return "world"
...
>>> s = server.Server({'my_device_module': MyDeviceModule()})
>>> s.run()
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

