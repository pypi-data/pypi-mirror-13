# coding: utf-8

from __future__ import print_function
from __future__ import absolute_import

_package_data = dict(
    full_package_name="pon",
    version_info=(0, 2, 2, "dev"),
    author="Anthon van der Neut",
    author_email="a.van.der.neut@ruamel.eu",
    description="Python Object Notation",
    keywords="pon object-notation json yaml xml",
    entry_points=None,    # delete or `my_cmd = pon:main` to get executable
    license="MIT license",
    # status=u"α",
    # data_files="",
    universal=False,
    install_requires=dict(
        any = [],
        py26=["ruamel.ordereddict"],
    ),
)   # NOQA


# < from ruamel.util.new import _convert_version
def _convert_version(tup):
    """Create a PEP 386 pseudo-format conformant string from tuple tup."""
    ret_val = str(tup[0])  # first is always digit
    next_sep = "."  # separator for next extension, can be "" or "."
    for x in tup[1:]:
        if isinstance(x, int):
            ret_val += next_sep + str(x)
            next_sep = '.'
            continue
        first_letter = x[0].lower()
        next_sep = ''
        if first_letter in 'abcr':
            ret_val += 'rc' if first_letter == 'r' else first_letter
        elif first_letter in 'pd':
            ret_val += '.post' if first_letter == 'p' else '.dev'
    return ret_val
# <

version_info = _package_data['version_info']
__version__ = _convert_version(version_info)

del _convert_version

import string                                            # NOQA
try:
    from ruamel.ordereddict import ordereddict           # NOQA
except ImportError:
    from collections import OrderedDict as ordereddict   # NOQA
import tokenize                                          # NOQA

import sys                                               # NOQA
import platform                                          # NOQA
import datetime                                          # NOQA
from textwrap import dedent                              # NOQA
from _ast import *                                       # NOQA

if sys.version_info < (3, ):
    string_type = basestring
else:
    string_type = str

if sys.version_info < (3, 4):
    class Bytes():
        pass

    class NameConstant:
        pass

if sys.version_info < (2, 7) or platform.python_implementation() == 'Jython':
    class Set():
        pass


def loads(node_or_string, dict_typ=dict, return_ast=False, file_name=None):
    """
    Safely evaluate an expression node or a string containing a Python
    expression.  The string or node provided may only consist of the following
    Python literal structures: strings, bytes, numbers, tuples, lists, dicts,
    sets, booleans, and None.
    """
    if sys.version_info < (3, 4):
        _safe_names = {'None': None, 'True': True, 'False': False}
    if isinstance(node_or_string, string_type):
        node_or_string = compile(
            node_or_string,
            '<string>' if file_name is None else file_name, 'eval', PyCF_ONLY_AST)
    if isinstance(node_or_string, Expression):
        node_or_string = node_or_string.body
    else:
        raise TypeError("only string or AST nodes supported")

    def _convert(node, expect_string=False):
        if isinstance(node, (Str, Bytes)):
            return node.s
        if expect_string:
            pass
        elif isinstance(node, Num):
            return node.n
        elif isinstance(node, Tuple):
            return tuple(map(_convert, node.elts))
        elif isinstance(node, List):
            return list(map(_convert, node.elts))
        elif isinstance(node, Set):
            return set(map(_convert, node.elts))
        elif isinstance(node, Dict):
            return dict_typ((_convert(k, expect_string=True), _convert(v)) for k, v
                            in zip(node.keys, node.values))
        elif isinstance(node, NameConstant):
            return node.value
        elif sys.version_info < (3, 4) and isinstance(node, Name):
            if node.id in _safe_names:
                return _safe_names[node.id]
        elif isinstance(node, UnaryOp) and \
             isinstance(node.op, (UAdd, USub)) and \
             isinstance(node.operand, (Num, UnaryOp, BinOp)):  # NOQA
            operand = _convert(node.operand)
            if isinstance(node.op, UAdd):
                return + operand
            else:
                return - operand
        elif isinstance(node, BinOp) and \
             isinstance(node.op, (Add, Sub, Mult)) and \
             isinstance(node.right, (Num, UnaryOp, BinOp)) and \
             isinstance(node.left, (Num, UnaryOp, BinOp)):  # NOQA
            left = _convert(node.left)
            right = _convert(node.right)
            if isinstance(node.op, Add):
                return left + right
            elif isinstance(node.op, Mult):
                return left * right
            else:
                return left - right
        elif isinstance(node, Call):
            func_id = getattr(node.func, 'id', None)
            if func_id == 'dict':
                return dict_typ((k.arg, _convert(k.value)) for k in node.keywords)
            elif func_id == 'set':
                return set(_convert(node.args[0]))
            elif func_id == 'date':
                return datetime.date(*[_convert(k) for k in node.args])
            elif func_id == 'datetime':
                return datetime.datetime(*[_convert(k) for k in node.args])
            elif func_id == 'dedent':
                return dedent(*[_convert(k) for k in node.args])
        elif isinstance(node, Name):
            return node.s
        err = SyntaxError('malformed node or string: ' + repr(node))
        err.filename = '<string>'
        err.lineno = node.lineno
        err.offset = node.col_offset
        err.text = repr(node)
        err.node = node
        raise err
    res = _convert(node_or_string)
    if not isinstance(res, dict_typ):
        raise SyntaxError("Top level must be dict not " + repr(type(res)))
    if return_ast:
        return res, node_or_string
    return res


