import redbaron

from include.tensor import *
from include.iterators import *
from include.loops import *
from include.program import *
from include.transformations import *
import re
import subprocess
import copy
import sys


        
def process_assignmentnode(element, R_ARRAYS, V_ARRAYS, ITERATORS):
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
        

    if asstype == "array":
        """ A = array(dtype, [N, .., N]) """
        
        dtype = params[0].dumps()
        tmpshape = params[1].find("list").value
        shape = []

        ## Converting ListNode elements into simple strings
        for data in tmpshape:
            shape.append(data.dumps())
        
        tensor = Tensor(name, dtype, shape, None, None, asstype)
      
        R_ARRAYS.append(tensor)

    if asstype == "add" or \
       asstype == "sub" or \
       asstype == "mul" or \
       asstype == "div" or \
       asstype == "vadd" or \
       asstype == "vsub" or \
       asstype == "vmul" or \
       asstype == "vdiv":
        
        t1 = params[0].dumps()
        t2 = params[1].dumps()

        acc1 = None
        acc2 = None

        afout = params[-1].find("list").value
        accstore = []
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
        if "v" in op:
            op = op.replace("v", "")
            
        if t1 in R_ARRAYS and t2 in R_ARRAYS:
            s1 = Subscript(t1, nacc1)
            s2 = Subscript(t2, nacc2)
            expr = Expression(op, s1, s2, None)

        if t1 in R_ARRAYS and t2 in V_ARRAYS:
            s1 = Subscript(t1, nacc1)
            expr = Expression(op, s1, t2.expr, None)

        if t1 in V_ARRAYS and t2 in R_ARRAYS:
            s2 = Subscript(t2, nacc2)
            expr = Expression(op, t1.expr, s2, None)
            
        if t1 in V_ARRAYS and t2 in V_ARRAYS:
            expr = Expression(op, t1.expr, t2.expr, None)

        tensor = Tensor(name, dtype, None, expr, None, asstype)

        store = Subscript(tensor, accstore)

        if "v" in asstype:
            V_ARRAYS.append(tensor)
            print tensor.debug_print()
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
        

    if asstype == "transpose":
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
        
        sub = range(1, len(parent.shape)+1)

        insub = Subscript(parent, swap_rec(sub, nranks, 0, len(nranks)))
        outsub = Subscript(name, sub)
    
        expr = Expression(None, insub, None, None)
        
        tensor = Tensor(name, parent.dtype, tshape, expr, parent, asstype)
        tensor.expr.update_store(outsub)
        R_ARRAYS.append(tensor)


    if asstype == "entrywise_add" or\
       asstype == "entrywise_sub" or\
       asstype == "entrywise_mul" or\
       asstype == "entrywise_div" or\
       asstype == "ventrywise_add" or\
       asstype == "ventrywise_sub" or\
       asstype == "ventrywise_mul" or\
       asstype == "ventrywise_div":
        t1 = params[0].dumps()
        t2 = params[1].dumps()

        for t in R_ARRAYS + V_ARRAYS:
            if t.name == t1:
                t1 = t
            if t.name == t2:
                t2 = t

        op = None 
        if "ventrywise" in asstype:
            op = asstype.replace("ventrywise_", "")
        else:
            op = asstype.replace("entrywise_", "")

        expr = None
        if t1 in R_ARRAYS and t2 in R_ARRAYS:
            aft1 = Subscript(t1, range(1, len(t1.shape)+1))
            aft2 = Subscript(t2, range(1, len(t2.shape)+1))
            expr = Expression(op, aft1, aft2, None)
        if t1 in R_ARRAYS and t2 in V_ARRAYS:
            aft1 = Subscript(t1, range(1, len(t1.shape)+1))
            expr = Expression(op, aft1, t2.expr, None)
        if t1 in V_ARRAYS and t2 in R_ARRAYS:
            aft2 = Subscript(t2, range(1, len(t2.shape)+1))
            expr = Expression(op, t1.expr, aft2, None)
        if t1 in V_ARRAYS and t2 in V_ARRAYS:
            expr = Expression(op, t1.expr, t2.expr, None)
        
        tensor = Tensor(name, t1.dtype, t1.shape, expr, None, asstype)

        if "ventrywise" in asstype:
            V_ARRAYS.append(tensor)
        else:
            store = Subscript(tensor, range(1, len(t1.shape)+1))
            tensor.expr.update_store(store)
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
            subscript = Subscript(inp, range(offset, offset + len(inp.shape)))
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


        outsub = range(1, len(shape)+1)
        red_axes = range(len(shape)+1, len(shape)+1 + len(_axes))

        sub1 = [0] * len(parent1.shape)
        sub2 = [0] * len(parent2.shape)

        
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
        if parent1 in R_ARRAYS and parent2 in R_ARRAYS:
            s1 = Subscript(parent1, sub1)
            s2 = Subscript(parent2, sub2)
            expr = Expression("mul", s1, s2, None)
        if parent1 in R_ARRAYS and parent2 in V_ARRAYS:
            s1 = Subscript(parent1, sub1)
            expr = Expression("mul", s1, parent2.expr, None)
        if parent1 in V_ARRAYS and parent2 in R_ARRAYS:
            s2 = Subscript(parent2, sub2)
            expr = Expression("mul", parent1.expr, s2, None)
        if parent1 in V_ARRAYS and parent2 in V_ARRAYS:
            expr = Expression("mul", parent1.expr, parent2.expr, None)
        

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



