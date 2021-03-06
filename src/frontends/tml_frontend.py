import redbaron

from include.tensor import *
#from include.iterators import *
from include.loops import *
from include.program import *
from include.transformations import *
from src.backends.C_backend import *


import re
import subprocess
import copy
import sys


        
def process_assignmentnode(element, R_ARRAYS, V_ARRAYS, ITERATORS, LOOPS):
    """ For a given "element", depending on the array/iterator declaration
    mode, it will be processed and sorted as a physical array (R_ARRAY)
    or virtual array (V_ARRAY) """

    name = element.find("name").value
    asstype = element.find("atomtrailers").find("name").value
    params = element.find("atomtrailers").find_all("callargument")


    if asstype == "scalar":
        dtype = params[0].dumps()    
        scal = Tensor(name, dtype, None, None, None, asstype)
        R_ARRAYS.append(scal)

    if asstype == "tensorize":
        tmpparent = params[0].dumps()
        parent = None
        for t in R_ARRAYS:
            if t.name == tmpparent:
                parent = t

        tensor = Tensor(name, parent.dtype, ['1'], None, parent, asstype)
        R_ARRAYS.append(tensor)

        
    if asstype == "array" or\
       asstype == "zeros" or\
       asstype == "ones" or\
       asstype == "identity" or\
       asstype == "shift_lower" or\
       asstype == "shift_upper" or\
       asstype == "hilbert":
        
        """ A = array(dtype, [N, .., N]) """
        
        dtype = params[0].dumps()
        tmpshape = params[1].find("list").value
        shape = []

        ## Converting ListNode elements into simple strings
        for data in tmpshape:
            shape.append(data.dumps())
        
        tensor = Tensor(name, dtype, shape, None, None, asstype)

        if asstype != "array" and asstype != "zeros":
            tensor.set_init_value("1")
            tensor.set_init_type(asstype)
        elif asstype == "zeros":
            tensor.set_init_value("0")
            tensor.set_init_type(asstype)

        
        R_ARRAYS.append(tensor)

    if asstype == "add" or \
       asstype == "sub" or \
       asstype == "mul" or \
       asstype == "div" or \
       asstype == "vadd" or \
       asstype == "vsub" or \
       asstype == "vmul" or \
       asstype == "vdiv" or \
       asstype == "radd" or \
       asstype == "rsub" or \
       asstype == "rdiv" or \
       asstype == "rmul":
        
        t1 = params[0].dumps()
        t2 = params[1].dumps()


        acc1 = None
        acc2 = None

        accstore = []
        if asstype[0] != 'v':
            afout = params[-1].find("list").value
            for val in afout:
                accstore.append(val.dumps())
            
        ## Get accesses
        if len(params) > 2:
            afin = params[2].find("list").value
            acc1 = afin[0].value
        
            if len(afin) == 2:
                acc2 = afin[1].value

        nacc1 = []
        if acc1 != None:
            for val in acc1:
                nacc1.append(val.dumps())

        
        nacc2 = []

        if acc2 != None:
            for val in acc2:
                nacc2.append(val.dumps())
       
        for t in R_ARRAYS + V_ARRAYS:     
            if t1 == t.name:
                t1 = t
            if t2 == t.name:
                t2 = t

        dtype = t1.dtype
        expr = None
        op = asstype

        if asstype[0] == 'v':
            asstype[0] = ''
   
            #op = op.replace("v", "")
            
        if t1 in R_ARRAYS and t2 in R_ARRAYS:
            s1 = Subscript(t1, nacc1)
            s2 = Subscript(t2, nacc2)
            expr = Expression(op, s1, s2, None)

        if t1 in R_ARRAYS and t2 in V_ARRAYS:
            s1 = Subscript(t1, nacc1)
            expr = Expression(op, s1, t2.expr, None)

        if t1 in V_ARRAYS and t2 in R_ARRAYS:
            s2 = Subscript(t2, nacc1)
            expr = Expression(op, t1.expr, s2, None)

        if t1 in V_ARRAYS and t2 in V_ARRAYS:
            expr = Expression(op, t1.expr, t2.expr, None)


        if asstype[0] == "r":
            expr.is_reduced(True)
            
        tensor = Tensor(name, dtype, None, expr, None, asstype)
        
        store = Subscript(tensor, accstore)

        if asstype[0] == 'v':
            V_ARRAYS.append(tensor)
        else:
            tensor.expr.update_store(store)

            R_ARRAYS.append(tensor)
            tensor.infer_range()           
        
                
    
    
    """
    if asstype == "replicate":
        parentname = params[0].dumps()
        parent = None
        # Parent must exist
        # TODO: must clarify if we can replicate virtual arrays
        for par in R_ARRAYS + V_ARRAYS:
            if par.name == parentname:
                parent = par

        array = IvieArrayReplicate(name, parent)
        R_ARRAYS.append(array)
    """

    # if asstype == "transpose":
    #     parentname = params[0].dumps()
    #     rank1 = params[1].dumps()
    #     rank2 = params[2].dumps()
    #     parent = None
    #     for par in R_ARRAYS + V_ARRAYS:
    #         if par.name == parentname:
    #             parent = par

    #     array = IvieArrayTranspose(name, parent, rank1, rank2)
    #     R_ARRAYS.append(array)
        

    if asstype == "transpose" or\
       asstype == "vtranspose":
        parent = params[0].dumps()
        ranks = params[1].find("list").value

        nranks = []
        for i in range(0, len(ranks)):
            tmp_ = []
            tmp = ranks[i].find("list").value
            for j in range(0, len(tmp)):
                tmp_.append(tmp[j].find("int").dumps())
            nranks.append(tmp_)


        for t in R_ARRAYS:
            if t.name == parent:
                parent = t

        tshape = deepcopy(parent.shape)
        tshape = swap_rec(tshape, nranks, 0, len(nranks))

        sub = []
        for i in range(1, len(parent.shape)+1):
            sub.append("i"+str(i))


        toswap = deepcopy(sub)
        insub = Subscript(parent, swap_rec(toswap, nranks, 0, len(nranks)))
        expr = Expression(None, insub, None, None)
        if asstype == "vtranspose":
            expr = None
        
        tensor = Tensor(name, parent.dtype, tshape, expr, parent, asstype)
        tensor.vtranspose_ranks = nranks
        if asstype == "transpose":
            outsub = Subscript(tensor, sub)
            
            tensor.expr.update_store(outsub)

            R_ARRAYS.append(tensor)
        else:
            V_ARRAYS.append(tensor)

    if asstype == "entrywise_add" or\
       asstype == "entrywise_sub" or\
       asstype == "entrywise_mul" or\
       asstype == "entrywise_div" or\
       asstype == "ventrywise_add" or\
       asstype == "ventrywise_sub" or\
       asstype == "ventrywise_mul" or\
       asstype == "ventrywise_div":
        parent1 = params[0].dumps()
        parent2 = params[1].dumps()

        for t in R_ARRAYS + V_ARRAYS:
            if t.name == parent1:
                parent1 = t
            if t.name == parent2:
                parent2 = t

        op = None 
        if "ventrywise" in asstype:
            op = asstype.replace("ventrywise_", "")
        else:
            op = asstype.replace("entrywise_", "")

        expr = None
        sub1 = []
        sub2 = []
        for i in range(1, len(parent1.shape)+1):
            sub1.append("i"+ str(i))
        for i in range(1, len(parent2.shape)+1):
            sub2.append("i"+ str(i))
            
        # if t1 in R_ARRAYS and t2 in R_ARRAYS:
        #     aft1 = Subscript(t1, sub1)
        #     aft2 = Subscript(t2, sub2)
        #     expr = Expression(op, aft1, aft2, None)
        # if t1 in R_ARRAYS and t2 in V_ARRAYS:
        #     aft1 = Subscript(t1, sub1)
        #     expr = Expression(op, aft1, t2.expr, None)
        # if t1 in V_ARRAYS and t2 in R_ARRAYS:
        #     aft2 = Subscript(t2, sub2)
        #     expr = Expression(op, t1.expr, aft2, None)
        # if t1 in V_ARRAYS and t2 in V_ARRAYS:
        #     expr = Expression(op, t1.expr, t2.expr, None)



        leftop = None
        rightop = None

        if parent1 in R_ARRAYS:
            leftop = Subscript(parent1, sub1)
        if parent1 in V_ARRAYS:
            if parent1.construct == "vtranspose":
                toswap = deepcopy(sub1)
                nranks = parent1.vtranspose_ranks
                leftop = Subscript(parent1.parent, swap_rec(toswap, nranks, 0, len(nranks)))
            else:
                leftop = parent1.expr

        if parent2 in R_ARRAYS:
            rightop = Subscript(parent2, sub2)
        if parent2 in V_ARRAYS:
            if parent2.construct == "vtranspose":
                toswap = deepcopy(sub2)
                nranks = parent2.vtranspose_ranks
                rightop = Subscript(parent2.parent, swap_rec(toswap, nranks, 0, len(nranks)))
            else:
                rightop = parent2.expr

        expr = Expression("mul", leftop, rightop, None)
        
        
        tensor = Tensor(name, parent1.dtype, parent1.shape, expr, None, asstype)

        if "ventrywise" in asstype:
            V_ARRAYS.append(tensor)
        else:
            substore = []
            for i in range(1, len(parent1.shape)+1):
                substore.append("i"+str(i))
                
            store = Subscript(tensor, substore)
            tensor.expr.update_store(store)
            tensor.infer_range()
            R_ARRAYS.append(tensor)
            
        print tensor.debug_print()

    
    # if asstype == "ventrywise_add" or\
    #    asstype == "ventrywise_sub" or\
    #    asstype == "ventrywise_mul" or\
    #    asstype == "ventrywise_div":
    #     t1 = params[0].dumps()
    #     t2 = params[1].dumps()

    #     for t in R_ARRAYS + V_ARRAYS:
    #         if t.name == t1:
    #             t1 = t
    #         if t.name == t2:
    #             t2 = t

    #     op = asstype.replace("ventrywise_", "")
    #     expr = None
    #     if t1 in R_ARRAYS and t2 in R_ARRAYS:
    #         aft1 = Subscript(t1, range(1, len(t1.shape)+1))
    #         aft2 = Subscript(t2, range(1, len(t2.shape)+1))
    #         expr = Expression(op, aft1, aft2, None)
    #     if t1 in R_ARRAYS and t2 in V_ARRAYS:
    #         aft1 = Subscript(t1, range(1, len(t1.shape)+1))
    #         expr = Expression(op, aft1, t2.expr, None)
    #     if t1 in V_ARRAYS and t2 in R_ARRAYS:
    #         aft2 = Subscript(t2, range(1, len(t2.shape)+1))
    #         expr = Expression(op, t1.expr, aft2, None)
    #     if t1 in V_ARRAYS and t2 in V_ARRAYS:
    #         expr = Expression(op, t1.expr, t2.expr, None)
        
    #     tensor = Tensor(name, t1.dtype, t1.shape, expr, None, asstype)
    #     #store = Subscript(tensor, range(1, len(t1.shape)+1))
    #     #tensor.expr.update_store(store)
    #     V_ARRAYS.append(tensor)


        
    if asstype == "outerproduct":
        ts = params[0].find("list").value

        inputs = []
        for data in ts:
            t = data.find("name").value
            for tens in R_ARRAYS:
                if t == tens.name:
                    inputs.append(tens)

        subscripts = []
        outaccess = []
        offset = 1
        for inp in inputs:
            sub = []
            for i in range(offset, offset + len(inp.shape)):
                sub.append("i"+str(i))
            subscript = Subscript(inp, sub)
            subscripts.append(subscript)
            offset = offset + len(inp.shape)
            outaccess += subscript.access

        innerexpr = Expression("mul", subscripts[-2], subscripts[-1], None)

        expr = None
        for i in range(len(subscripts) - 3, -1, -1):
            expr = Expression("mul", subscripts[i], innerexpr, None)
            innerexpr = expr

        dtype = inputs[0].dtype
        shape = []
        for inp in inputs:
            shape += inp.shape

        tensor = Tensor(name, dtype, shape, innerexpr, None, asstype)
        store = Subscript(tensor, outaccess)
        tensor.expr.update_store(store)

        R_ARRAYS.append(tensor)

        #print tensor.debug_print()
        tensor.infer_range()

        
    # if asstype == "vtranspose":
    #     parentname = params[0].dumps()
    #     rank1 = params[1].dumps()
    #     rank2 = params[2].dumps()
    #     parent = None
    #     for par in R_ARRAYS + V_ARRAYS:
    #         if par.name == parentname:
    #             parent = par


    #     ### Update 08/11/17. I need to generate variants with 
    #     ### transpositions. One way of doing it is to 
    #     ### transform "vtranspose" instances into "transpose" instances.
    #     ### Here, the corresponding "build" is not systematically added to 
    #     ### the list of loops for a simple reason: LOOPS are normally not 
    #     ### including in the parameters of this function, so I don't want to 
    #     ### mess up with the function specification, and thus the entire code 
    #     ### in this file. Instead, I retrieve this loop elsewhere (the loop is 
    #     ### store in the self.loop attribute).
    #     ###
    #     ### This should not be done systematically. But for the immediate
    #     ### urge, I am doing it this way even if its hacky. 
    #     ### The following should be commented whenever desired.
        
    #     ### ------ Begin hack ------
    #     ## Creation of explicit copy
    #     array_ = IvieArrayTranspose(name, parent, rank1, rank2)
        
    #     ## Creation of iterators for transposition loop.
    #     sizes = parent.sizes
    #     nbdim = len(sizes)
    #     iterators = []
    #     for i in range(0, nbdim):
    #         tmpname = "i_"+name+"_"+str(i)
    #         it = IvieIteratorIterator(tmpname, str(0), sizes[i], str(1))
    #         iterators.append(it)
    #         ITERATORS.append(it)

    #     ## Creation of a build instruction
    #     ## DEPS and V_ARRAYS are useless here.
    #     ## I just let them in the parameters to avoid bugs.
    #     array_.build(iterators, [], V_ARRAYS)
    #     R_ARRAYS.append(array_)
    #     ### ------- End hack -------

    #     ### Uncomment the following to generate code with 
    #     ### vtransposes.
    #     #array = IvieArrayVtranspose(name, parent, rank1, rank2)
    #     #V_ARRAYS.append(array)
        
    # if asstype == "select": 
    #     pairs = []
    #     for cond in params:
    #         pair = cond.find("list").value
    #         condition = pair[0].dumps()
    #         array_ = pair[1].dumps()
    #         parent = None
    #         for par in R_ARRAYS + V_ARRAYS:
    #             if par.name == array_:
    #                 parent = par
    #                 pairs.append([condition, parent])
    #                 array = IvieArraySelect(name, pairs)
    #                 V_ARRAYS.append(array)



    if asstype == "contract" or\
       asstype == "vcontract":
        ### Tensor contraction
        ### T[i,j] = A[i,k] * B[j,k]
        parent1 = params[0].dumps()
        parent2 = params[1].dumps()
        _axes = params[2].find("list")
        
        for array in R_ARRAYS + V_ARRAYS:
            if array.name == parent1:
                parent1 = array
            if array.name == parent2:
                parent2 = array

        # flag1 = False
        # flag2 = False
        # for array in R_ARRAYS:
        #     if array.name == parent1:
        #         parent1 = array
        #         flag1 = True
        #     if array.name == parent2:
        #         parent2 = array
        #         flag2 = True

        # if flag1 == False:
        #     for array in V_ARRAYS:
        #         if array.name == parent1:
        #             parent1 = array.parent
        # if flag2 == False:
        #     for array in V_ARRAYS:
        #         if array.name == parent2:
        #             parent2 = array.parent
                    
        dtype = parent1.dtype
                
        axes1 = []
        axes2 = []
        if _axes[0].find("list") == None and _axes[1].find("list") == None:
            axes1.append(_axes[0].dumps())
            axes2.append(_axes[1].dumps())

        else:
            ## Multiple contractions
            for axe in _axes:
                axes1.append(axe[0].dumps())
                axes2.append(axe[1].dumps())
                        
        # print axes1
        # print axes2

        t1shape = []
        t2shape = []

        for i in range(0, len(parent1.shape)):
            if str(i+1) not in axes1:
                t1shape.append(parent1.shape[i])



        for i in range(0, len(parent2.shape)):
            if str(i+1) not in axes2:
                t2shape.append(parent2.shape[i])

        shape = t1shape + t2shape

        outsub = []
        for i in range(1, len(shape)+1):
            outsub.append("i"+str(i))

        red_axes = []
        for i in range(len(shape)+1, len(shape)+1 + len(_axes)):
            red_axes.append("i"+str(i))

        sub1 = [None] * len(parent1.shape)
        sub2 = [None] * len(parent2.shape)

        
        inc1 = 0
        for i in range(0, len(sub1)):
            if str(i+1) not in axes1:
                sub1[i] = outsub[inc1]
                inc1 += 1
    
        for i in range(0, len(sub2)):
            if str(i+1) not in axes2:
                sub2[i] = outsub[inc1]
                inc1 += 1

        inc1 = 0
        for red in red_axes:
            sub1[int(axes1[inc1])-1] = red
            sub2[int(axes2[inc1])-1] = red
            inc1 += 1



        expr = None

        leftop = None
        rightop = None

        if parent1 in R_ARRAYS:
            leftop = Subscript(parent1, sub1)
        if parent1 in V_ARRAYS:
            if parent1.construct == "vtranspose":
                toswap = deepcopy(sub1)
                nranks = parent1.vtranspose_ranks
                leftop = Subscript(parent1.parent, swap_rec(toswap, nranks, 0, len(nranks)))
            else:
                leftop = parent1.expr

        if parent2 in R_ARRAYS:
            rightop = Subscript(parent2, sub2)
        if parent2 in V_ARRAYS:
            if parent2.construct == "vtranspose":
                toswap = deepcopy(sub2)
                nranks = parent2.vtranspose_ranks
                rightop = Subscript(parent2.parent, swap_rec(toswap, nranks, 0, len(nranks)))
            else:
                rightop = parent2.expr

        expr = Expression("mul", leftop, rightop, None)
         
        # if parent1 in R_ARRAYS and parent2 in R_ARRAYS:
        #     s1 = Subscript(parent1, sub1)
        #     s2 = Subscript(parent2, sub2)
        #     expr = Expression("mul", s1, s2, None)
        # if parent1 in R_ARRAYS and parent2 in V_ARRAYS:
        #     s1 = Subscript(parent1, sub1)
        
        #     expr = Expression("mul", s1, parent2.expr, None)
        # if parent1 in V_ARRAYS and parent2 in R_ARRAYS:
        #     s2 = Subscript(parent2, sub2)
        #     expr = Expression("mul", parent1.expr, s2, None)
        # if parent1 in V_ARRAYS and parent2 in V_ARRAYS:
        #     expr = Expression("mul", parent1.expr, parent2.expr, None)
        
        expr.is_reduced("+")
        tensor = Tensor(name, dtype, shape, expr, None, asstype)

        # Here I actually need the outsubscript everytime
        store = Subscript(tensor, outsub)
        tensor.expr.update_store(store)
        if asstype == "contract":

            R_ARRAYS.append(tensor)
        if asstype == "vcontract":
            V_ARRAYS.append(tensor)

        print tensor.debug_print()

    if asstype == "scalar_add" or\
       asstype == "scalar_sub" or\
       asstype == "scalar_mul" or\
       asstype == "scalar_div":
        ### Scalar multiplication 
        ### T[i, j] = u * B[i, j]

        parent1 = params[0].dumps()
        parent2 = params[1].dumps()
        for array in R_ARRAYS + V_ARRAYS:
            if array.name == parent1:
                parent1 = array
            if array.name == parent2:
                parent2 = array

        sub1 = ["scalar"]            
        sub2 = range(1, len(parent2.shape)+1)

        s1 = Subscript(parent1, sub1)
        s2 = Subscript(parent2, sub2)
        op = asstype.replace("scalar_", "")
        expr = Expression(op, s1, s2, None)
                
        tensor = Tensor(name, parent2.dtype, parent2.shape, expr, None, asstype)
        store = Subscript(tensor, sub2)
        tensor.expr.update_store(store)
        R_ARRAYS.append(array)
        

    ## Test: Replicate for both iterators and arrays.
    ## Depending on the input of replicate, it will 
    ## either generate an array or an iterator.
    ## This will not change internal data structure. 

    # if asstype == "replicate":
    #     parentname = params[0].dumps()
    #     parent = None
    #     # Parent must exist
    #     # TODO: must clarify if we can replicate virtual arrays
    #     for par in R_ARRAYS + V_ARRAYS:
    #         if par.name == parentname:
    #             parent = par

    #     ## If parent is not NULL at this stage,
    #     ## then parent is an array. 
    #     if parent != None:
    #         array = IvieArrayReplicate(name, parent)
    #         R_ARRAYS.append(array)
    #     else:
    #         ## Otherwise, it is an iterator
    #         for it in ITERATORS:
    #             if it.name == parentname:
    #                 parent = it

    #         iterator = IvieIteratorReplicate(name, parent)
    #         ITERATORS.append(iterator)


    # # Handling iterators
    if asstype == "iterator":
        minbound = params[0].dumps()
        maxbound = params[1].dumps()
        stride = params[2].dumps()

        iterator = IvieIteratorIterator(name, minbound, maxbound, stride)
        ITERATORS.append(iterator)



    if asstype == "build":
        tensor = params[0].dumps()

        for t in R_ARRAYS:
            if t.name == tensor:
                tensor = t

        loop = tensor.build(name)

        LOOPS.append(loop)
        

    if asstype == "vectorize" or\
       asstype == "parallelize":
        lname = params[0].dumps()
        lr = int(params[1].dumps())
        sched = None
        paramtype = "VEC"
        if asstype == "parallelize":
            sched = params[2].dumps()
            paramtype = "THRD"

        loopin = None
        for l in LOOPS:
            if lname == l.label:
                loopin = l

        newloop = deepcopy(loopin)
        parallelize(newloop.loopnest, lr, paramtype, sched)
        newloop.label = name
        LOOPS.append(newloop)


    if asstype == "stripmine":
        
        lname = params[0].dumps()
        lr = int(params[1].dumps())
        factor = params[2].dumps()

        loopin = None
        for l in LOOPS:
            if lname == l.label:
              loopin = l

        newloop = deepcopy(loopin)
        print newloop.loopnest.debug_print()
        stripmine(newloop.loopnest, lr, factor)
        print newloop.loopnest.debug_print()

        newloop.label = name
        LOOPS.append(newloop)

    if asstype == "interchange":
        
        lname = params[0].dumps()
        ranks = params[1].find("list").value


        nranks = []
        for i in range(0, len(ranks)):
            tmp_ = []
            tmp = ranks[i].find("list").value
            for j in range(0, len(tmp)):
                tmp_.append(tmp[j].find("int").dumps())
            nranks.append(tmp_)

        loopin = None
        for l in LOOPS:
            if lname == l.label:
              loopin = l


        newloop = deepcopy(loopin)

        print newloop.loopnest.debug_print()

        for pair in nranks:
            i1 = None
            i2 = None
            r1 = min(int(pair[0]), int(pair[1]))
            r2 = max(int(pair[0]), int(pair[1]))
            i1 = get_iterator(loopin.loopnest, r1, i1)
            i2 = get_iterator(loopin.loopnest, r2, i2)

            ## I need to decoupled interchange from updating stmt
            ## because of messy recursion when handling both
            ## in the same function.
            interchange(newloop.loopnest, r1, r2, i1, i2)
            interchange_stmt(newloop.loopnest, r1, r2)

        print newloop.loopnest.debug_print()

        newloop.label = name
        LOOPS.append(newloop)

        

    if asstype == "fuse":
        l1 = params[0].dumps()
        l2 = params[1].dumps()
        lr = params[2].dumps()
        
        for l in LOOPS:
            if l1 == l.label:
                l1 = l
            if l2 == l.label:
                l2 = l

        tofuse = None
        tofuse = get_loop(l2.loopnest, int(lr), tofuse)
        newloop = deepcopy(l1)

        print newloop.loopnest.debug_print()
        fuse(newloop.loopnest, tofuse, int(lr))
        newloop.label = name
        
        print newloop.loopnest.debug_print()
        LOOPS.append(newloop)


    if asstype == "peel":
        ## I assume peeling at end of loop only.
        lname = params[0].dumps()
        lr = int(params[1].dumps())
        factor = int(params[2].dumps())


        loopin = None
        for l in LOOPS:
            if lname == l.label:
                loopin = l

        newloop = deepcopy(loopin)
        print newloop.loopnest.debug_print()
        peel(newloop.loopnest, lr, factor)

        newloop.label = name
        LOOPS.append(newloop)
        print newloop.loopnest.debug_print()
        
        
    if asstype == "unroll":
        lname = params[0].dumps()
        lr = int(params[1].dumps())
        factor = None
        if len(params) > 2:
            factor = int(params[2].dumps())

        
        loopin = None
        for l in LOOPS:
            if lname == l.label:
              loopin = l


        newloop = deepcopy(loopin)
        print newloop.loopnest.debug_print()
        
        unroll(newloop.loopnest, lr, factor)

        print newloop.loopnest.debug_print()
        newloop.label = name

        LOOPS.append(newloop)




        



