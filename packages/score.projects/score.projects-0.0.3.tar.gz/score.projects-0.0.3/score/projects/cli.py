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

import click
import score.cli.conf
from score.init import parse_config_file, init as score_init
import sys
import textwrap
import os


@click.group()
@click.pass_context
def main(clickctx):
    conf = parse_config_file(score.cli.conf.globalconf())
    if 'projects' not in conf:
        default = '~/Projects'
        if sys.platform in ('linux', 'freebsd'):
            default = '~/projects'
        target = click.prompt(
            textwrap.dedent('''
                Welcome to The SCORE Framework!
                Where would you like to keep your projects?
                [default: %s]
            ''' % default).strip(),
            prompt_suffix=' ',
            default=default,
            show_default=False,
            type=click.Path(file_okay=True, dir_okay=False))
        open(score.cli.conf.globalconf(), 'a').write(textwrap.dedent('''
            [projects]
            root = %s
        ''' % os.path.expanduser(target)).rstrip())
        conf['projects'] = {'root': target}
    if 'score.init' not in conf:
        conf['score.init'] = {}
    conf['score.init']['modules'] = 'score.projects'
    clickctx.obj['projects'] = score_init(conf).projects
    return


@main.command()
@click.argument('name')
@click.pass_context
def create(clickctx, name):
    clickctx.obj['projects'].create(name).spawn_shell()


@main.command()
@click.pass_context
def list(clickctx):
    for project in clickctx.obj['projects']:
        print(project.name)


@main.command()
@click.argument('name')
@click.pass_context
def load(clickctx, name):
    clickctx.obj['projects'][name].spawn_shell()


if __name__ == '__main__':
    main()
