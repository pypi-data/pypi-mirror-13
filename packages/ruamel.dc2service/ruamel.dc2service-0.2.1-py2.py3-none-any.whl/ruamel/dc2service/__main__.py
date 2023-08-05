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
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        self.dc2s = DC2Service(self._args, self._config)
        if self._args.func:
            return self._args.func()

    def parse_args(self):
        self._config = AppConfig(
            'ruamel_dc2service',
            filename=AppConfig.check,
            parser=self._parser,  # sets --config option
            warning=to_stdout,
            add_save=False,  # add a --save-defaults (to config) option
        )
        # self._config._file_name can be handed to objects that need
        # to get other info>mation from the configuration directory
        self._config.set_defaults()
        self._parse_args(
            # default_sub_parser="",
        )

    @sub_parser(help='generate service', aliases=['gen'])
    # @option('--session-name', default='abc')
    @option('--respawn-limit', nargs=2, type=int)
    @option('--no-dc2service-author-info', action='store_true')
    @option('dcyaml', nargs='?')
    def generate(self):
        self.dc2s.generate()

    @sub_parser(help='list template files')
    def templates(self):
        self.dc2s.templates()


def main():
    n = DC2ServiceCmd()
    n.parse_args()
    sys.exit(n.run())

if __name__ == '__main__':
    main()
