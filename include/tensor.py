from copy import deepcopy, copy
from termcolor import colored
from utils import *


class Subscript():
    tensor = None
    access = None

    def __init__(self, tensor, access):
        self.tensor = tensor
        self.access = access

    def debug_print(self):
        string = self.tensor.name + "[" + str(self.access[0])
        for data in self.access[1:]:
            string += ', ' + str(data)
        string += ']'
        return string

class Expression():
    op = None
    left = None
    right = None

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def debug_print(self):
        # debugleft = None
        # debugright = None
        # if self.left != None:
        #     debugleft = self.left.debug_print()
        # if self.right != None:
        #     debugright = self.right.debug_print()
        # return "(" + self.op + ", " + debugleft + ", " + debugright + ")"
        tleft = None
        tright = None
        if self.left != None:
            tleft = self.left.debug_print()
        if self.right != None:
            tright = self.right.debug_print()
        return (self.op, tleft, tright)

class Tensor():
    dtype = None
    shape = None
    expr = None
    parent = None
    construct = None
    debug_str = None
    

    def __init__(self, name, dtype, shape, expr, parent, construct):
        self.name = name
        self.dtype = dtype
        self.shape = shape
        self.expr = expr
        self.parent = parent
        self.construct = construct


        if self.expr != None:
            print (self.dtype, self.name, self.shape, self.expr.debug_print(),\
                   self.parent, self.construct)

        
        def debug_print(self):
            return (self.dtype, self.name, self.shape,\
               lambda: self.expr.debug_print() if self.expr != None else None,\
               self.parent, self.construct)


    def build(self):
        # infer ranges
        # create and return loop
        pass
    
# class Array(Tensor):
    
#     def __init__(self, name, dtype, shape):
#         self.name = name
#         self.dtype = dtype
#         self.shape = shape


# class Scalar(Tensor):

#     def __init__(self, name, dtype):
#         self.name = name
#         self.dtype = dtype

# class Tensorize(Tensor):
    
#     def __init__(self, name, parent):
#         self.name = name
#         self.dtype = parent.dtype
#         self.shape = ['1']
#         self.parent = parent

# class Op(Tensor):

#     def __init__(self, name, expr):
#         self.name = name
#         self.expr = expr

# class Transpose(Tensor):
    
#     def __init__(self, name, parent, ranks):
#         self.name = name
#         self.parent = parent
#         self.dtype = parent.dtype
#         tmp_shape = deepcopy(parent.shape)
#         self.shape = swap_rec(tmp_shape, ranks, 0, len(ranks))


# class Entrywise(Tensor):

#     def __init__(self, name, parent1, parent2, expr):
#         self.name = name
#         self.dtype = parent1.dtype
#         self.shape = parent1.shape
#         self.expr = expr
        

# class Outerproduct(Tensor):

#     def __init__(self, name, dtype, shape, expr):
#         self.name = name
#         self.dtype = dtype
#         self.shape = shape
#         self.expr = expr


# class Contract(Tensor):

#         def __init__(self, name, parent1, parent2, axes1, axes2):
#         self.name = name
#         self.axes1 = axes1
#         self.axes2 = axes2
#         self.dtype = parent1.dtype

#         self.shape = parent1.shape 
        
#         self.dimension = str(int(self.parent1.dimension) + int(self.parent2.dimension) - len(axes1) - len(axes2))
#         self.reduction = True
       
#         for i in range(0, len(self.parent1.sizes)):
#             if str(i+1) not in self.axes1:
#                 self.sizes.append(parent1.sizes[i])
        
        
#         for i in range(0, len(self.parent2.sizes)):
#             if str(i+1) not in self.axes2:
#                 self.sizes.append(parent2.sizes[i])
  
        
