"""
    The process of instruction selection is preceeded by the creation of
    a selection dag (directed acyclic graph). The dagger take ir-code as
    input and produces such a dag for instruction selection.

    A DAG represents the logic (computation) of a single basic block.
"""

import logging
import re
from .. import ir
from ..target.isa import Register
from ..target.target import Label
from .selectiongraph import SGNode, SGValue, SelectionGraph
from ..utils.tree import Tree


NODE_ATTR = '$nodetype$$$'


def register(tp):
    """ Register a function for type tp """
    def reg_f(f):
        # f_map[tp] = f
        setattr(f, NODE_ATTR, tp)
        return f
    return reg_f


def make_op(op, vreg):
    typ = 'I{}'.format(vreg.bitsize)
    return '{}{}'.format(op, typ)


def make_map(cls):
    f_map = {}
    for name, func in list(cls.__dict__.items()):
        if hasattr(func, NODE_ATTR):
            tp = getattr(func, NODE_ATTR)
            f_map[tp] = func
    setattr(cls, 'f_map', f_map)
    return cls


def prepare_function_info(target, function_info, ir_function):
    """ Fill function info with labels for all basic blocks """
    # First define labels and phis:
    for ir_block in ir_function:
        # Put label into map:
        function_info.label_map[ir_block] = Label(ir.label_name(ir_block))

        # Create virtual registers for phi-nodes:
        for phi in ir_block.phis:
            vreg = function_info.frame.new_reg(
                target.get_reg_class(ty=phi.ty), twain=phi.name)
            function_info.phi_map[phi] = vreg


class FunctionInfo:
    """ Keeps track of global function data when generating code for part
    of a functions. """
    def __init__(self, frame):
        self.frame = frame
        self.value_map = {}  # mapping from ir-value to dag node
        self.label_map = {}
        self.phi_map = {}  # mapping from phi node to vreg
        self.block_roots = {}  # Mapping from block to root of block