# def process_placement_atomtrailersnode(element, R_ARRAYS):
#     """ Update memory placement of a given array.
#     This only applies to physical arrays. """

#     placement = element.value[1].dumps()
#     arrayname = element.value[0].dumps()
#     params = element.value[2].find_all("callargument")
    
#     for array in R_ARRAYS:
#         if array.name == arrayname:
#             if placement == "map_interleaved":
#                 array.set_interleaved(params[0])
#                 if placement == "map_onnode":
#                     array.set_onnode(params[0].dumps())


# def process_build_outerproduct(array, iterators):
#     print "coucou"

# def process_build_transpose(array, iterators, V_ARRAYS):
#     ### At = transpose(A, 1, 2)                                                                                                                            
#     ### ...                                                                                                                                               
#     ### build(At, [ta_1, ta_2])                                                                                                                            
#     ###                                                                                                                                      
#     ### must generate on of the following loops                                                                                             
#     ###       
#     ### Av = vtranspose(A, 1, 2)        
#     ### with ta_1 as siter:          
#     ###   with ta_2 as siter:        
#     ###     At[ta_1][ta_2] = _tr(Av[ta_1][ta_2])   
#     ###         
#     ###   OOR  
#     ###       
#     ### Av = vtranspose(At, 1, 2)                    
#     ### with ta_1 as siter:                         
#     ###   with ta_2 as siter:                      
#     ###     Av[ta_1][ta_2] = _tr(A[ta_1][ta_2])   
#     ###                                          
#     ### For the moment, we handle regular reads (option 2)                     
#     ### By default, iterators are set as permutable and parallel
    