# def process_withcontextitem(item, ITERATORS):
#     """ Processing of withcontextitemnode.
#     An iterator may be used in the different following forms:
    
#     (1) with perm _it_, _it2_ as _kind_
#     (2) with perm _it_ as _kind_, _it2_ as _kind_

#     Returns the iterator that is concerned, updated 
#     with dimension infos. """

#     iterators = None

#     for context in item:
#         ctxt = context.find("withcontextitem")
#         permutable = False
        
#         params = ctxt.find_all("name")

#         parallelism = None
#         schedule = None
#         privatevars = []
#         name = None
#         if "perm" in params[0].dumps():
#             permutable = True
#             name = params[0].dumps().replace("perm", "")
#         else:
#             name = params[0].dumps()
            
#         kind = params[1].dumps()
        
#         # TODO: raise error when piter has nothing specified
#         # TODO: allow schedule to specify an integer: because of "params = find_all("name")
#         #       if integer is used, it wont be taken into account
#         if kind == "piter":
#             infos = params[2:]
#             for i in range(0, len(infos)):
#                 info = infos[i].dumps()
#                 if info == "level":
#                     parallelism = infos[i+1].dumps()
#                 if info == "schedule":
#                     schedule = infos[i+1].dumps()
#                 if info == "private":
#                     for j in range(i+1, len(infos)):
#                         tmp_ = infos[j]
#                         if tmp_.dumps() == "schedule" or tmp_.dumps() == "level":
#                             break
#                         else:
#                             privatevars.append(tmp_.dumps())


#         # Search for iterators in the list        
#         for it in ITERATORS:
#             if name == it.name:
#                 it.set_permutability(permutable)
#                 it.set_kind(kind)
#                 it.set_parallelism(parallelism)
#                 it.set_schedule(schedule)
#                 it.set_private_variables(privatevars)
#                 iterators = it
                
#     return iterators


def process_argument(name, indexes, R_ARRAYS, V_ARRAYS, ITERATORS):
    """ Return an argument """
    
    store_array = None
    store_indexes = []
    string = ""

    for array in R_ARRAYS + V_ARRAYS:
        if array.name == name:
            store_array = array 
            string += array.name


            for index in indexes:
                for iterator in ITERATORS:
                    if index.find("name") != None:
                        if index.find("name").value == iterator.name:
                            string += "[" + iterator.name + "]"
                            store_indexes.append(iterator)
                            

    arg = IvieArgument(store_array, store_indexes, string)
    return arg
    
# def process_loop_assignmentnode(element, R_ARRAYS, V_ARRAYS, ITERATORS, STATEMENTS, ARGS, boolean):
#     """ We process assignementnode in loops, i.e 
#     statements, which is different from process_assignmentnode

#     Returns a statement """
#     # Written element
#     # .value is a list where first element is the name, and the following are indexes
    
