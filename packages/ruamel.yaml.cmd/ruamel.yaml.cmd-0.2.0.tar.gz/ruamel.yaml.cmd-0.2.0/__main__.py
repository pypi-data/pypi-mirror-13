# coding: utf-8

"""
this is the source for the yaml utility
"""

from __future__ import print_function
from __future__ import absolute_import

import sys

from ruamel.std.argparse import ProgramBase, option, sub_parser, version, \
    CountAction, SmartFormatter
# from ruamel.appconfig import AppConfig
from . import __version__

from .yaml_cmd import YAML


def to_stdout(*args):
    sys.stdout.write(' '.join(args))


class YAML_Cmd(ProgramBase):
    def __init__(self):
        super(YAML_Cmd, self).__init__(
            formatter_class=SmartFormatter,
            aliases=True,
        )
        self._config = None

    # you can put these on __init__, but subclassing YAML_Cmd
    # will cause that to break
    @option('--verbose', '-v',
            help='increase verbosity level', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @option('--indent', type=int, global_option=True)
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        self._yaml = YAML(self._args, self._config)
        if self._args.func:
            return self._args.func()

    def parse_args(self):
        # self._config = AppConfig(
        #     'yaml',
        #     filename=AppConfig.check,
        #     parser=self._parser,  # sets --config option
        #     warning=to_stdout,
        #     add_save=False,  # add a --save-defaults (to config) option
        # )
        # self._config._file_name can be handed to objects that need
        # to get other information from the configuration directory
        # self._config.set_defaults()
        self._parse_args()

    @sub_parser(
        aliases=['round-trip'],
        help='test round trip on YAML data',
        description='test round trip on YAML data',
    )
    @option('--save', action='store_true', help="""save the rewritten data back
    to the input file (if it doesn't exist a '.orig' backup will be made)
    """)
    @option('file', nargs='+')
    def rt(self):
        return self._yaml.round_trip()

    @sub_parser(
        aliases=['from-json'],
        help='convert json to block YAML',
        description='convert json to block YAML',
    )
    @option('--flow', action='store_true',
            help='use flow instead of block style')
    # @option('--literal', action='store_true',
    #         help='convert scalars with newlines to literal block style')
    @option('--write', '-w', action='store_true',
            help='write a  .yaml file, instead of stdout')
    @option('file', nargs='+')
    def json(self):
        return self._yaml.from_json()

    @sub_parser(
        aliases=['from-ini'],
        help='convert .ini/config to block YAML',
        description='convert .ini/config to block YAML',
    )
    @option('--basename', '-b', action='store_true',
            help='re-use basename of file for .yaml file, instead of writing'
            ' to stdout')
    @option('--test', action='store_true')
    @option('file')
    def ini(self):
        return self._yaml.from_ini()

    @sub_parser(
        # aliases=['to-html'],
        help='convert YAML to html tables',
        description="""convert YAML to html tables. If hierarchy is two deep (
        sequence/mapping over sequence/mapping) this is mapped to one table
        If the hierarchy is three deep, a list of 2 deep tables is assumed, but
        any non-list/mapp second level items are considered text.
        Row level keys are inserted in first column (unless --no-row-key),
        item level keys are used as classes for the TD.
        """,
    )
    @option("--level", action='store_true', help="print # levels and exit")
    @option('--check')
    @option('file')
    def htmltable(self):
        return self._yaml.to_htmltable()

    @sub_parser(
        'from-html',
        help='convert HTML to YAML',
        description="""convert HTML to YAML. Tags become keys with as
        value a list. The first item in the list is a key value pair with
        key ".attribute" if attributes are available followed by tag and string
        segment items. Lists with one item are by default flattened.
        """,
    )
    @option("--no-body", action='store_true',
            help="drop top level html and body from HTML code segments")
    @option("--strip", action='store_true',
            help="strip whitespace surrounding strings")
    @option('file')
    def from_html(self):
        return self._yaml.from_html()

    @sub_parser(
        'from-csv',
        aliases=['csv'],
        help='convert CSV to YAML',
        description="""convert CSV to YAML.
        By default generates a list of rows, with the items in a 2nd level
        list.
        """,
    )
    @option('--delimiter')
    # @option('--quotechar')
    @option('file')
    def from_csv(self):
        return self._yaml.from_csv()

    @sub_parser(
        'from-dirs',
        aliases=['fromdirs'],
        help='combine multiple YAML files into one',
        description="""Combine multiple YAML files into one.
        Path chunks (directories) are converted to mapping entries, the YAML contents
        the value of the (last) key. If there are multiple files in one directory, the
        filenames are used as well (or specify --use-file-name).
        """,
    )
    @option('--output', '-o', help='write to file OUTPUT instead of stdout')
    @option('--use-file-names', action='store_true')
    @option('file', nargs='+', help='full path names (a/b/data.yaml)')
    def fromdirs(self):
        return self._yaml.from_dirs()

    if 'test' in sys.argv:
        @sub_parser(
            description='internal test function',
        )
        @option('file', nargs='*')
        def test(self):
            return self._yaml.test()


def main():
    n = YAML_Cmd()
    n.parse_args()
    sys.exit(n.run())

if __name__ == '__main__':
    main()
