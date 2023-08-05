collective.recipe.maildump
==========================

.. contents::

Introduction
------------

This recipe installs `maildump <https://github.com/ThiefMaster/maildump>`_  a
python-based clone of the awesome `MailCatcher <https://github.com/sj26/mailcatcher>`_
tool.

Installation
------------

Look at this example::

    [buildout]
    parts = maildump

    [maildump]
    recipe = collective.recipe.maildump

That's all.

How to use it
-------------

Just run ``bin/maildumpctl``. By default it will start the web server on port
``1080`` and the smtp server on port ``1025``.

Configure your application to use the SMTP server on localhost, port 25, no
user, and no password.

For example, on django add the following to you ``settings.py`` file::

    EMAIL_HOST = "localhost"
    EMAIL_HOST_USER = ""
    EMAIL_HOST_PASSWORD = ""
    EMAIL_PORT = 1025
    EMAIL_USE_TLS = False
    DEFAULT_FROM_EMAIL='contacto@holokinesislibros.com'
    SERVER_EMAIL = 'contacto@holokinesislibros.com'