class Formatter(string.Formatter):
    def format(self, *args, **kwargs):
        self.nr_expanded = 0  # gets changed if a field is gotten
        return string.Formatter.format(self, *args, **kwargs)

    def get_field(self, field_name, args, kwargs):
        self.nr_expanded += 1
        return get(kwargs, field_name), field_name


class PON(object):
    sep = '.'
    MAX_DEPTH = 10

    def __init__(self, stream_or_list_or_string=None, obj=None):
        self.rt_info = [[], {}, [], [], False]
        if stream_or_list_or_string is not None:
            if isinstance(stream_or_list_or_string, string_type):
                stream_or_list_or_string = stream_or_list_or_string.splitlines(True)
            if obj is not None:
                raise NotImplementedError("cannot provide stream and object")
            self.extract(stream_or_list_or_string, start='', typ=None)
        else:
            self.obj = obj
        self.fmt = Formatter()

    def load(self, path):
        with open(path) as fp:
            txt = fp.read()
            if sys.version_info < (3,):
                txt = txt.decode('utf-8')
            return loads(txt)

    def get(self, path, expand=None):
        """path is either a string of sections seprated by PON.sep, or a list
        or a tuple (already completely split into sections).
        """
        if expand is True:
            expand = self.obj
        if isinstance(path, tuple):
            sections = list(path)
        elif isinstance(path, list):
            sections = path[:]
        else:
            sections = path.split(PON.sep)
        base = self.obj
        while sections:
            key = sections.pop(0)
            if isinstance(base, list):
                key = int(key)
            base = base[key]
        if expand is not None and isinstance(base, string_type):
            self.fmt.nr_expanded = -1
            depth = 0
            while self.fmt.nr_expanded != 0:
                base = self.fmt.format(base, **expand)
                depth += 1
                if depth > PON.MAX_DEPTH:
                    raise NotImplementedError("Max recursion depth is {0}".format(
                        PON.MAX_DEPTH))
            return base
        return base

    def store(self, path, value):
        sections = path.split(PON.sep)
        base = self.obj
        while len(sections) > 1:
            key = sections.pop(0)
            if isinstance(base, list):
                key = int(key)
            base = base[key]
        base[sections[0]] = value
        return self.obj

    def extract(self, stream_or_list_or_string, start, typ=' = dict(', round_trip=True):
        """read through the stream or list until the string start+typ is found.
        Then accumulate the configuration until the token typ[-1] is found
        in the same position as where start was.
        """

        if isinstance(stream_or_list_or_string, string_type):
            stream_or_list_or_string = stream_or_list_or_string.splitlines(True)
        d = ordereddict if round_trip else dict
        if typ is None:
            res = loads(u''.join(stream_or_list_or_string), dict_typ=d,
                        return_ast=round_trip)
        else:
            process = Process(start, typ)
            for line in stream_or_list_or_string:
                if process(line):
                    break
            res = loads(u''.join(process.lines), dict_typ=d, return_ast=round_trip)
            stream_or_list_or_string = process.lines
        if not round_trip:
            return res
        self.obj = res[0]
        if hasattr(stream_or_list_or_string, 'rewind'):
            stream_or_list_or_string.rewind()
        self.add_comments_to_keys(stream_or_list_or_string, res[1])

    def update(self, file_name, start, typ=' = dict('):
        """update the configuration in a file replacing the part start+typ until the endline
        of that structure. Normally used as

            file_name="__init__.py"
            s = "_package_data"
            t = ' = {'
            with open(file_name) as fp:
                p = PON()
                p.extract(fp, start=s, typ=t)
            # p.dictify()  # <- optional, e.g. if old format
            v = list(p.obj['version_info'])
            v[1] += 1 # update minor version
            v[2] = 0 # set micro version
            p.obj['version_info'] = tuple(v)
            p.update(file_name, start=s, typ=t)
        """
        import io
        with io.open(file_name) as fp:
            lines = list(fp)
        process = Process(start, typ)
        with io.open(file_name, 'w') as fp:
            for line in lines:
                res = process(line)
                if res is False:
                    print(line, end=u'', file=fp)
                elif res is True:
                    fp.write(u'{} = '.format(start))
                    self.dump(fp)

    def add_comments_to_keys(self, lines, ast):
        """ tokenize lines and gather comments
        comments are string, line, column, last_token_ended tuples.
        last_token_ended:
           0 -> full line
           -1 -> full line before dict started.
        """
        key_positions = self._parse_rt_info_from_ast(ast)
        comments = []
        dict_has_started = False
        last_token_ended = -1
        last_dict_line = 0
        for typ, token, start, end, l in tokenize.generate_tokens(ReadLiner(lines).readline):
            # tokenize.printtoken(typ, token, start, end, line)
            if typ == tokenize.COMMENT:
                comments.append((token, start[0], start[1], last_token_ended))
                continue
            if typ == tokenize.NL:
                last_token_ended = 0 if dict_has_started else -1
            else:
                last_token_ended = end[1]
                dict_has_started = True
                if typ != tokenize.ENDMARKER:
                    last_dict_line = start[0]
        ci = 0
        pre = []
        trailing = []
        post = []
        self.rt_info = [pre, key_positions, trailing, post, key_positions.pop(None, None)]
        while ci < len(comments) and comments[ci][3] < 0:
            pre.append(comments[ci])
            ci += 1
        for key in key_positions:
            v = key_positions[key]
            while ci < len(comments) and comments[ci][1] <= v[0]:
                if comments[ci][1] == v[0]:
                    v[4] = comments[ci]
                else:
                    v[3].append(comments[ci])
                ci += 1
        while ci < len(comments) and comments[ci][1] < last_dict_line:
            trailing.append(comments[ci])
            ci += 1
        while ci < len(comments):
            post.append(comments[ci])
            ci += 1

    def dump_rt_info(self):
        for c in self.rt_info[0]:
            print('pre', c)
        for key in self.rt_info[1]:
            v = self.rt_info[1][key]
            print(key, v)
        for c in self.rt_info[2]:
            print('trailing', c)
        for c in self.rt_info[3]:
            print('post', c)

    def _parse_rt_info_from_ast(self, a):
        key_positions = ordereddict()
        self.prefix = []
        res = self._convert(a, key_positions)
        if not isinstance(res, ordereddict):
            raise SyntaxError("Top level must be dict not " + repr(type(res)))
        return key_positions

    def _add_key(self, key_positions, key, line, col, value):
        """
        value == -3: dedented multi-line-string
        value == -2: curly braces style dict ( i.e.  '{}' not 'dict()' )
        value == -1: multi-line-string
        value >= 0: other value item, col_offset
        """
        self.prefix.append(key)
        key_positions[tuple(self.prefix)] = [line, col, value, [], None]

    def _curly_braces_style(self, key_positions):
        """we have to know the dict style ( {}/dict() )"""
        if not self.prefix:  # top level
            key_positions[None] = -2
        else:
            key_positions[tuple(self.prefix)][2] = -2

    def _dedented_multi_line_string(self, key_positions):
        """dedented multiline string"""
        key_positions[tuple(self.prefix)][2] = -3

    def _pop_key(self):
        self.prefix.pop()

    def _get_line_number(self, node):
        lineno = node.lineno
        if node.col_offset == -1:  # multiline string
            try:
                lineno -= node.s.count('\n')
            except:
                # change if anything else then multiline strings
                # can cause this to happen
                raise
        return lineno, node.col_offset, node.col_offset

    def _convert(self, node, key_positions):
        if isinstance(node, List):
            l = []
            for idx, v in enumerate(node.elts):
                line, col, mls = self._get_line_number(v)
                self._add_key(key_positions, idx, line, col, mls)
                l.append(self._convert(v, key_positions))
                self.prefix.pop()
            return l
        elif isinstance(node, Dict):
            d = ordereddict()
            for k, v in zip(node.keys, node.values):
                self._curly_braces_style(key_positions)
                # keys for curly braces style dict are nodes themselves, there is
                # no need for compensation
                kc = k.s  # Str/Bytes Node
                self._add_key(key_positions, kc, k.lineno, k.col_offset, v.col_offset)
                d[kc] = self._convert(v, key_positions)
                self._pop_key()
            return d
        elif isinstance(node, Call):
            func_id = getattr(node.func, 'id', None)
            if func_id == 'dict':
                d = ordereddict()
                for k in node.keywords:
                    line, col, mls = self._get_line_number(k.value)
                    self._add_key(key_positions, k.arg, line, col, mls)
                    d[k.arg] = self._convert(k.value, key_positions)
                    self._pop_key()
                return d
            elif func_id == 'set':
                return set(self._convert(node.args[0], key_positions))
            elif func_id == 'dedent':
                self._dedented_multi_line_string(key_positions)
                return None
        elif isinstance(node, Name):
            if sys.version_info < (3, 4) and isinstance(node, Name) and \
               node.id in ['None', 'True', 'False']:
                return node.id
            return node.s

    def dictify(self):
        """try to make "curly braces" style dicts in the config into "dict()" style ones"""
        import keyword    # to test string when dictify-ing, clashes with from ast import *

        def keys_ok_for_dict(iterable):  # hand in dict, or keys
            for sub_key in iterable:
                if not isinstance(sub_key, string_type):
                    return False
                if ' ' in sub_key:
                    return False
                if keyword.iskeyword(sub_key):
                    return False
            return True

        if keys_ok_for_dict(self.obj):
            self.rt_info[4] = False
        for k in self.rt_info[1]:
            v = self.rt_info[1][k]
            if len(v) > 1 and v[2] == -2:
                # check here for any subkeys with spaces or other "dict()"
                # prohibiting behaviour.
                if keys_ok_for_dict(self.get(k)):
                    v[2] = 1

    def dump(self, fp=sys.stdout):
        from pon.dump import PrettyPrinter

        pp = PrettyPrinter(stream=fp, indent=4, width=80, depth=None,
                           rt_info=self.rt_info)
        pp.pprint(self.obj)


def get(obj, path, expand=None):
    return PON(obj=obj).get(path, expand=expand)


def store(obj, path, value):
    return PON(obj=obj).store(path, value)


def extract(stream_or_list, start, typ=' = dict('):
    return PON().extract(stream_or_list, start, typ=typ, round_trip=False)


class ReadLiner:
    def __init__(self, lines):
        self.lines = lines
        self.idx = -1

    def readline(self):
        self.idx += 1
        if self.idx >= len(self.lines):
            raise StopIteration
        return self.lines[self.idx]


class Process:
    def __init__(self, start, typ):
        self.lines = []
        self.start = start
        self.typ = typ
        self.match = start + typ
        self.indent = None
        # don't have to do list in next match, top level should be dict
        self.end = {'{': '}', '(': ')', '[': ']'}[typ[-1]]

    def __call__(self, line):
        assert isinstance(line, string_type)
        if self.indent is None:
            pos = line.find(self.match)
            if pos == -1:
                return False
            self.indent = pos
            line = line.split('=', 1)[-1].lstrip()
        self.lines.append(line)
        if line[self.indent] == self.end:
            self.indent = None
            return True
