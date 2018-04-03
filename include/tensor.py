from copy import deepcopy, copy
from termcolor import colored
from utils import *



class Subscript():
    tensor = None
    access = None

    def __init__(self, tensor, access):
        self.tensor = tensor
        self.access = access

class Expression():
    op = None
    subscript1 = None
    subscript2 = None

    def __init__(self, op, subscript1, subscript2):
        self.op = op
        self.subscript1 = subscript1
        self.subscript2 = subscript2
    
    

class Tensor():
    dtype = None
    shape = None
    expr = None
    parent = None
    debug_str = None

    def debug_print(self):
        return debug_str

    
class Array(Tensor):
    
    def __init__(self, name, dtype, shape):
        self.name = name
        self.dtype = dtype
        self.shape = shape


class Scalar(Tensor):

    def __init__(self, name, dtype):
        self.name = name
        self.dtype = dtype

class Tensorize(Tensor):
    
    def __init__(self, name, parent):
        self.name = name
        self.dtype = parent.dtype
        self.shape = ['1']
        self.parent = parent

class Op(Tensor):

    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class Transpose(Tensor):

    def __init__(self, name, parent, ranks):
        self.name = name
        self.parent = parent
        self.dtype = parent.dtype
        self.expr = parent.expr

          
        tmp_shape = deepcopy(parent.shape)
        self.shape = swap_rec(tmp_shape, ranks, 0, len(ranks))

        print parent.shape
        print self.shape
