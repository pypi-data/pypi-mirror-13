# coding: utf-8

"""
this is the source for the yaml utility
"""

from __future__ import print_function
from __future__ import absolute_import


import sys
import os
import io
from textwrap import dedent

import ruamel.yaml
from ruamel.yaml.compat import ordereddict, DBG_EVENT, DBG_NODE  # DBG_TOKEN
from ruamel.yaml.configobjwalker import configobj_walker


def yaml_to_html2(code):
    buf = io.StringIO()
    buf.write(u'<HTML>\n')
    buf.write(u'<HEAD>\n')
    buf.write(u'</HEAD>\n')
    buf.write(u'<BODY>\n')
    buf.write(u'<TABLE>\n')
    if isinstance(code, dict):
        for k in code:
            buf.write(u'  <TR>\n')
            for x in [k] + code[k]:
                buf.write(u'    <TD>{0}</TD>\n'.format(x))
            buf.write(u'  </TR>\n')
    elif isinstance(code, list):
        # assume list of (k, v) pairs
        order = []
        for item in code:
            if not order:
                buf.write(u'  <TR>\n')
                for k in item:
                    order.append(k)
                    buf.write(u'    <TD>{0}</TD>\n'.format(k))
                buf.write(u'  </TR>\n')
            buf.write(u'  <TR>\n')
            for k in order:
                buf.write(u'    <TD>{0}</TD>\n'.format(item.get(k)))
            buf.write(u'  </TR>\n')

    buf.write(u'<TABLE>\n')
    buf.write(u'</BODY>\n')
    buf.write(u'</HTML>\n')
    return buf.getvalue()


def yaml_to_html(code, level):
    if level == 2:
        return yaml_to_html2(code)
    # elif level == 3:
    #     return yaml_to_html3(code)
    raise NotImplementedError


def commentify(data, sort_dict=True):
    """convert any normal dict and list in data to CommentedMap resp CommentedSeq
    and handle **their** values recursively
    """
    from ruamel.yaml.comments import CommentedMap, CommentedSeq

    def conv(d):
        if isinstance(d, (CommentedMap, CommentedSeq)):
            return d
        if isinstance(d, dict):
            ret_val = CommentedMap()
            if sort_dict and not isinstance(d, ordereddict):
                for key in sorted(d):
                    ret_val[key] = conv(d[key])
            else:
                for key in d:
                    ret_val[key] = conv(d[key])
            return ret_val
        if isinstance(d, list):
            ret_val = CommentedSeq()
            for k in d:
                ret_val.append(conv(k))
            return ret_val
        return d
    return conv(data)


