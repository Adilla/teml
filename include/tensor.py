from copy import deepcopy, copy
from termcolor import colored

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