#     ### TODO: fix bug when build is within loop. 
    
#     ### Create statement and innermost loop                                       

#     for iter_ in iterators:
#         iter_.set_kind("piter")
#         pos = iterators.index(iter_)
#         iter_.set_private_variables(iterators[pos:])
#         iter_.set_permutability(True)
        
#     source = array.parent
#     newvirt = IvieArrayVtranspose(array.name + "_t",  array, array.rank1, array.rank2)
#     V_ARRAYS.append(newvirt)
#     written = IvieArgument(newvirt, iterators, "")
#     ### Perte d'information pour les index complique!
#     read    = IvieArgument(array.parent, iterators, "")
#     statement = IvieStatement("_transpose" + array.name, written, [read])

#     innermost = IvieLoop(iterators[-1], [statement])
    
#     ### Build loop from innermost to outermost dimension                   
#     for i in range(len(iterators)-2, -1, -1):
#         innermost = IvieLoop(iterators[i], [innermost])
        
#     return innermost


# ## Experimental. How we do transformation needs to be clarified. 
def process_atomtrailersnode(prog, element, ITERATORS, SCHEDULER, STATEMENTS, V_ARRAYS, R_ARRAYS, LOOPS, DEPS):
    """ Adds each transformation in a scheduler. """
    
    name = element.value[0].dumps()
    params = element.value[1].find_all("callargument")

    #### Build is not a transformation, it just builds a loop
    #### for intermediate array construction, so that we may 
    #### be able to manipulate them afterwards. 
    #### The only reason it is in this is function is 
    #### because the syntax is basically the same as 
    #### that of transformations


    if name == "codegen":
        string = ""
        loops = params.find("list")
        max = 1
        for loo in loops:
            name = loo.dumps()
            for l in LOOPS:
                if l.label == name:
                    res = prettyprint_C_loop(l.loopnest, max)
                    string += res[0]


                    if res[1] > max:
                        max = res[1]

        prog.code.append(string)
        if max > prog.maxiter:
            prog.maxiter = max

    # if name == "init":
    #     tensors = params.find("list")
    #     tensors_ = []  
    #     for ten in tensors:
    #         name = ten.dumps()
    #         for t in R_ARRAYS:
    #             if t.name == name:
    #                 tensors_.append(t)
    #     prog.tensors = tensors_


    if name == "init":
        tensor = params[0].dumps()  
        for t in R_ARRAYS:
            if t.name == tensor:
                t.set_init_value(params[1].dumps())
                prog.tensors.append(t)
            if t.name != tensor and t.initvalue != None and\
               t not in prog.tensors:
                prog.tensors.append(t)

                
    if name == "alloc" or \
       name == "alloc_align" or \
       name == "alloc_interleaved" or \
       name == "alloc_onnode":
        tensor = params[0].dumps()

        attr = None
        if name == "alloc_onnode" or name == "alloc_align":
            attr = params[1].dumps()

        policy = None
        if name != "alloc":
            policy = name.replace("alloc_", "")
            
        for t in R_ARRAYS:
            if t.name == tensor:
                t.set_alloc_policy(policy)
                t.set_alloc_attribute(attr)

                
    if name == "__align":
        for arr in params:
            for array in R_ARRAYS:
                if array.name == arr.dumps():
                    array.align = True

    if name == "__simd_hints":
        for iter_ in params:
            for iterator in ITERATORS:
                if iterator.name == iter_.dumps():
                    iterator.vec_hints = True

    
                    
def process_FST(fst):
    """ Processing of FST to retrieve all informations.
    At this level of the FST, we encounter different Redbaron 
    data structures that correspond to the following:

    - AssignmentNode <==> Arrays and iterators declaration
    - AtomtrailersNode <==> Loop transformations (???)
    
    Returns an Program data structure containing the following
    informations:
    - Arrays (virtual and physical)
    - Loops """
    
    R_ARRAYS = []
    V_ARRAYS = []
    ITERATORS = []
    LOOPS = []
    SCHEDULER = []
    STATEMENTS = []
    ARGS = []
    ALL_DEPS = []
    mem_placement_constructs = ["map_onnode", "map_interleaved"]


    prog = Program([], [])
    for element in fst:
        if isinstance(element, redbaron.AssignmentNode):
            process_assignmentnode(element, R_ARRAYS, V_ARRAYS, ITERATORS, LOOPS)


        if isinstance(element, redbaron.AtomtrailersNode):
        #     ## For the moment, two types of atomtrailers:
        #     ## Those for memory placement, e.g, A.map_onnode(0)
        #     ## Those for loop transformation, e.g fuse(i1, i2)
        #     ## For each, the structure of .value is a bit different
        #     ## For memory placement, we make sure that .value[1] 
        #     ## is a memory placement construct such map_onnode, 
        #     ## or map_interleaved. Otherwise, it's loop transformation
        #     if element.value[1].dumps() in mem_placement_constructs:
        #         process_placement_atomtrailersnode(element, R_ARRAYS)
            #     else:
            process_atomtrailersnode(prog, element, ITERATORS, SCHEDULER, STATEMENTS, V_ARRAYS, R_ARRAYS, LOOPS, ALL_DEPS)
                

    ### This portion is related to loops generated by
    ### vtransposes transformed in to transpose (see lines 120--176).
    ### The loop is retrieved here since we LOOPS is a parameter of 
    ### function. 
    ### We add the loop at the beginning of LOOPS.
    ### In the C_backend file, I make sure that this loop
    ### will not be included in the mesh loop.

    ### ----- Begin hack ------
    # for array in R_ARRAYS:
    #     if array.__class__.__name__ == "IvieArrayTranspose":
    #         if array.loop != None:
    #             LOOPS.insert(0, array.loop)
    ### ----- End hack -------
    

    #return IvieProgram(R_ARRAYS, V_ARRAYS, ITERATORS, LOOPS, SCHEDULER, STATEMENTS, ALL_DEPS)
   
    return prog