@make_map
class SelectionGraphBuilder:
    def __init__(self, target):
        self.target = target
        self.logger = logging.getLogger('selection-graph-builder')
        self.postfix_map = {
            ir.i64: 'I64', ir.i32: "I32", ir.i16: "I16", ir.i8: 'I8'}
        self.postfix_map[ir.ptr] = 'I{}'.format(target.byte_sizes['ptr'] * 8)

    @register(ir.Jump)
    def do_jump(self, node):
        sgnode = self.new_node('JMP')
        sgnode.value = self.function_info.label_map[node.target]
        self.chain(sgnode)

    def make_opcode(self, opcode, typ):
        """ Generate typed opcode from opcode and type """
        return opcode + self.postfix_map[typ]

    def chain(self, sgnode):
        if self.current_token is not None:
            sgnode.add_input(self.current_token)
        self.current_token = sgnode.new_output('ctrl', kind=SGValue.CONTROL)

    def new_node(self, name, *args, value=None):
        """ Create a new selection graph node, and add it to the graph """
        sgnode = SGNode(name)
        sgnode.add_inputs(*args)
        sgnode.value = value
        sgnode.group = self.current_block
        self.sgraph.add_node(sgnode)
        return sgnode

    def add_map(self, node, sgvalue):
        assert isinstance(node, ir.Value)
        assert isinstance(sgvalue, SGValue)
        self.function_info.value_map[node] = sgvalue

    def get_value(self, node):
        return self.function_info.value_map[node]

    @register(ir.Return)
    def do_return(self, node):
        """ Move result into result register and jump to epilog """
        res = self.get_value(node.result)
        vreg = self.function_info.frame.rv
        opcode = self.make_opcode('MOV', node.result.ty)
        mov_node = self.new_node(opcode, res, value=vreg)
        self.chain(mov_node)

        # Jump to epilog:
        sgnode = self.new_node('JMP')
        sgnode.value = self.function_info.label_map[node.function.epilog]
        self.chain(sgnode)

    @register(ir.CJump)
    def do_cjump(self, node):
        """ Process conditional jump into dag """
        lhs = self.get_value(node.a)
        rhs = self.get_value(node.b)
        cond = node.cond
        sgnode = self.new_node('CJMP', lhs, rhs)
        sgnode.value = cond, self.function_info.label_map[node.lab_yes],\
            self.function_info.label_map[node.lab_no]
        self.chain(sgnode)

    @register(ir.Terminator)
    def do_terminator(self, node):
        sgnode = self.new_node('TRM')
        sgnode.add_input(self.current_token)

    @register(ir.Alloc)
    def do_alloc(self, node):
        # TODO: check alignment?
        fp = self.new_node(
            self.make_opcode("REG", ir.ptr),
            value=self.function_info.frame.fp)
        fp_output = fp.new_output('fp')
        offset = self.new_node(self.make_opcode("CONST", ir.ptr))
        offset.value = self.function_info.frame.alloc_var(node, node.amount)
        offset_output = offset.new_output('offset')
        sgnode = self.new_node(
            self.make_opcode('ADD', ir.ptr), fp_output, offset_output)
        self.chain(sgnode)
        self.add_map(node, sgnode.new_output('alloc'))

    def get_address(self, ir_address):
        """ Determine address for load or store. """
        if isinstance(ir_address, ir.Variable):
            # A global variable may be contained in another module
            # That is why it is created here, and not in the prepare step
            sgnode = self.new_node('LABEL', value=ir.label_name(ir_address))
            address = sgnode.new_output('address')
        else:
            address = self.get_value(ir_address)
        return address

    @register(ir.Load)
    def do_load(self, node):
        """ Create dag node for load operation """
        address = self.get_address(node.address)
        sgnode = self.new_node(self.make_opcode('LDR', node.ty), address)
        # Make sure a data dependence is added to this node
        self.chain(sgnode)
        self.add_map(node, sgnode.new_output(node.name))

    @register(ir.Store)
    def do_store(self, node):
        """ Create a DAG node for the store operation """
        address = self.get_address(node.address)
        value = self.get_value(node.value)
        opcode = self.make_opcode('STR', node.value.ty)
        sgnode = self.new_node(opcode, address, value)
        self.chain(sgnode)

    @register(ir.Const)
    def do_const(self, node):
        if isinstance(node.value, int):
            name = self.make_opcode('CONST', node.ty)
            value = node.value
        else:  # pragma: no cover
            raise NotImplementedError(str(type(node.value)))
        sgnode = self.new_node(name)
        sgnode.value = value
        self.add_map(node, sgnode.new_output(node.name))

    @register(ir.LiteralData)
    def do_literal_data(self, node):
        """ Literal data is stored after a label """
        label = self.function_info.frame.add_constant(node.data)
        sgnode = self.new_node('LABEL', value=label)
        self.add_map(node, sgnode.new_output(node.name))

    @register(ir.Binop)
    def do_binop(self, node):
        """ Visit a binary operator and create a DAG node """
        names = {'+': 'ADD', '-': 'SUB', '|': 'OR', '<<': 'SHL',
                 '*': 'MUL', '&': 'AND', '>>': 'SHR', '/': 'DIV',
                 '%': 'REM', '^': 'XOR'}
        op = self.make_opcode(names[node.operation], node.ty)
        a = self.get_value(node.a)
        b = self.get_value(node.b)
        sgnode = self.new_node(op, a, b)
        self.add_map(node, sgnode.new_output(node.name))

    @register(ir.Cast)
    def do_int_to_byte_cast(self, node):
        # TODO: add some logic here?
        value = self.get_value(node.src)
        self.add_map(node, value)

    @register(ir.Call)
    def do_call(self, node):
        # This is the moment to move all parameters to new temp registers.
        args = []
        inputs = []
        for argument in node.arguments:
            arg_val = self.get_value(argument)
            loc = self.function_info.frame.new_reg(
                self.target.value_classes[argument.ty])
            args.append(loc)
            opcode = self.make_opcode('MOV', argument.ty)
            arg_sgnode = self.new_node(opcode, arg_val, value=loc)
            self.chain(arg_sgnode)
            # inputs.append(arg_sgnode.new_output('x'))

        # New register for copy of result:
        ret_val = self.function_info.frame.new_reg(
            self.target.value_classes[node.ty], '{}_result'.format(node.name))

        # Perform the actual call:
        sgnode = self.new_node(
            'CALL', value=(node.function_name, args, ret_val))
        for i in inputs:
            sgnode.add_input(i)
        self.chain(sgnode)

        # When using the call as an expression, use copy of return value:
        output = sgnode.new_output('res')
        output.vreg = ret_val
        self.add_map(node, output)

    @register(ir.Phi)
    def do_phi(self, node):
        """ Refer to the correct copy of the phi node """
        vreg = self.function_info.phi_map[node]
        sgnode = self.new_node(self.make_opcode('REG', node.ty), value=vreg)
        output = sgnode.new_output(node.name)
        output.vreg = vreg
        self.add_map(node, output)

    def copy_phis_of_successors(self, ir_block):
        """ When a terminator instruction is encountered, handle the copy
        of phi values into the expected virtual register """
        # Copy values to phi nodes in other blocks:
        for succ_block in ir_block.successors:
            for phi in succ_block.phis:
                vreg = self.function_info.phi_map[phi]
                from_val = phi.get_value(ir_block)
                val = self.get_value(from_val)
                opcode = self.make_opcode('MOV', phi.ty)
                sgnode = self.new_node(opcode, val, value=vreg)
                self.chain(sgnode)

    def entry_block_special_case(self, function_info, ir_function):
        """ Copy arguments into new temporary registers """
        # TODO: maybe this can be done different
        # Copy parameters into fresh temporaries:
        for arg in ir_function.arguments:
            loc = function_info.frame.arg_loc(arg.num)
            # TODO: byte value are not always passed in byte registers..
            #
            tp_pf = 'REGI{}'.format(loc.bitsize)
            param_node = self.new_node(
                tp_pf,
                value=loc)
            assert isinstance(loc, Register)
            output = param_node.new_output(arg.name)
            vreg = function_info.frame.new_reg(
                self.target.value_classes[arg.ty], twain=arg.name)
            output.vreg = vreg
            self.chain(param_node)

            # When refering the paramater, use the copied value:
            self.add_map(arg, output)

    def block_to_sgraph(self, ir_block, function_info):
        """ Create dag (directed acyclic graph) from a basic block.
            The resulting dag can be used for instruction selection.
        """
        assert isinstance(ir_block, ir.Block)

        self.current_block = ir_block

        # Create start node:
        self.current_token = self.new_node('ENTRY').new_output(
            'token', kind=SGValue.CONTROL)

        # Emit extra dag for parameters when entry block:
        if ir_block is ir_block.function.entry:
            self.entry_block_special_case(function_info, ir_block.function)

        # Generate series of trees:
        for instruction in ir_block:
            # In case of last statement, first perform phi-lifting:
            if isinstance(instruction, ir.LastStatement):
                self.copy_phis_of_successors(ir_block)

            # Dispatch the handler depending on type:
            self.f_map[type(instruction)](self, instruction)

        # Create end node:
        sgnode = self.new_node('EXIT')
        sgnode.add_input(self.current_token)
        function_info.block_roots[ir_block] = sgnode

    def build(self, ir_function, function_info):
        """ Create a selection graph for the given function """
        self.sgraph = SelectionGraph()
        self.function_info = function_info

        # TODO: fix this total mess with vreg, block and chains:
        self.current_block = None

        # Create maps for global variables:
        for variable in ir_function.module.Variables:
            val = self.new_node('LABEL', value=ir.label_name(variable))
            self.add_map(variable, val.new_output(variable.name))

        # Create start node:
        self.current_token = self.new_node('ENTRY').new_output(
            'token', kind=SGValue.CONTROL)

        # Generate nodes for all blocks:
        for ir_block in ir_function:
            self.block_to_sgraph(ir_block, function_info)

        self.sgraph.check()
        return self.sgraph


