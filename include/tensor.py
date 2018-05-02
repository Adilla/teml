from copy import deepcopy, copy
from termcolor import colored
from utils import *
import subprocess
from loops import *

class Subscript():
    tensor = None
    access = None

    def __init__(self, tensor, access):
        self.tensor = tensor
        self.access = access

    def debug_print(self):
        string = self.tensor.name + "["
        if self.access != []:
            string += str(self.access[0])
        
            for data in self.access[1:]:
                string += ', ' + str(data)
        string += ']'
        return string

class Expression():
    op = None
    left = None
    right = None
    store = None
    ranks = None
    reduced = False

    
    def __init__(self, op, left, right, store):
        self.op = op
        self.left = left
        self.right = right
        self.store = store

    def update_store(self, store):
        self.store = store

    def update_ranks(self, ranks):
        self.ranks = ranks

    def is_reduced(self, bool):
        self.reduced = bool
        
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
        tstore = None
        if self.left != None:
            tleft = self.left.debug_print()
        if self.right != None:
            tright = self.right.debug_print()
        if self.store != None:
            tstore = self.store.debug_print()
        return (tstore, self.op, tleft, tright)

class Tensor():
    dtype = None
    shape = None
    expr = None
    parent = None
    construct = None
    debug_str = None
    loopdomain = None
    loop = None
    initvalue = None
    inittype = None
    allocpolicy = None
    allocattribute = None

    def __init__(self, name, dtype, shape, expr, parent, construct):
        self.name = name
        self.dtype = dtype
        self.shape = shape
        self.expr = expr
        self.parent = parent
        self.construct = construct
    
        """
        if self.expr != None:
            print (self.dtype, self.name, self.shape, self.expr.debug_print(),\
                   self.parent, self.construct)
        """
            
    def debug_print(self):
        if self.expr != None:
            print (self.dtype, self.name, self.shape, self.expr.debug_print(),\
                   self.parent, self.construct)

    def set_init_value(self, val):
        self.initvalue = val

    def set_init_type(self, type):
        self.inittype = type

    def set_alloc_policy(self, policy):
        self.allocpolicy = policy

    def set_alloc_attribute(self, attr):
        self.allocattribute = attr

    def infer_range(self):
        ## Infer range of output tensor.
       

        if self.expr != None:
            # Collect constraints
            # in string format for ISCC
            constraints = []
            indexes = []

            
            constraints = collect_constraints(constraints, indexes, self.expr)

            indexes = ", ".join(indexes)
            indexes = "S[" + indexes + "]"
            constraints = " and ".join(constraints)
            constraints = "C := { " + indexes + ": " + constraints + " };\n"
            outsub = ", ".join(self.expr.store.access)
            write = self.name + "[" + outsub + "]"
            # Build relation with output tensor
            relation = "W := { " + indexes + " -> " + write + "} * C;\n"
            irange = "R := ran W;\n"
            domain = "D := dom W;\n"
            lexmax = "L := lexmax R;\n"
            result = "print D;\nprint L;\n"
            iscc_script = constraints + relation + irange + domain + lexmax + result

            with open("_script.iscc", "w") as source:
                source.write(iscc_script)

            # I don't know why the following does not work
            #rrange = subprocess.call(['~/Tools/barvinok-0.41/iscc', '<', '_script.iscc'])
            # I will generate a sh file containing the command
            with open("_bscript.sh", "w") as source:
                command = "~/Tools/barvinok-0.41/iscc < _script.iscc"
                source.write(command)

            rrange = subprocess.check_output(["zsh", "_bscript.sh"])


            
            res = rrange.split("\n")
            
            domain = res[0].split(":")
            domain = domain[1].replace(" }", "")
            domain = domain.split(" and ")


            iterranges = []

            for dom in domain:
                # To switch to ranks
                dom = dom.replace("i", "")

                r = dom.replace(" ", "").split("<=")
                r[1] = int(r[1])
                
                iterranges.append(r)
        
            self.loopdomain = iterranges

            # clean up
            del res[-1]

            # processing resulting shape
            rrange = res[1].replace(self.name, "").\
                     replace("{ ", "").\
                     replace(" }", "").\
                     replace("\n", "").\
                     replace("[", "").\
                     replace("]", "").\
                     split(", ")


            for i in range(0, len(rrange)):
                rrange[i] = int(rrange[i]) + 1
                rrange[i] = str(rrange[i])

            self.shape = rrange


    def build(self, label):
        
        # Sorting to make it easier
        # x[1] corresponds to the rank
        # print sorted(self.loopdomain, key=lambda x: x[1])
        iterators = []
        if self.loopdomain == None:
            ### It means that this tensor is the result
            ### of a high level operation
            self.infer_range()
        self.loopdomain = sorted(self.loopdomain, key=lambda x: x[1])
        for it in self.loopdomain:
            #Strict domain
            #iterr = Iterator(it[1], it[0], it[2], '1')

            #But for the moment, we assume
            #iterators to start from 0
        
            iterr = Iterator(it[1], '0', it[2], '1')
            iterators.append(iterr)
        
        innermost = Loop(iterators[-1], [self.expr])

        for i in range(len(iterators)-2, -1, -1):
            innermost = Loop(iterators[i], [innermost])
        #self.loop = innermost
        #self.loop.debug_print()

        self.loop = LoopBox(label, innermost)
        return self.loop

        
        