#     store = element.target.value
#     name = store[0].dumps()
#     indexes = store[1:]
    
#     indexes_ = []
#     tmp_indexes = store[1:].find_all("name")
#     count = 0
#     for tmp in tmp_indexes:
#         for iterator in ITERATORS:
#             if iterator.name == tmp.dumps():
#                 count += 1
#                 indexes_.append(tmp)
                
#     written = None
#     if count == 1:
#         ## Dealing with regular function access
#         written = process_argument(name, indexes, R_ARRAYS, V_ARRAYS, ITERATORS)
#     else:
#         ## Otherwise access may involve multiple iterators.
#         written = process_argument(name, indexes_, R_ARRAYS, V_ARRAYS, ITERATORS)
#         written.set_indexes_dump(store[1:])
        

#     ARGS.append([written, 'W'])
#     # Function name
#     func_name = element.value.find("name").value

#     # Arguments
#     # .value is the list of all arguments
#     args = element.value.find("call").value
#     arguments = []
#     for arg in args:
#         # .value.value returns the name and the indexes as a list
#         infos = arg.value.value

#         name = None
#         indexes = []
#         argument = None
#         if isinstance(infos, str):
#             # This is when you have scalars.
#             # For flexibility, it's okay if there are scalar variables, but 
#             # uhm, this needs to be clarified
#             name = infos

#         else: # Otherwise, array elements are concerned
#             name = infos[0].dumps()
#             indexes = infos[1:]
            


#             indexes_ = []
#             tmp_indexes = infos[1:].find_all("name")
#             count = 0
#             for tmp in tmp_indexes:
#                 for iterator in ITERATORS:
#                     if iterator.name == tmp.dumps():
#                         count += 1
#                         indexes_.append(tmp)
                        
#             argument = None
#             if count == 1:
#                 ## Dealing with regular function access
#                 argument = process_argument(name, indexes, R_ARRAYS, V_ARRAYS, ITERATORS)
#             else:
#                 ## Otherwise access may involve multiple iterators.
#                 argument = process_argument(name, indexes_, R_ARRAYS, V_ARRAYS, ITERATORS)
#                 argument.set_indexes_dump(infos[1:])
                
#             #argument = process_argument(name, indexes, R_ARRAYS, V_ARRAYS, ITERATORS)
#             ARGS.append([argument, "R"])
#             arguments.append(argument)   

        


#     statement = IvieStatement(func_name, written, arguments)
#     statement.update_atomicity(boolean)
#     STATEMENTS.append(statement)

#     return statement
    
# def process_withnode(element, dimension, LOOPS, R_ARRAYS, V_ARRAYS, ITERATORS, STATEMENTS, ARGS, ALL_DEPS, boolean):
#     """ From a given WithNode, we create an IvieLoop. """


#     iters = element.contexts
#     content = element.value
#     iterators = process_withcontextitem(iters, ITERATORS)
#     body = []
#     DEPS = []

#     for bod in content:
#         if isinstance(bod, redbaron.AssignmentNode):
#             body.append(process_loop_assignmentnode(bod, R_ARRAYS, V_ARRAYS, ITERATORS, STATEMENTS,  ARGS, False))


#         if isinstance(bod, redbaron.WithNode):
#             body.append(process_withnode(bod, [], LOOPS, R_ARRAYS, V_ARRAYS, ITERATORS, STATEMENTS, ARGS, ALL_DEPS, False))

#     for bod in content:
#         if isinstance(bod, redbaron.AtomtrailersNode):
#             if bod.find("name").value == "atomic":
#                 body.append(process_loop_assignmentnode(bod.find("callnode").value[0], R_ARRAYS, V_ARRAYS, ITERATORS, STATEMENTS, True))
#             elif bod.find("name").value == "sync":
#                 body.append("sync")
#             elif bod.find("name").value == "build":
#                 params = bod.find("callnode").value
#                 array_ = params[0].dumps()
#                 iters = params[1].find("list").value
#                 its = []
#                 for array in V_ARRAYS + R_ARRAYS:
#                     if array.name == array_:
#                         array_ = array
                        
