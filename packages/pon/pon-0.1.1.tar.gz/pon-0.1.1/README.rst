
Python Object Notation
======================

Python Object Notation (PON) fills the need for simple, human usable
and maintainable, configuration data file format for Python.

A basic example of a PON file::

  dict(
    version = [1, 2, 3],  # Major, Minor and Micro version number
    email = "avdn@europython.org",
    score = 8.7,
    restrictions = None,
    published = True,
    install_requires=dict(   # nested structure
      any=['requests', 'beautifulsoup'],
      py26=['ordereddict'],
    ),
    oddkeys = { "2":  2, "s p a c e d": "out"}
  )

.. example pon basic.pon


PON:

- is readable and maintainable through familiarity for all Python programmers
- allows comments
- is editable by humans without breaking things every other time
- is efficiently and securely loadable
- Has basic types: string, numbers (including simple math), ``True``,
  ``False``, ``None``, ``date()``, datetime (in UTC, no timezone info)
- basic structures: dict (``dict()`` / ``{}``) and list (``[]``),
- extended structures: set (``set()`` / ``{}`` (the latter only on
  2.7+) and tuples (``( )``)
- basic and extended structures which can be nested (within its own
  type as well as in the other type) with the following restrictions:

  - top level must be a dict
  - no syntax for self references
  - ``{ }`` can only having strings as keys
  - children of the extended structures (set, tuple) cannot be
    referenced for subsitutions

- has substitutions/interpolations on string values, with the
  substitute value, being the ``str()`` result of a possible complex value
- can be embedded in a Python file as it is valid Python code, and
  provides routines to extract such an embedded configuration.
- expects UTF-8 based input
- has support for multi-line strings through normal triple-quoting, as
  well as for ``dedent``-ing those multi-line strings
- has a read-only parser with a small enough footprint to not
  necessarily require a package to be installed before you can use it
  (e.g. the basic XX line parser in several ``setup.py`` files in
  packages on PyPI)
- with a few restrictions, supports round-tripping without the loss of
  comments and without the loss of carefully ordered keys
- Output is PEP8 except for allowing (but not requiring) spaces around
  the ``=`` following a ``dict()`` key


Why not YAML/XML/INI-CFG/JSON
-----------------------------


YAML
....

YAML fulfils all of the requirements of the PON except for the string
substitution on values. And it can fulfil more complex tasks, like
handling (self) references and complex dict/mapping keys. However the
basics are easily readable, not all of its syntactical variations
might be familiar. 

The main problem is that it requires an external library (ruamel.yaml
for YAML1.2 (with roundtrip preservation of comments), PyYAML for 1.1
(with guaranteed loss of comments) and e.g. cannot be used within a
``setup.py``.

XML
...

An XML parser ships with python so using that from any program is
possible. XML combines the inefficiency of ASCII with the illegibility
of binary. 'nnuf said.

INI

INI/CFG files are familiar to a lot of people, but unfortunately there
are all kinds of variations and extensions. Python's built-in
``configparser`` (``ConfigParser`` in < Python 3.0), provides only
limited structural information. It is essentially a dict (with the
sections as keys) each with a dict as value (the key, value pairs). It
supports multi-line strings in a traditional way (indented
continuation lines), comments and has interpolation in two different
forms.

JSON
....

JSON is a format familiar to many for data exchange. However several
things make it inapplicability for configuration files that are manipulated by
humans:

  - the unavailability to handle comments in most implementations
    (including Python's ``json`` module), although the inventor specified
    these should be ignored
  - humans generating an invalid format on every other, edit because
    commas are separators and are not allowed before list/dict terminal
    ``]`` resp. ``}``
  - require even simple dict keys to be obfuscated by quotes

Python has most of the batteries for PON included
-------------------------------------------------

In Python you can already do::

  config = dict(
      version = [1, 2, 3],  # Major, Minor and Micro version number
      email = "avdn@europython.org",
      score = 8.7,
      restrictions = None,
      published = True,
      install_requires=dict(   # nested structure
          any=['requests', 'beautifulsoup',],
          py26=['ordereddict']
      ),
  )

.. example code ponispython.pon

This **is** python code, and the embedding requirement is implicitly
taken care of.  The problem is you don't always want to
evaluation/include this *as code* because of security
implications. You need to be able to parse this and reject invalid or
dangerous constructs.

(Please notice you can delete just the whole``py26=``line in the above
without breaking things because you end up with a comma before the
closing parenthesis.)

Parsing out PON (almost) of the box
-----------------------------------

The function ``literal_eval`` from the ``ast`` module can parse a more
JSON like variation of the previous config. E.g. the contents of the
following file::

  {
    "version": [1, 2, 3],  # Major, Minor and Micro version number
    "email": "avdn@europython.org",
    "score": 8.7,
    "restrictions": None,
    "published": True,
    "install_requires": {   # nested structure
      "any": ['requests', 'beautifulsoup',],
      "py26": ['ordereddict']
    },
  }

.. example pon literal_eval.pon

using the following::

   python -c 'import ast; ast.literal_eval(open("input2.pon").read())

The above can also be relatively easily parsed from a larger (Python
source) file by looking for the assignment to a known variable, ``config = {`` and the corresponding ``}`` (usually at the same indentation level).

The is almost JSON, but to be able to include **that** in Python, as well as
parse that from JSON, you need to change it some more::

  true = True
  null = None
  config = {
      "version": [1, 2, 3],
      "email": "avdn@europython.org",
      "score": 8.7,
      "restrictions": null,
      "published": true,
      "install_requires": {
          "any": ["requests", "beautifulsoup",],
          "py26": ["ordereddict"]
      }
  }

.. example code almost_json.json

You have to define ``null`` and ``true`` for the Python parser. For
JSON you also have to remove the comments, and consistently use double
quotes for strings. And above all you have to remove trailing commas,
which is most often forgotten when deleting whole key-value lines at
the end of a dictionary/mapping in JSON (resulting in non-running
programs unless you use ruamel.yaml/PyYAML to load your JSON files).

Actually, the above is not valid JSON (did you see the trailing comma
in the list on the ``any`` line?). These problems don't make JSON a
bad format. It is fine for information interchange between
programs. JSON files should just never be edited, and preferably not
even have to be read, by humans.


A replacement for literal_eval
------------------------------

``ast.literal_eval`` cannot deal with ``dict()``, so using that you
cannot have keys that are strings, without the need for quotes. It
also throws a useless generic ValueError, when it is fed invalid
strings, making it difficult to provide meaningful feedback to the
human supplier of the (invalid) configuration data. And finally it
happily tries and fails to do its job when you feed it a nonsense data
like a float.

``ast.literal_eval`` is a good example how you can make a minimal
evaluator around the ``ast`` facilities. A small adaptation can handle
the extras like ``dict``, ``date`` and ``datetime``. Thus allowing
non-quoted simple keys, while disallowing non string keys for ``{}``,
forcing a toplevel dictionary. The code including adaptations for 2.6
and later support (2.6's cannot handle `{}` type sets)::

  import sys
  import datetime
  from textwrap import dedent
  from _ast import *       # NOQA
  
  if sys.version_info < (3, ):
      string_type = basestring
  else:
      string_type = str
  
  if sys.version_info < (3, 4):
      class Bytes():
          pass
  
      class NameConstant:
          pass
  
  if sys.version_info < (2, 7):
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
  
The above 108 lines of Python **is** the actual code, that loads the full PON from an iterable.


.. example output loads_min.py

This code can be further reduced if you only need to support later
Python versions, and if you know your input is restricted (no math, no
set/tuples/``{}``, no datetime, etc)


SyntaxError
...........

The ``ast.literal_eval`` gives you a generic ValueError without any
indication of what might be wrong where in the input. From the
``SyntaxError`` that is raised on erroreous input by ``loads()`` you
can retrieve useful line information::

  error_str = u"""
  dict(
      a= u"α",
      b= False,
      c= date(2015, 9, 12),
      d= 1.37,
  )
  """

  try:
      loads(error_str)
  except SyntaxError as e:
      context = 2
      from_line = e.lineno - (context + 1)
      to_line = e.lineno + (context - 1)
      w = len(str(to_line))
      for index, line in enumerate(error_str.splitlines(True)):
          if from_line <= index <= to_line:
              print(u"{:{}}: {}".format(index, w, line), end=u'')
              if index == e.lineno - 1:
                  print(u"{:{}}  {}^--- {}".format(
                      u' ', w, u' ' * e.offset, e.node))

giving you::

  2:    a= u"α",
  3:    b= False,
  4:    c= date(2015, 9, 12),
           ^--- <_ast.Call object at 0x7f1598d20950>
  5:    d= 1.37,
  6: )

Motivation
----------

The development of the ``literal_eval`` extension/replacement was
motivated by cleaning providing version and other information from the
``__init__.py`` of a package to its ``setup.py`` file, thereby
minimising the clutter of extra configuration files in the base
directory (it is bad enough with ``setup.py``, ``dist`` and
``tox.ini`` as non hidden files/directories.

A version number can be easily parsed from an ``__init__.py`` file.
But allowing for more complex and complete configuration data allows
``setup.py`` to be the same for all of my projects.

Using the ``pon`` package
-------------------------

The ``pon`` package provides the the main parser
``loads()``, the utility functions ``get()``, ``store()`` and
``extract()`` and the PON class (for which the utilities are shortcuts).


``get()`` and ``store()``
.........................

If you have configuration::

    dict(
        a = dict(
            b = 24,
            c = [1, 3.14, {'d': 'klm'}],
    }

loaded into a variable ``config``, you can access the value ``klm`` in
the normal Python way by using ``config['a']['c'][2]['d']``. PON also
provides the function ``get()`` with which you can access the same
value using ``get(config, 'a.c.2.d')``.

Based on the nested structure of ``config`` the "2" in that sequence is
converted to an index. As indicated integers as dict keys, are not allowed.

Complementary there is the ``store()`` function (``set()`` being reserved)
that takes as third parameter a value, to set or overwrite an existing one:
``store(config, 'a.c.2.d', 'xyz')``


Substitution with ``get()``
...........................

Substitution (called interpolation in
``ConfigParser``/``configparser``) is done by accessing a value of
your configuration with with ``get()``, and providing the extra
keyword ``expand``. Substitution is done recursively on the expanded value.
You can provide the ``config`` object itself to expand::

   val = get(config, 'some.path', expand=config)

and since this is such a common use case, you can specify ``expand=True``
instead of actually passing in ``config`` twice.

The syntax for substitution is the usual Python,
``"{key}".format(key=value)``, string formatting but the key can be a
dotted sequence valid for ``get()``::

  import pon
  
  config = pon.loads("""\
  dict(
      a = dict(
          image = "http://{domain}/images",
          alt = "europython.eu",
          dd = (2011, 10, 2)  # this is a tuple
      ),
      domain = 'python.{tld.organisations}',
      datestr = 'date{a.dd}',
      tld = {"organisations": "org", "commmercian": "com"}
  )
  """)
  
  for key in ['a.image', 'datestr']:
      print(key, '->', pon.get(config, key, expand=config))

.. example code substitute.py

giving::

  a.image -> http://python.org/images
  datestr -> date(2011, 10, 2)


.. example output substitute.py

The recursion level is restricted to 10. The separator (".") can
be set on the ``PON`` class, but since ":" is special in format strings,
that character cannot be used.

RoundTripping PON
-----------------

With some restrictions it is possible to round trip PON, while
preserving comments, just like ruamel.yaml can:
- you will not lose any data
- on the first round-trip your formatting might change
- a second round-trip will result in the same output as the first round-trip

In order to facilitate round-tripping extra information needs to be
kept that is not available in the normal dict you get from the loading
of your PON data structure into Python. This extra processing can be
done up-front, after which the original configuration data is no
longer necessary in text form, but wastes time during loading in case
the round-tripping is never needed. It can be extracted on demand, but
in that case the original textual data needs to be available. This
time vs storage trade of is currently done at load time, and only when
using the PON class (and not when using utility function ``loads()``).

If you create a PON object from ``input`` (a file, a string or a list
of strings) using ``PON(input)`` the resulting object will have
information about the dict keys and list elements and has comment
information associated with these keys.

The primary purpose for round-tripping is updating existing
information in the configuration: updating one of the tuple values for
key "version", adding a dependency package to the list necessary for
``py26``. If a whole new configuration file including comments needs
to be generated, this can generally be done more easily by using (or
starting from) a text template.

Comments
........

Dumping the loaded PON structure as text, assuming some formatting
criteria, is relatively easy, if we would just ignore the fact that
comments are important for future readers of the dumped information.

The Python built-in ``compile()`` function generating the AST
information from which the object holding the configuration
information, is extracted, throws away the comments. The comment
information has to be re-associated with the object and in addition to
determining what comment belongs where, this requires that the
elements in the object tree can be extended (requiring more complex
objects that behave like dicts/lists, but have extra slots for comment
information, a method which ruamel.yaml uses) or that a shadow
structure is kept in the same form as the configuration object.

PON follows a hybrid by requiring the dictionaries to have key
insertion ordering (the ordering of the keys in the source
configuration data) as well as keeping a shadow structure. The shadow
structure is extracted from the AST tree (used for generating/checking
the configuration loaded) with tokenization information (which
provides the comments).

Comments are associated with dictionary keys or list elements as far
as these are "on their own line". A full line comment belongs, or
consecutive comments belong, to the next key/element if it is on a
line of its own after the previous key/element. An end-of-line comment
follows a key/element at the end of a line (and there can be only
one). Additionally track is kept of comments before the initial, top
level, ``dict(``, after the final key (there is no following one to
hook it up to) and after the dict closing ``)`` token.

An example of a heavily commented PON file::

  # this is the configuration driving setup
  # initials comments going before the configuration information
  dict(   # the top level dict can also have an end-of-line comment
      # full comment associated with the key version
      # this doesn't explain its usage that much, also associates with version
      version=(1, 2, 3)    # end-of-line comment for version
      alt = dict(   # this is end-of-line for alt
          # associated with place
          place=u"Düsseldorf",  
          taste="awful",
          # the next key is klm, this comment  will move down on round-trip.
      ),  # this is assocated with klm as well, even though not a end-of-line
      "klm" = [ 3, 5, 6 ],  # although list elements, belongs to klm
      "xyz" = [   # belong to xyz
          42,     # the answer (associated with 42)
          196,
      ],
      # trailing comment, special
  )
  # still more to say, special as well

If you change dictionary keys, comments associated with these will
generally get lost. So do comments associated with key/element that
get deleted.

Changes on first round trip
...........................

Partly due to the ``pprint`` code on which the dumper is based, partly
due to arbitrary decisions on what kind of formatting info is
preserved and partly depending on your input the following happens on
the first round-trip:

- the last element on a multi-line dict/list gets a trailing comma
- comments that cannot be associated with an dict key or list element
  on the same line get moved to the next key/element (or the end of
  the main dict if no following elements)
- strings are single quoted unless they contain a single quote (and no
  double quotes)
- indent levels are a at 4 spaces
- space around the equal sign between dict keys and values is removed
- sets and tuples elements cannot be associated with comments, hence comments 
  wander if they are not on the same line as a dict-key/list-element 
- sets and tuples are dumped on a single line, any dicts and lines
  underneath them are currently inaccessible for ``get()`` and
  therefore keys/elements for such dicts/lists cannot be associated
  with comments
- extra lines with white space are silently dropped
- add/subtract/multiply is not preserved
- the datetime ``repr()`` drops trailing milliseconds if and seconds if
  they equal zero.

No data or comments gets lost, unless you manipulate dict keys and/or
list length. And if the output from a dump is taken as source there
should be no further "wandering". The following input::

  
  try:
      from cStringIO import StringIO as _StringIO
  except ImportError:
      from io import StringIO as _StringIO
  
  from pon import PON
  
  input = """
  dict(
      pckgs = dict(
          any=['package1', 'package2'],
          py26=['another package', 'and one with a long name',
          'and on a new line']   # where do you go?
      ),
  )
  """
  
  out1 = _StringIO()
  p1 = PON(input)
  p1.dump(out1)
  print(out1.getvalue())
  
  out2 = _StringIO()
  p2 = PON(out1.getvalue())
  p2.dump(out2)
  
  
  print('roundtrip 1: {0}, roundtrip 2: {1}'.format(
      input == out1.getvalue(),
      out1.getvalue() == out2.getvalue()))

.. example code reformat.py

gives the following output::

  dict(
      pckgs=dict(
          any=['package1', 'package2'],
          py26=['another package', 'and one with a long name',
          'and on a new line',   # where do you go?
          ],
      ),
  )
  
  roundtrip 1: False, roundtrip 2: True


.. example output reformat.py

Further improvements
....................

- The set and tuple elements could be indexed, and then comments could
  be associated with their elements, and multi-line dumping would be
  better preserved.

- The ``dump()`` could take parameters about indentation depth and on
  string quoting information.

- The ``dump()`` output should be PEP8 compliant in principle. But IMO
  the removal of spaces around the `=` in a multi-line keyword
  argument assignment for ``dict()`` doesn't make thing more
  readable. A parameter to select one or the other would be useful::


   dict(
      a='1234324',
      b=['xyz', 'klm'],
   )

  is less easy to read than::

   dict(
      a = '1234324',
      b = ['xyz', 'klm'],
   )

- Keeping the ``#`` of comments on multiple consecutive lines aligned,
  even if a value was changed before dumping and has become longer.

Showcase
--------

The following program contains most (if not all) of the facilities
and round-trips::

  
  from io import StringIO as _StringIO
  from pon import PON
  
  configs = u'''\
  # example config
  # should contain all types and facilities
  dict(
      s='abc',  # single line string
      # multiline string
      mls="""one
      two
      three""",
      mls_dedent=dedent("""
          abc
          def
      """),
      ghi={'A': 1, 'B': 2},
      klm=['Airbus 370', 'Fokker 100'],
      opq=set([2, 3, 5, 7, 9]),
      rst=(0, 1, 1, 2, 3, 5, 8, 13),   # Fibonacci
      m={u'π': 3.14},
      anniversary=date(2011, 10, 2),
      dts=datetime(1919, 12, 1, 13, 45, 4),
      milisec=datetime(1922, 10, 19, 17, 55, 23, 321),
      six=2 + 4,
      secs_per_day=24 * 60 * 60,
      two=-2 - -4,
      # if you want to extend, do it here
  )
  # and it's over
  '''
  
  out = _StringIO()
  p = PON(configs)
  p.dump(out)
  conf_adjust_for_calc = configs
  # calculations are not preserved, they don't round trip, so adjust here
  for x, y in ((u'2 + 4', u'6'),
               (u'24 * 60 * 60', u"{}".format(24 * 60 * 60)),
               (u'-2 - -4', u'2')):
      conf_adjust_for_calc = conf_adjust_for_calc.replace(x, y)
  print('roundtrip 1: {0}'.format(out.getvalue() == conf_adjust_for_calc))

.. example code showcase.py

with output::

  roundtrip 1: True


.. example output showcase.py


.. todo:

