# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

import sys
import os                 # NOQA

from ruamel.std.argparse import ProgramBase, option, CountAction, \
    SmartFormatter, sub_parser, version
from ruamel.appconfig import AppConfig
from . import __version__
from .dc2service import DC2Service


def to_stdout(*args):
    sys.stdout.write(' '.join(args))


class DC2ServiceCmd(ProgramBase):
    def __init__(self):
        super(DC2ServiceCmd, self).__init__(
            formatter_class=SmartFormatter,
            aliases=True,
            # usage="""""",
        )

    # you can put these on __init__, but subclassing DC2ServiceCmd
    # will cause that to break
    @option('--verbose', '-v',
            help='increase verbosity level', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @option('--upstart', action='store_true', global_option=True,
            help='generate upstart file (instead of autodetect)')
    @option('--systemd', action='store_true', global_option=True,
            help='generate systemd file (instead of autodetect)')
    @option('--docker-compose', metavar='EXE', global_option=True,
            help='path to dcw/docker-compose %(metavar)s (default %(default)s)')
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        self.dc2s = DC2Service(self._args, self._config)
        if hasattr(self._args, 'func'):
            return self._args.func()
        self._parse_args(['--help'])

    def parse_args(self):
        self._config = AppConfig(
            'ruamel_dc2service',
            filename=AppConfig.check,
            parser=self._parser,  # sets --config option
            warning=to_stdout,
            add_save=False,  # add a --save-defaults (to config) option
        )
        # find the exe if not specified
        if self._config.get_global('docker-compose') is None:
            dc = find_executable()  # can be None, is ok
            self._config.set_global('docker-compose', dc)
        # self._config._file_name can be handed to objects that need
        # to get other information from the configuration directory
        self._config.set_defaults()
        self._parse_args(
            # default_sub_parser="",
        )

    @sub_parser(help='generate service', aliases=['gen'])
    # @option('--session-name', default='abc')
    @option('--respawn-limit', nargs=2, type=int)
    @option('--no-dc2service-author-info', action='store_true')
    @option('--up-d', action='store_true',
            help='allow (old) "up -d" in ExecStart line')
    @option('--diff', action='store_true',
            help="diff generated service with existing one (no install)")
    @option('dcyaml', nargs='?')
    def generate(self):
        self.dc2s.generate()

    @sub_parser(help='list template files')
    def templates(self):
        self.dc2s.templates()


def find_executable():
    # search for dcw (preferred) or docker-compose
    paths = ['/opt/util/docker-compose/bin'] + sys.path
    for path in paths:
        for exe in [os.path.join(path, 'dcw'), os.path.join(path, 'docker-compose')]:
            if os.path.exists(exe):
                return exe


def main():
    n = DC2ServiceCmd()
    n.parse_args()
    sys.exit(n.run())

if __name__ == '__main__':
    main()