#                 for it in iters:
#                     for iterator in ITERATORS:
#                         if iterator.name == it.dumps():
#                             its.append(iterator)

#                 body.append(array_.build(its, DEPS, V_ARRAYS))
#             else:
#                 process_loop_atomtrailernode(bod, ARGS, DEPS)
                
                        

#     loop = IvieLoop(iterators, body)
#     loop.dependencies = DEPS
#     ALL_DEPS += DEPS
#     #loop.update_atomicity(boolean)
#     # Append loop only if outermost dimension
#     if dimension == None:
#         LOOPS.append(loop)
#     return loop

# def create_dependency(sink, source, condition, ARGS, DEPS, deptype):
#     for arg_sink in ARGS:
#         if arg_sink[0].string == sink:
#             for arg_source in ARGS:
#                 if arg_source[0].string == source:
#                     if deptype == "raw":
#                         if arg_sink[1] == "R" and arg_source[1] == "W":
#                             dependency = IvieDependency(deptype, arg_source[0], arg_sink[0], condition)
#                             DEPS.append(dependency)
#                     if deptype == "war":
#                         if arg_sink[1] == "W" and arg_source[1] == "R":
#                             dependency = IvieDependency(deptype, arg_source[0], arg_sink[0], condition)
#                             DEPS.append(dependency)
#                     if deptype == "rar":
#                         if arg_sink[1] == "R" and arg_source[1] == "R":
#                             dependency = IvieDependency(deptype, arg_source[0], arg_sink[0], condition)
#                             DEPS.append(dependency)
#                     if deptype == "waw":
#                         if arg_sink[1] == "W" and arg_source[1] == "W":
#                             dependency = IvieDependency(deptype, arg_source[0], arg_sink[0], condition)
#                             DEPS.append(dependency)
                                                    

# def process_loop_atomtrailernode(bod, ARGS, DEPS):
#     """ Handle specification of data dependencies. """
#     """ OR possible build construct. """

#     dep_constructs = ["__raw", "__waw", "__rar", "__war"]
    
#     sink = ""
#     sink += bod.value[0].dumps()
#     name = bod.value[0].dumps()
#     ## Retrieve index position of type of dep. this will help
#     ## retrieving sink indexes
#     for i in range(0, len(bod.value)):
#         if bod.value[i].dumps() in dep_constructs:
#             break
            
#     deptype = bod.value[i].dumps().replace("__","")
#     sources = bod.value[i+1].find_all("callargument")
#     sink_indexes_ = bod.value[1:i]
#     for i in range(0, len(sink_indexes_)):
#         sink += "[" + sink_indexes_[i].find("name").value + "]"
        
