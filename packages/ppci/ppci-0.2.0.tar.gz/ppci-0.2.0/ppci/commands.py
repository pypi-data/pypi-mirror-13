"""
    Contains the command line interface functions.
"""
import sys
import platform
import argparse
import logging

from .pcc.yacc import transform
from .utils.hexfile import HexFile
from .binutils.objectfile import load_object, print_object
from .tasks import TaskError
from . import version, api
from .common import logformat
from .arch.target_list import target_names


version_text = 'ppci {} compiler on {} {}'.format(
    version, platform.python_implementation(), platform.python_version())


def log_level(s):
    """ Converts a string to a valid logging level """
    numeric_level = getattr(logging, s.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(s))
    return numeric_level


base_parser = argparse.ArgumentParser(add_help=False)
base_parser.add_argument(
    '--log', help='Log level (info,debug,warn)', metavar='log-level',
    type=log_level, default='info')
base_parser.add_argument(
    '--report', metavar='report-file',
    help='Specify a file to write the compile report to',
    type=argparse.FileType('w'))
base_parser.add_argument(
    '--verbose', '-v', action='count', default=0,
    help='Increase verbosity of the output')
base_parser.add_argument(
    '--version', '-V', action='version', version=version_text,
    help='Display version and exit')


base2_parser = argparse.ArgumentParser(add_help=False)
base2_parser.add_argument(
    '--machine', '-m', help='target machine', required=True,
    choices=target_names)
base2_parser.add_argument(
    '--output', '-o', help='output file', metavar='output-file',
    type=argparse.FileType('w'), required=True)


class ColoredFormatter(logging.Formatter):
    """ Custom formatter that makes vt100 coloring to log messages """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    colors = {
        'INFO': WHITE,
        'WARNING': YELLOW,
        'ERROR': RED
    }

    def format(self, record):
        reset_seq = '\033[0m'
        color_seq = '\033[1;%dm'
        levelname = record.levelname
        msg = super().format(record)
        if levelname in self.colors:
            color = color_seq % (30 + self.colors[levelname])
            msg = color + msg + reset_seq
        return msg


build_description = """
Build utility. Use this to execute build files.
"""
build_parser = argparse.ArgumentParser(
    description=build_description, parents=[base_parser])
build_parser.add_argument(
    '-f', '--buildfile', metavar='build-file',
    help='use buildfile, otherwise build.xml is the default',
    default='build.xml')
build_parser.add_argument('targets', metavar='target', nargs='*')


def build(args=None):
    """ Run the build command from command line. Used by ppci-build.py """
    args = build_parser.parse_args(args)
    with LogSetup(args):
        api.construct(args.buildfile, args.targets)


c3c_description = """
C3 compiler. Use this compiler to produce object files from c3 sources and c3
includes. C3 includes have the same format as c3 source files, but do not
result in any code.
"""
c3c_parser = argparse.ArgumentParser(
    description=c3c_description, parents=[base_parser, base2_parser])
c3c_parser.add_argument(
    '-i', '--include', action='append', metavar='include',
    help='include file', default=[])
c3c_parser.add_argument(
    'sources', metavar='source', help='source file', nargs='+')


def c3c(args=None):
    """ Run c3 compile task """
    args = c3c_parser.parse_args(args)
    with LogSetup(args):
        # Compile sources:
        obj = api.c3c(args.sources, args.include, args.machine)

        # Write object file to disk:
        obj.save(args.output)
        args.output.close()


asm_description = """
Assembler utility.
"""
asm_parser = argparse.ArgumentParser(
    description=asm_description, parents=[base_parser, base2_parser])
asm_parser.add_argument(
    'sourcefile', type=argparse.FileType('r'),
    help='the source file to assemble')


def asm(args=None):
    """ Run asm from command line """
    args = asm_parser.parse_args(args)
    with LogSetup(args):
        # Assemble source:
        obj = api.asm(args.sourcefile, args.machine)

        # Write object file to disk:
        obj.save(args.output)
        args.output.close()

link_description = """
Linker. Use the linker to combine several object files and a memory layout
to produce another resulting object file with images.
"""
link_parser = argparse.ArgumentParser(
    description=link_description, parents=[base_parser, base2_parser])
link_parser.add_argument(
    'obj', type=argparse.FileType('r'), nargs='+',
    help='the object to link')
link_parser.add_argument(
    '--layout', '-L', help='memory layout', required=True,
    type=argparse.FileType('r'), metavar='layout-file')


def link(args=None):
    """ Run asm from command line """
    args = link_parser.parse_args(args)
    with LogSetup(args):
        obj = api.link(args.obj, args.layout, args.machine)
        obj.save(args.output)
        args.output.close()

objdump_description = """
Objdump utility to display the contents of object files.
"""
objdump_parser = argparse.ArgumentParser(
    description=objdump_description, parents=[base_parser])
objdump_parser.add_argument(
    'obj', help='object file', type=argparse.FileType('r'))


def objdump(args=None):
    """ Dump info of an object file """
    args = objdump_parser.parse_args(args)
    with LogSetup(args):
        obj = load_object(args.obj)
        args.obj.close()
        print_object(obj)

