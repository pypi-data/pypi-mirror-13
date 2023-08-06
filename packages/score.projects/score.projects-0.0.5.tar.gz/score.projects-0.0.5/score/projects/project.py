# Copyright © 2015 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

import re
import os
from score.cli.conf import confroot
from vex.main import _main as vex_main


def vex(*args):
    vex_main(os.environ, args)


def copytpl(src, dst, vars):
    if os.path.isdir(src):
        os.makedirs(dst)
        for filetpl in os.listdir(src):
            file = filetpl
            for k, v in vars.items():
                file = file.replace(k, v)
            copytpl(os.path.join(src, filetpl), os.path.join(dst, file), vars)
    else:
        try:
            content = open(src).read()
            for k, v in vars.items():
                content = content.replace(k, v)
            open(dst, 'w').write(content)
        except UnicodeDecodeError:
            # not a text file, just copy content
            open(dst, 'wb').write(open(src, 'rb').read())


class Project:

    def __init__(self, conf, name):
        assert re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name), 'Invalid name'
        self.name = name
        self.conf = conf
        self.root = os.path.join(conf.root, name)
        self.venvdir = os.path.join(confroot(global_=True), 'projects', name)

    def create(self, template='web'):
        # copy scaffold
        assert not self.exists, 'Project already exists'
        scaffold = os.path.join(os.path.dirname(__file__),
                                'scaffold', template, 'files')
        copytpl(scaffold, self.root, {
            '{venv}': self.venvdir,
            '{root}': self.root,
            '{name}': self.name,
            '{ucname}': self.name.capitalize(),
        })
        # create virtualenv
        vex('--path', self.venvdir, '--make', 'true')
        # install the project
        vex('--path', self.venvdir, 'pip', 'install', '--editable', self.root)
        # register configurations
        prodconf = os.path.join(self.root, 'production.conf')
        devconf = os.path.join(self.root, 'development.conf')
        localconf = os.path.join(self.root, 'local.conf')
        vex('--path', self.venvdir, 'score', 'conf', 'add', prodconf)
        vex('--path', self.venvdir, 'score', 'conf', 'add', devconf)
        vex('--path', self.venvdir, 'score', 'conf', 'add', '-d', localconf)

    def create_venv(self):
        import vex.options
        import vex.make
        options = vex.options.get_options(['--path', self.venvdir])
        vex.make.handle_make(os.environ, options, self.venvdir)

    def spawn_shell(self):
        vex('--path', self.venvdir, '--cwd', self.root)

    @property
    def exists(self):
        return os.path.exists(self.root)
