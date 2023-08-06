# The MIT License (MIT)
#
# Copyright (c) 2015 Philippe Proulx <pproulx@efficios.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from termcolor import cprint, colored
import btctfirtg.config
import btctfirtg.gen
import argparse
import os.path
import btctfirtg
import sys
import os
import re


def _perror(msg):
    cprint('Error: ', 'red', end='', file=sys.stderr)
    cprint(msg, 'red', attrs=['bold'], file=sys.stderr)
    sys.exit(1)


def _pconfig_error(e):
    lines = []

    while True:
        if e is None:
            break

        lines.append(str(e))

        if not hasattr(e, 'prev'):
            break

        e = e.prev

    if len(lines) == 1:
        _perror(lines[0])

    cprint('Error:', 'red', file=sys.stderr)

    for i, line in enumerate(lines):
        suf = ':' if i < len(lines) - 1 else ''
        cprint('  ' + line + suf, 'red', attrs=['bold'], file=sys.stderr)

    sys.exit(1)


def _parse_args():
    ap = argparse.ArgumentParser()

    ap.add_argument('-d', '--declaration', action='store_true',
                    help='generate declaration C code')
    ap.add_argument('-c', '--creation', action='store_true',
                    help='generate creation C code')
    ap.add_argument('-a', '--asserts', action='store_true',
                    help='generate assertions')
    ap.add_argument('-p', '--put-references', action='store_true',
                    help='generate put references C code')
    ap.add_argument('-n', '--no-put-root', action='store_true',
                    help='when using -p, do not put root reference')
    ap.add_argument('-i', '--indent', action='store', type=int, default=0,
                    help='indentation level (default: 0)')
    ap.add_argument('-V', '--version', action='version',
                    version='%(prog)s {}'.format(btctfirtg.__version__))
    ap.add_argument('config', metavar='CONFIG', action='store',
                    help='bt-ctfirtg YAML configuration file')

    # parse args
    args = ap.parse_args()

    # validate that configuration file exists
    if not os.path.isfile(args.config):
        _perror('"{}" is not an existing file'.format(args.config))

    # validate that indentation level is positive
    if args.indent < 0:
        _perror('{} is not a valid indentation level'.format(args.indent))

    return args


def run():
    # parse arguments
    args = _parse_args()

    # create configuration
    try:
        config = btctfirtg.config.from_yaml_file(args.config)
    except btctfirtg.config.ConfigError as e:
        _pconfig_error(e)
    except Exception as e:
        _perror('unknown exception: {}'.format(e))

    # create generator
    generator = btctfirtg.gen.CCodeGenerator(args.indent)

    # generate all?
    if not args.creation and not args.declaration and not args.put_references:
        args.creation = True
        args.declaration = True
        args.put_references = True

    printed = False

    if args.declaration:
        print(generator.generate_declarations(config.root_type))
        printed = True

    if args.creation:
        if printed:
            print()

        print(generator.generate_creations(config.root_type, args.asserts))
        printed = True

    if args.put_references:
        if printed:
            print()

        print(generator.generate_put_references(config.root_type,
                                                args.no_put_root))