objcopy_description = """
Objcopy utility to manipulate object files.
"""
objcopy_parser = argparse.ArgumentParser(
    description=objcopy_description, parents=[base_parser])
objcopy_parser.add_argument(
    'input', help='input file', type=argparse.FileType('r'))
objcopy_parser.add_argument(
    '--segment', '-S', help='segment to copy', required=True)
objcopy_parser.add_argument(
    'output', help='output file')
objcopy_parser.add_argument(
    '--output-format', '-O', help='output file format')


def objcopy(args=None):
    """ Copy from binary format 1 to binary format 2 """
    args = objcopy_parser.parse_args(args)
    with LogSetup(args):
        # Read object from file:
        obj = load_object(args.input)
        args.input.close()
        api.objcopy(obj, args.segment, args.output_format, args.output)


def yacc_cmd(args=None):
    """
    Parser generator utility. This script can generate a python script from a
    grammar description.

    Invoke the script on a grammar specification file:

    .. code::

        $ ./yacc.py test.x -o test_parser.py

    And use the generated parser by deriving a user class:


    .. code::

        import test_parser
        class MyParser(test_parser.Parser):
            pass
        p = MyParser()
        p.parse()


    Alternatively you can load the parser on the fly:

    .. code::

        import yacc
        parser_mod = yacc.load_as_module('mygrammar.x')
        class MyParser(parser_mod.Parser):
            pass
        p = MyParser()
        p.parse()

    """
    parser = argparse.ArgumentParser(
        description='xacc compiler compiler', parents=[base_parser])
    parser.add_argument(
        'source', type=argparse.FileType('r'), help='the parser specification')
    parser.add_argument(
        '-o', '--output', type=argparse.FileType('w'), required=True)

    args = parser.parse_args(args)
    with LogSetup(args):
        transform(args.source, args.output)
        args.output.close()


def hex2int(s):
    if s.startswith('0x'):
        s = s[2:]
        return int(s, 16)
    raise ValueError('Hexadecimal value must begin with 0x')

hexutil_parser = argparse.ArgumentParser(
   description='hexfile manipulation tool by Windel Bouwman')
subparsers = hexutil_parser.add_subparsers(
    title='commands',
    description='possible commands', dest='command')

p = subparsers.add_parser('info', help='dump info about hexfile')
p.add_argument('hexfile', type=argparse.FileType('r'))

p = subparsers.add_parser('new', help='create a hexfile')
p.add_argument('hexfile', type=argparse.FileType('w'))
p.add_argument('address', type=hex2int, help="hex address of the data")
p.add_argument(
    'datafile', type=argparse.FileType('rb'), help='binary file to add')

p = subparsers.add_parser('merge', help='merge two hexfiles into a third')
p.add_argument('hexfile1', type=argparse.FileType('r'), help="hexfile 1")
p.add_argument('hexfile2', type=argparse.FileType('r'), help="hexfile 2")
p.add_argument(
    'rhexfile', type=argparse.FileType('w'), help="resulting hexfile")


def hexutil(args=None):
    args = hexutil_parser.parse_args(args)
    if not args.command:
        hexutil_parser.print_usage()
        sys.exit(1)

    if args.command == 'info':
        hexfile = HexFile.load(args.hexfile)
        hexfile.dump()
        args.hexfile.close()
    elif args.command == 'new':
        hexfile = HexFile()
        data = args.datafile.read()
        args.datafile.close()
        hexfile.add_region(args.address, data)
        hexfile.save(args.hexfile)
        args.hexfile.close()
    elif args.command == 'merge':
        # Load first hexfile:
        hexfile1 = HexFile.load(args.hexfile1)
        args.hexfile1.close()

        # Load second hexfile:
        hexfile2 = HexFile.load(args.hexfile2)
        args.hexfile2.close()

        hexfile = HexFile()
        hexfile.merge(hexfile1)
        hexfile.merge(hexfile2)
        hexfile.save(args.rhexfile)
        args.rhexfile.close()
    else:  # pragma: no cover
        raise NotImplementedError()


class LogSetup:
    """ Context manager that attaches logging to a snippet """
    def __init__(self, args):
        self.args = args
        self.console_handler = None
        self.file_handler = None
        self.logger = logging.getLogger()

    def __enter__(self):
        self.logger.setLevel(logging.DEBUG)
        self.console_handler = logging.StreamHandler()
        self.console_handler.setFormatter(ColoredFormatter(logformat))
        self.console_handler.setLevel(self.args.log)
        self.logger.addHandler(self.console_handler)

        if self.args.verbose > 0:
            self.console_handler.setLevel(logging.DEBUG)

        if self.args.report:
            self.file_handler = logging.StreamHandler(self.args.report)
            self.logger.addHandler(self.file_handler)
        self.logger.debug('Loggers attached')
        self.logger.info(version_text)

    def __exit__(self, exc_type, exc_value, traceback):
        # Check if a task error was raised:
        if isinstance(exc_value, TaskError):
            logging.getLogger().error(str(exc_value.msg))
            err = True
        else:
            err = False

        self.logger.debug('Removing loggers')
        if self.args.report:
            self.logger.removeHandler(self.file_handler)
            self.args.report.close()

        self.logger.removeHandler(self.console_handler)

        # exit code when error:
        if err:
            sys.exit(1)
