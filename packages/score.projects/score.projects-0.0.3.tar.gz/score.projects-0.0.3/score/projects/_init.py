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

from score.init import ConfiguredModule
from .project import Project
import os
from score.cli.conf import confroot


defaults = {
}


def init(confdict):
    conf = defaults.copy()
    conf.update(confdict)
    return ConfiguredProjectModule(os.path.expanduser(conf['root']))


class ConfiguredProjectModule(ConfiguredModule):

    def __init__(self, root):
        import score.projects
        super().__init__(score.projects)
        self.root = root

    def get(self, name):
        return Project(self, name)

    def create(self, name):
        project = self.get(name)
        project.create()
        return project

    def all(self):
        venvroot = os.path.join(confroot(global_=True), 'projects')
        try:
            for file in os.listdir(venvroot):
                yield self.get(file)
        except FileNotFoundError:
            pass

    def __iter__(self):
        return self.all()

    __getitem__ = get