#     for data in sources:
#         if data.find("list") == None:
#             elt = sources.find("callargumentnode").value.value
#             source = elt.dumps()
#             create_dependency(sink, source, None, ARGS, DEPS, deptype)
#         else:
#             ## Then there are conditions
#             cond = data.find("list").value
#             source = cond[1].dumps()
#             condition = cond[0].dumps() ## At some point, I may need to work with objects instead of strings
#             create_dependency(sink, source, condition, ARGS, DEPS, deptype)


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
def process_transformation_atomtrailersnode(element, ITERATORS, SCHEDULER, STATEMENTS, V_ARRAYS, R_ARRAYS, LOOPS, DEPS):
    """ Adds each transformation in a scheduler. """
    
    name = element.value[0].dumps()
    params = element.value[1].find_all("callargument")

    #### Build is not a transformation, it just builds a loop
    #### for intermediate array construction, so that we may 
    #### be able to manipulate them afterwards. 
    #### The only reason it is in this is function is 
    #### because the syntax is basically the same as 
    #### that of transformations
    if name == "build":
        array_ = params[0].dumps()
        #iters = params[1].find("list").value

        iterators = []
        for array in V_ARRAYS + R_ARRAYS:
            if array.name == array_:
                array_ = array

        # for it in iters:
        #     for iterator in ITERATORS:
        #         if iterator.name == it.dumps():
        #             iterators.append(iterator)

        array_.build(iterators)

        ## DEPS useless here
        #LOOPS.append(array_.build(iterators, DEPS, V_ARRAYS))
        #print array_.name
        #array_.build(iterators)

    # if name == "build_outerproduct":
    #     array_ = params[0].dumps()
    #     iters = params[1].find("list").value
    #     for array in R_ARRAYS + V_ARRAYS:
    #         if array.name == array_:
    #             array_ = array

    #     iterators = []
    #     for it in iters:
    #         for iterator in ITERATORS:              
    #             if iterator.name == it.dumps():
    #                 iterators.append(iterator)
                    
    #     # V_ARRAYS useless here
    #     LOOPS.append(array_.build(iterators, DEPS, V_ARRAYS))
        

    # if name == "build_contraction":
    #     array_ = params[0].dumps()
    #     iters = params[1].find("list").value
    #     for array in R_ARRAYS:
    #         if array.name == array_:
    #             array_ = array

    #     iterators = []
    #     for it in iters:
    #         for iterator in ITERATORS:              
    #             if iterator.name == it.dumps():
    #                 iterators.append(iterator)

    #     LOOPS.append(array_.build(iterators, DEPS, V_ARRAYS))
      

    if name == "parallelize":
        iterator = params[0].dumps()
        type_ = params[1].dumps()
        schedule = params[2].dumps()
        private_vars = params[3].find("list")

        privates = []
        if private_vars != None:
            for var in private_vars.value:
                privates.append(var.dumps())


        for it in ITERATORS:
            if it.name == iterator:
                iterator = it

        if type_ == "None":
            type_ = None

        if schedule == "None":
            schedule = None
                
        transformation = IvieTransformationParallelize(iterator, type_, schedule, privates)
        SCHEDULER.append(transformation)



    if name == "reverse":
        rev = params[0].dumps()
        
        for iterator in ITERATORS:
            if iterator.name == rev:
                rev = iterator

        transformation = IvieTransformationReverse(rev)
        SCHEDULER.append(transformation)

    if name == "peel":
        peeled = params[0].dumps()
        factor_begin = params[1].dumps()
        factor_end = params[2].dumps()

        for iterator in ITERATORS:
            if iterator.name == peeled:
                if factor_begin != "None":
                    iterator.set_peel_begin_factor(factor_begin)
                if factor_end != "None":
                    iterator.set_peel_end_factor(factor_end)
                    
                peeled = iterator

        transformation = IvieTransformationPeel(peeled)
        
        SCHEDULER.append(transformation)

    """
    if name == "peel_begin" or name == "peel_end":
        peeled = params[0].dumps()
        factor = params[1].dumps()
     
        for iterator in ITERATORS:
            if iterator.name == peeled:
                print iterator.name
                iterator.set_peel_factor(factor)
                peeled = iterator

        offset = ""
        if "begin" in name:
            offset = "begin"
        else:
            offset = "end"

        transformation = IvieTransformationPeel(peeled, offset)
 
        SCHEDULER.append(transformation)

    """

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

    if name == "fuse":
        remaining = params[0].dumps()
        fused = params[1].dumps()

        remaining_iterator = None
        fused_iterator = None
        for iterator in ITERATORS:
            if iterator.name == remaining:
                remaining_iterator = iterator
            if iterator.name == fused:
                fused_iterator = iterator

        transformation = IvieTransformationFuse(remaining_iterator, fused_iterator)
        SCHEDULER.append(transformation)

    if name == "collapse": 
        remaining = params[0].dumps()
        collapsed = params[1].dumps()
        
        for iterator in ITERATORS:
            if iterator.name == remaining:
                remaining = iterator
            if iterator.name == collapsed:
                collapsed = iterator

        transformation = IvieTransformationCollapse(remaining, collapsed)
        SCHEDULER.append(transformation)

    if name == "tile":
        permutable_band = []
        ## What I understand is if permutable, then tilable
        ## If one of the iterators is not marked as permutable
        ## an error should be raised. 
        ## We collect the iterators, but we will raise legality
        ## errors when applying transformation. For the moment
        ## its just about building the data structure of the program
        for iter_ in params:
            for iterator in ITERATORS:
                if iterator.name == iter_.dumps():
                    permutable_band.append(iterator)

        
        transformation = IvieTransformationTile(permutable_band)
        SCHEDULER.append(transformation)


    if name == "stripmine":        
        iter_ = params[0].dumps()
        for iterator in ITERATORS:
            if iter_ == iterator.name:
                iter_ = iterator


        transformation = IvieTransformationStripmine(iter_)
        SCHEDULER.append(transformation)
        
    if name == "interchange":
        iter1 = params[0].dumps()
        iter2 = params[1].dumps()

        iterator1 = None
        iterator2 = None
        for iterator in ITERATORS:
            if iter1 == iterator.name:
                iterator1 = iterator
            if iter2 == iterator.name:
                iterator2 = iterator

        transformation = IvieTransformationInterchange(iterator1, iterator2)
        SCHEDULER.append(transformation)
        

    if name == "unroll" or name == "unroll_and_fuse":
        iter_name = params[0].dumps()
        if len(params) > 1:
            factor = params[1].dumps()
        else:
            factor = "-1"

        iter_ = None
        for iterator in ITERATORS:
            if iterator.name == iter_name:
                iterator.set_unroll_factor(factor)
                iter_ = iterator

        transformation = IvieTransformationUnroll(iter_)
        if name == "unroll_and_fuse":
            transformation.set_innerfuse()
        SCHEDULER.append(transformation)




    ## Experimental, not yet well defined.
    if name == "distribute":
        ## Comment: we specify the point from which 
        ## the distribution starts. 
        ## if necessary to distribute multiple times
        ## then consider composition of distributions (?)
        ## Also, do we instanciate new iterators for 
        ## all loop body structure ? 
        ## Update: For the moment, yes, we instanciate new 
        ## iterators, like in "clone"

        start = params[0].dumps()
        newloop = params[1].find("list")
        stmts = params[2].find("list")
        

        for iterator in ITERATORS:
            if iterator.name == start:
                start = iterator
                
        newloop_ =  []
        stmts_ = []
        for i in range(0, len(newloop)):
            for iterator in ITERATORS:
                if iterator.name == newloop[i].dumps() and iterator not in newloop_:
                    newloop_.append(iterator)

        ## Just collecting statement names for the moment
        for i in range(0, len(stmts)):
            stmts_.append(stmts[i].dumps())


        transformation = IvieTransformationDistribute(start, newloop_, stmts_)
        SCHEDULER.append(transformation)


