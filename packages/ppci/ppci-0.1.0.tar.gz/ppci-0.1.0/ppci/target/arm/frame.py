from ..target import Label, Alignment
from ..target import Frame, VCall
from .instructions import dcd, Add, Sub, Push, Pop, Mov, Mov2, Bl
from ..data_instructions import Db
from .instructions import RegisterSet
from .registers import R0, R1, R2, R3, R4, R5, R6, R7, R8
from .registers import R9, R10, R11, LR, PC, SP, ArmRegister, get_register


class ArmFrame(Frame):
    """ Arm specific frame for functions.

        ABI:
        pass arg1 in R1
        pass arg2 in R2
        pass arg3 in R3
        pass arg4 in R4
        return value in R0
        R5 and above are callee save (the function that is called
    """
    def __init__(self, name):
        super().__init__(name)
        # Allocatable registers:
        self.regs = [R0, R1, R2, R3, R4, R5, R6, R7]
        self.rv = R0
        self.p1 = R1
        self.p2 = R2
        self.p3 = R3
        self.p4 = R4
        self.fp = R11

        self.locVars = {}

        # Literal pool:
        self.constants = []
        self.literal_number = 0

    def new_virtual_register(self, twain=""):
        """ Retrieve a new virtual register """
        return super().new_virtual_register(ArmRegister, twain=twain)

    def gen_call(self, label, args, res_var):
        """ Generate code for call sequence. This function saves registers
            and moves arguments in the proper locations.

        """
        # TODO: what ABI to use?

        # Setup parameters:
        reg_uses = []
        for i, arg in enumerate(args):
            arg_loc = self.arg_loc(i)
            if isinstance(arg_loc, ArmRegister):
                reg_uses.append(arg_loc)
                self.move(arg_loc, arg)
            else:  # pragma: no cover
                raise NotImplementedError('Parameters in memory not impl')
        # self.emit(Bl(label, ))
        self.emit(
            VCall(label, extra_uses=reg_uses, extra_defs=[self.rv]))
        self.move(res_var, self.rv)

    def make_call(self, vcall):
        """ Implement actual call and save / restore live registers """
        # R0 is filled with return value, do not save it, it will conflict.
        # Now we now what variables are live:
        live_regs = self.live_regs_over(vcall)
        register_set = set(live_regs)

        # Caller save registers:
        if register_set:
            yield Push(RegisterSet(register_set))

        yield Bl(vcall.function_name)

        # Restore caller save registers:
        if register_set:
            yield Pop(RegisterSet(register_set))

    def get_register(self, color):
        return get_register(color)

    def move(self, dst, src):
        """ Generate a move from src to dst """
        self.emit(Mov2(dst, src, ismove=True))

    def arg_loc(self, pos):
        """
            Gets the function parameter location in IR-code format.
        """
        if pos == 0:
            return self.p1
        elif pos == 1:
            return self.p2
        elif pos == 2:
            return self.p3
        elif pos == 3:
            return self.p4
        else:  # pragma: no cover
            raise NotImplementedError('No more than 4 parameters implemented')

    def alloc_var(self, lvar, size):
        if lvar not in self.locVars:
            self.locVars[lvar] = self.stacksize
            self.stacksize = self.stacksize + size
        return self.locVars[lvar]

    def add_constant(self, value):
        """ Add constant literal to constant pool """
        for lab_name, val in self.constants:
            if value == val:
                return lab_name
        assert type(value) in [str, int, bytes], str(value)
        lab_name = '{}_literal_{}'.format(self.name, self.literal_number)
        self.literal_number += 1
        self.constants.append((lab_name, value))
        return lab_name

    def prologue(self):
        """ Returns prologue instruction sequence """
        # Label indication function:
        yield Label(self.name)
        yield Push(RegisterSet({LR, R11}))
        # Callee save registers:
        yield Push(RegisterSet({R5, R6, R7, R8, R9, R10}))
        if self.stacksize > 0:
            yield Sub(SP, SP, self.stacksize)  # Reserve stack space
        yield Mov(R11, SP)                 # Setup frame pointer

    def litpool(self):
        """ Generate instruction for the current literals """
        # Align at 4 bytes
        if self.constants:
            yield Alignment(4)

        # Add constant literals:
        while self.constants:
            label, value = self.constants.pop(0)
            yield Label(label)
            if isinstance(value, int) or isinstance(value, str):
                yield dcd(value)
            elif isinstance(value, bytes):
                for byte in value:
                    yield Db(byte)
                yield Alignment(4)   # Align at 4 bytes
            else:  # pragma: no cover
                raise NotImplementedError('Constant of type {}'.format(value))

    def between_blocks(self):
        for ins in self.litpool():
            self.emit(ins)

    def epilogue(self):
        """ Return epilogue sequence for a frame. Adjust frame pointer
            and add constant pool
        """
        if self.stacksize > 0:
            yield Add(SP, SP, self.stacksize)
        yield Pop(RegisterSet({R5, R6, R7, R8, R9, R10}))
        yield Pop(RegisterSet({PC, R11}), extra_uses=[self.rv])
        # Add final literal pool:
        for instruction in self.litpool():
            yield instruction
        yield Alignment(4)   # Align at 4 bytes