class DagSplitter:
    """ Class that splits a DAG into a series of trees. This series is sorted
        such that data dependencies are met. The trees can henceforth be
        used to match trees.
    """
    def __init__(self, target):
        self.logger = logging.getLogger('dag-splitter')
        self.target = target

    def get_reg_class(self, data_flow):
        """ Determine the register class suited for this data flow line """
        op = data_flow.node.name
        if op == 'LABEL':
            return self.target.get_reg_class(ty=ir.ptr)
        assert 'I' in op
        bitsize = int(re.search('I(\d+)', op).group(1))
        return self.target.get_reg_class(bitsize=bitsize)

    def traverse_back(self, node):
        """
        Traverse the graph backwards from the given node, creating a tree
        and optionally adding this tree to the list of generated trees
        """

        # if node is already processed, stop:
        if node in self.node_map:
            return self.node_map[node]

        # Stop on entry node:
        if node.name == 'ENTRY':
            tree = Tree(node.name, value=node.value)
            self.node_map[node] = tree
            self.trees.append(tree)
            return tree

        # For now assert that nodes can only max 1 data value:
        assert len(node.data_outputs) <= 1

        # Make sure control dependencies are satisfied first:
        for inp in node.control_inputs:
            self.traverse_back(inp.node)

        # Second, process memory dependencies:
        for inp in node.memory_inputs:
            self.traverse_back(inp.node)

        # Create data for data dependencies:
        children = []
        for inp in node.data_inputs:
            if (inp.node.group is node.group) or \
                    (inp.node.group is None) or \
                    inp.node.name.startswith('CONST'):
                res = self.traverse_back(inp.node)
            else:
                if not inp.vreg:
                    cls = self.get_reg_class(inp)
                    vreg = self.frame.new_reg(cls, inp.name)
                    inp.vreg = vreg

            # If the input value has a vreg, use it:
            if inp.vreg:
                children.append(Tree(make_op('REG', inp.vreg), value=inp.vreg))
            else:
                children.append(res)

        # Create a tree node:
        tree = Tree(node.name, *children, value=node.value)

        # Determine if the node should be copied to register:
        for data_output in node.data_outputs:
            # Skip constants:
            if node.name.startswith('CONST'):
                continue

            # Check if value is used more then once:
            if (len(data_output.users) > 1) or node.volatile or \
                    any(u.group is not node.group for u in data_output.users):
                if not data_output.vreg:
                    cls = self.get_reg_class(data_output)
                    vreg = self.frame.new_reg(cls, data_output.name)
                    data_output.vreg = vreg

        # Handle outputs:
        if len(node.data_outputs) == 0:
            # If the tree was volatile, it must be emitted
            if node.volatile:
                self.trees.append(tree)
        else:
            # If the output has a vreg, put the value in:
            data_output = node.data_outputs[0]
            if data_output.vreg:
                vreg = data_output.vreg
                tree = Tree(make_op('MOV', vreg), tree, value=vreg)
                self.trees.append(tree)
                tree = Tree(make_op('REG', vreg), value=vreg)
            elif node.volatile:
                self.trees.append(tree)

        # Store for later and prevent multi coverage of dag:
        self.node_map[node] = tree

        return tree

    def split_dag(self, root, frame):
        """ Split dag into forest of trees.
            The approach here is to start at the exit of the flowgraph
            and go back to the beginning.

            This function can be looped over and yields a series
            of somehow topologically sorted trees.
        """
        self.trees = []
        self.node_map = {}
        self.frame = frame

        assert len(root.outputs) == 0

        # First determine the usages:
        self.traverse_back(root)

        return self.trees