#     # Experimental
#     if name == "clone":
#         clone = params[1].find("list")
#         cloned = params[0].dumps()

#         newloop = []

#         for iterator in ITERATORS:
#             if iterator.name == cloned:
#                 cloned = iterator
                
#         for i in range(0, len(clone)):
#             for iterator in ITERATORS:
#                 if iterator.name == clone[i].dumps() and iterator not in newloop:
#                     newloop.append(iterator)

#         transformation = IvieTransformationClone(cloned, newloop)
#         SCHEDULER.append(transformation)

#     if name == "purge":
#         purgeable = None
#         for it in ITERATORS:
#             if it.name == params[0].dumps():
#                 purgeable = it

#         transformation = IvieTransformationPurge(purgeable)
#         SCHEDULER.append(transformation)

#     # Experimental
#     if name == "replace_array":
#         dimension = params[0].dumps()
#         origin = params[1].dumps()
#         replacer = params[2].dumps()

#         for it in ITERATORS:
#             if it.name == dimension:
#                 dimension = it

#         for array in V_ARRAYS + R_ARRAYS:
#             if array.name == origin:
#                 origin = array

#             if array.name == replacer:
#                 replacer = array

#         transformation = IvieTransformationReplace(dimension, origin, replacer)
#         SCHEDULER.append(transformation)




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


    
    for element in fst:
        if isinstance(element, redbaron.AssignmentNode):
            process_assignmentnode(element, R_ARRAYS, V_ARRAYS, ITERATORS)


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
            process_transformation_atomtrailersnode(element, ITERATORS, SCHEDULER, STATEMENTS, V_ARRAYS, R_ARRAYS, LOOPS, ALL_DEPS)
                

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
    

    return IvieProgram(R_ARRAYS, V_ARRAYS, ITERATORS, LOOPS, SCHEDULER, STATEMENTS, ALL_DEPS)