class YAML:
    def __init__(self, args, config):
        self._args = args
        self._config = config

    def from_ini(self):
        try:
            from configobj import ConfigObj
        except ImportError:
            print("to convert from .ini you need to install configobj:")
            print("  pip install configobj:")
            sys.exit(1)
        errors = 0
        doc = []
        cfg = ConfigObj(open(self._args.file))
        if self._args.test:
            print(ruamel.yaml.dump(cfg))
            return
        for line in configobj_walker(cfg):
            doc.append(line)
        joined = '\n'.join(doc)
        rto = self.round_trip_single(joined)
        if self._args.basename:
            out_fn = os.path.splitext(self._args.file)[0] + '.yaml'
            if self._args.verbose > 0:
                print('writing', out_fn)
            with open(out_fn, 'w') as fp:
                print(rto, end='', file=fp)  # already has eol at eof
        else:
            print(rto, end='')  # already has eol at eof
        # print()
        # if rto != joined:
        #     self.diff(joined, rto, "test.ini")
        return 1 if errors else 0

    def test(self):
        self._args.event = self._args.node = True
        dbg = 0
        if self._args.event:
            dbg |= DBG_EVENT
        if self._args.node:
            dbg |= DBG_NODE
        os.environ['YAMLDEBUG'] = str(dbg)
        if False:
            x = ruamel.yaml.comment.Comment()
            print(sys.getsizeof(x))
            return

        def print_input(input):
            print(input, end='')
            print('-' * 15)

        def print_tokens(input):
            print('Tokens (from scanner) ' + '#' * 50)
            tokens = ruamel.yaml.scan(input, ruamel.yaml.RoundTripLoader)
            for idx, token in enumerate(tokens):
                # print(token.start_mark)
                # print(token.end_mark)
                print("{0:2} {1}".format(idx, token))

        def rt_events(input):
            dumper = ruamel.yaml.RoundTripDumper
            events = ruamel.yaml.parse(input, ruamel.yaml.RoundTripLoader)
            print(ruamel.yaml.emit(events, indent=False, Dumper=dumper))

        def rt_nodes(input):
            dumper = ruamel.yaml.RoundTripDumper
            nodes = ruamel.yaml.compose(input, ruamel.yaml.RoundTripLoader)
            print(ruamel.yaml.serialize(nodes, indent=False, Dumper=dumper))

        def print_events(input):
            print('Events (from parser) ' + '#' * 50)
            events = ruamel.yaml.parse(input, ruamel.yaml.RoundTripLoader)
            for idx, event in enumerate(events):
                print("{0:2} {1}".format(idx, event))

        def print_nodes(input):
            print('Nodes (from composer) ' + '#' * 50)
            x = ruamel.yaml.compose(input, ruamel.yaml.RoundTripLoader)
            x.dump()  # dump the node

        def scan_file(file_name):
            inp = open(file_name).read()
            print('---------\n', file_name)
            print('---', repr(self.first_non_empty_line(inp)))
            print('<<<', repr(self.last_non_empty_line(inp)))

        if False:
            for x in self._args.file:
                scan_file(x)
            return

        if True:
            import pickle
            lines = 0
            for x in self._args.file:
                print(x, end=' ')
                if x.endswith('.yaml'):
                    data = ruamel.yaml.load(open(x))
                    print(len(data), end=' ')
                    lines += len(data)
                    out_name = x.replace('.yaml', '.pickle')
                    with open(out_name, 'w') as fp:
                        pickle.dump(data, fp)
                elif x.endswith('.pickle'):
                    with open(x) as fp:
                        data = pickle.load(fp)
                    print(len(data), end=' ')
                    lines += len(data)
                print()
            print('lines', lines)
            return

        input = dedent("""
        application: web2py
        version: 1
        runtime: python27
        api_version: 1
        threadsafe: false

        default_expiration: "24h"

        handlers:
        - url: /(?P<a>.+?)/static/(?P<b>.+)
          static_files: 'applications/\\1/static/\\2'
          upload: applications/(.+?)/static/(.+)
          secure: optional
        """)

        input = dedent("""\
        a:
            b: foo
            c: bar
        """)

        print_input(input)
        print_tokens(input)
        print_events(input)
        # rt_events(input)
        print_nodes(input)
        # rt_nodes(input)

        data = ruamel.yaml.load(input, ruamel.yaml.RoundTripLoader)
        print('data', data)
        if False:
            data['american'][0] = 'Fijenoord'
            l = data['american']
        l = data
        if True:
            # print type(l), '\n', dir(l)
            comment = getattr(l, '_yaml_comment', None)
            print('comment_1', comment)
        dumper = ruamel.yaml.RoundTripDumper
        print('>>>>>>>>>>')
        # print(ruamel.yaml.dump(data, default_flow_style=False,
        #    Dumper=dumper), '===========')
        print("{0}=========".format(ruamel.yaml.dump(
            data,
            indent=4,
            Dumper=dumper)))
        comment = getattr(l, '_yaml_comment', None)
        print('comment_2', comment)

        # test end

    def from_json(self):
        # use roundtrip to preserve order
        errors = 0
        docs = []
        dumper = ruamel.yaml.RoundTripDumper
        for file_name in self._args.file:
            if not self._args.write and file_name == '-':
                inp = sys.stdin.read()
            else:
                inp = open(file_name).read()
            loader = ruamel.yaml.Loader  # RoundTripLoader
            data = ruamel.yaml.load(inp, loader)
            data = commentify(data)
            if self._args.write:
                yaml_file_name = os.path.splitext(file_name)[0] + '.yaml'
                with open(yaml_file_name, 'w') as fp:
                    ruamel.yaml.dump(data, fp,
                                     Dumper=dumper,
                                     default_flow_style=self._args.flow,
                                     allow_unicode=True,
                                     )
            else:
                docs.append(data)
        if self._args.write:
            return 1 if errors else 0
        # if self._args.literal:
        #     from ruamel.yaml.convert.literal import walk_tree
        #     for doc in docs:
        #         walk_tree(doc)
        print(ruamel.yaml.dump_all(
            docs, Dumper=dumper,
            default_flow_style=self._args.flow,
            allow_unicode=True,
        ))
        return 1 if errors else 0

    def to_htmltable(self):
        def vals(x):
            if isinstance(x, list):
                return x
            if isinstance(x, (dict, ordereddict)):
                return x.values()
            return []

        def seek_levels(x, count=0):
            my_level = count
            sub_level = 0
            for v in vals(x):
                if v is None:
                    continue
                sub_level = max(sub_level, seek_levels(v, my_level+1))
            return max(my_level, sub_level)

        inp = open(self._args.file).read()
        loader = ruamel.yaml.RoundTripLoader
        code = ruamel.yaml.load(inp, loader)
        # assert isinstance(code, [ruamel.yaml.comments.CommentedMap])
        assert isinstance(code, (dict, list))
        levels = seek_levels(code)
        if self._args.level:
            print("levels:", levels)
            return
        print(yaml_to_html(code, levels))

    def from_html(self):
        from .convert.html import HTML2YAML
        h2y = HTML2YAML(self._args)
        with open(self._args.file) as fp:
            print(h2y(fp.read()))

    def from_csv(self):
        from .convert.from_csv import CSV2YAML
        c2y = CSV2YAML(self._args)
        c2y(self._args.file)

    def from_dirs(self):
        import glob
        files = []
        for fn in [glob.glob(fns) for fns in self._args.file]:
            files.extend(fn)
        if not self._args.use_file_names:
            dirs = set()
            for fn in files:
                dn = os.path.dirname(fn)
                if dn in dirs:
                    print('double directory {}, using file names'.format(dn))
                    self._args.use_file_names = True
                    break
                else:
                    dirs.add(dn)
        tl_data = ruamel.yaml.comments.CommentedMap()
        for fn in sorted(files):
            path = os.path.dirname(fn).split(os.path.sep)
            if self._args.use_file_names:
                bn, ext = os.path.splitext(fn)
                if ext == '.yaml':
                    path.append(bn)
                else:
                    path.append(fn)
            parent_data = tl_data
            while (path):
                key, path = path[0], path[1:]
                if path:
                    data = ruamel.yaml.comments.CommentedMap()
                else:
                    data = ruamel.yaml.load(open(fn), Loader=ruamel.yaml.RoundTripLoader)
                parent_data = parent_data.setdefault(key, data)
            # parent_data =
        res = ruamel.yaml.dump(tl_data, Dumper=ruamel.yaml.RoundTripDumper)
        if self._args.output:
            with open(self._args.output, 'w') as fp:
                fp.write(res)
        else:
            print(res)

    def round_trip(self):
        errors = 0
        warnings = 0
        for file_name in self._args.file:
            inp = open(file_name).read()
            e, w, stabilize, outp = self.round_trip_input(inp)
            if w == 0:
                if self._args.verbose > 0:
                    print(u"{0}: ok".format(file_name))
                continue
            if self._args.save:
                backup_file_name = file_name + '.orig'
                if not os.path.exists(backup_file_name):
                    os.rename(file_name, backup_file_name)
                with open(file_name, 'w') as ofp:
                    ofp.write(outp)
            if not self._args.save or self._args.verbose > 0:
                print("{0}:\n     {1}".format(file_name,
                                              u', '.join(stabilize)))
                self.diff(inp, outp, file_name)
            errors += e
            warnings += w
        if errors > 0:
            return 2
        if warnings > 0:
            return 1
        return 0

    def round_trip_input(self, inp):
        errors = 0
        warnings = 0
        stabilize = []
        outp = self.round_trip_single(inp)
        if inp == outp:
            return errors, warnings, stabilize, outp
        warnings += 1
        if inp.split() != outp.split():
            errors += 1
            stabilize.append(u"drops info on round trip")
        else:
            if self.round_trip_single(outp) == outp:
                stabilize.append(u"stabilizes on second round trip")
            else:
                errors += 1
        ncoutp = self.round_trip_single(inp, drop_comment=True)
        if self.round_trip_single(ncoutp, drop_comment=True) == ncoutp:
            stabilize.append(u"ok without comments")
        return errors, warnings, stabilize, outp

    def round_trip_single(self, inp, drop_comment=False):
        explicit_start = self.first_non_empty_line(inp) == '---'
        explicit_end = self.last_non_empty_line(inp) == '...'
        indent = self._args.indent
        loader = ruamel.yaml.SafeLoader if drop_comment else \
            ruamel.yaml.RoundTripLoader
        code = ruamel.yaml.load(inp, loader)
        dumper = ruamel.yaml.SafeDumper if drop_comment else \
            ruamel.yaml.RoundTripDumper
        return ruamel.yaml.dump(
            code,
            Dumper=dumper,
            indent=indent,
            explicit_start=explicit_start,
            explicit_end=explicit_end,
        )

    def first_non_empty_line(self, txt):
        """return the first non-empty line of a block of text (stripped)
        do not split or strip the complete txt
        """
        pos = txt.find('\n')
        prev_pos = 0
        while pos >= 0:
            segment = txt[prev_pos:pos].strip()
            if segment:
                break
            # print (pos, repr(segment))
            prev_pos = pos
            pos = txt.find('\n', pos+1)
        return segment

    def last_non_empty_line(self, txt):
        """return the last non-empty line of a block of text (stripped)
        do not split or strip the complete txt
        """
        pos = txt.rfind('\n')
        prev_pos = len(txt)
        maxloop = 10
        while pos >= 0:
            segment = txt[pos:prev_pos].strip()
            if segment:
                break
            # print (pos, repr(segment))
            prev_pos = pos
            pos = txt.rfind('\n', 0, pos-1)
            maxloop -= 1
            if maxloop < 0:
                break
        return segment

    def diff(self, inp, outp, file_name):
        import difflib
        inl = inp.splitlines(True)  # True for keepends
        outl = outp.splitlines(True)
        diff = difflib.unified_diff(inl, outl, file_name, 'round trip YAML')
        # 2.6 difflib has trailing space on filename lines %-)
        strip_trailing_space = sys.version_info < (2, 7)
        for line in diff:
            if strip_trailing_space and line[:4] in ['--- ', '+++ ']:
                line = line.rstrip() + '\n'
            sys.stdout.write(line)
