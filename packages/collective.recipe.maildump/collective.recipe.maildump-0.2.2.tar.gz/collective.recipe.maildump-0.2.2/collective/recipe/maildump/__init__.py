# -*- coding: utf-8 -*-
# Copyright (C)2015 Noe Nieto

import logging, os, zc.buildout
import zc.recipe.egg


class Recipe(object):
    """Installs and configures maildump"""

    def __init__(self, buildout, name, options):
        self.name, self.options, self.buildout = name, options, buildout
        self.port = options.get('port', '1025')
        self.ip = options.get('ip', '127.0.0.1')
        self.db_path = options.get('db-path', os.path.join(
            buildout['buildout']['directory'], 'parts', name
        ))

    def install(self):
        """Installer"""
        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.

        dbpath = self.db_path
        if not os.path.exists(dbpath):
            os.makedirs(dbpath)

        installed = self._install_script()
        installed.append(dbpath)
        return installed

    def update(self):
        return self._install_script()

    def _install_script(self):
        installed = []
        ctlscript = zc.recipe.egg.Egg(
            self.buildout,
            self.name,
            {'eggs': 'maildump',
             'scripts': 'maildump=maildumpctl',
             })
        installed += list(ctlscript.install())

        return installed