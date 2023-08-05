"""
    Entry point when building c3 sources.
"""

import logging
import collections
from ..common import CompilerError
from .lexer import Lexer
from .parser import Parser
from .codegenerator import CodeGenerator
from .scope import Context, SemanticError
from ..irutils import Verifier
from ..opt.mem2reg import Mem2RegPromotor


class Builder:
    """
        Generates IR-code from c3 source.
        Reports errors to the diagnostics system.
    """
    def __init__(self, diag, target):
        self.logger = logging.getLogger('c3')
        self.diag = diag
        self.lexer = Lexer(diag)
        self.parser = Parser(diag)
        self.codegen = CodeGenerator(diag)
        self.verifier = Verifier()
        self.target = target

    def build(self, srcs, imps=(), return_context=False):
        """ Create IR-code from sources. Raises compiler error when something
            goes wrong. Returns a list of ir-code modules.
        """
        assert isinstance(srcs, collections.Iterable)
        assert isinstance(imps, collections.Iterable)
        self.logger.debug('Building {} source files'.format(len(srcs)))
        self.logger.debug('Using {} includes'.format(len(imps)))

        # Create a context where the modules can live:
        context = Context(self.target)

        # Phase 1: Lexing and parsing stage
        for src in srcs:
            self.do_parse(src, context)
        for src in imps:
            self.do_parse(src, context)

        # Phase 1.8: Handle imports:
        self.logger.debug('Resolving imports')
        try:
            for mod in context.modules:
                for imp in mod.imports:
                    if context.has_module(imp):
                        if mod.innerScope.has_symbol(imp):
                            raise SemanticError("Redefine of {}".format(imp))
                        mod.innerScope.add_symbol(context.get_module(imp))
                    else:
                        msg = 'Cannot import {}'.format(imp)
                        raise SemanticError(msg)
        except SemanticError as ex:
            self.diag.error(ex.msg, ex.loc)
            raise

        # Phase 1.9
        for module in context.modules:
            self.codegen.gen_globals(module, context)

        # Phase 2: Generate intermediate code
        # Only return ircode when everything is OK
        ir_modules = []
        for pkg in context.modules:
            ir_modules.append(self.codegen.gencode(pkg, context))

        # Hack to check for undefined variables:
        try:
            for ir_module in ir_modules:
                self.check_control_flow(ir_module)
        except CompilerError as ex:
            self.diag.error(ex.msg, ex.loc)
            raise

        self.logger.debug('C3 build complete!')
        if return_context:
            return ir_modules, context
        else:
            return ir_modules

    def check_control_flow(self, ir_module):
        pas = Mem2RegPromotor()
        pas.run(ir_module)
        self.verifier.verify(ir_module)

    def do_parse(self, src, context):
        """ Lexing and parsing stage (phase 1) """
        tokens = self.lexer.lex(src)
        self.parser.parse_source(tokens, context)
