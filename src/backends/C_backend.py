""" Generate C code from data structures """

from include import *
from copy import deepcopy

def get_last_physical_parent(array, parent, permcumul):
    physicals = ["IvieArrayTranspose", "IvieArrayArray",
                 "IvieArrayReplicate", "IvieArrayIntermediate", 
                 "IvieArrayOuterproduct", "IvieArrayContraction",
                 "IvieArrayEntrywise"]

    if array.parent.__class__.__name__ in physicals and parent == []:
        parent.append(array.parent)
    else:
        if array.parent.__class__.__name__ == "IvieArrayVtranspose":
            permcumul.append([array.parent.rank1, array.parent.rank2])
        parent.append(get_last_physical_parent(array.parent, parent, permcumul))

    return parent

def prettyprint_C_declaration(array):
    datatype = None
    sizes = None
    name = None
    """
    if array.__class__.__name__ != "IvieArrayArray":
        datatype = array.parent.datatype
        sizes = array.parent.sizes
    else:
        datatype = array.datatype
        sizes = array.sizes

    """
    ## Static arrays
    """
    string = array.datatype + " " + array.name
    if len(array.sizes) == int(array.dimension):
        for size in array.sizes:
            string += "[" + size + "]"
    else:
s        string += "[" + array.sizes[0]
        for size in array.sizes[1:]:
            string += "*" + size
        string += "]"
        
    string += ";\n"
    """
    ## Pointers
    string  = array.datatype 
    for i in range(0, len(array.sizes)):
        string += "*"
    string += array.name + ";\n"


    return string



def prettyprint_CFD_C_declaration(array):
    #string = array.datatype + " *" + array.name + ";\n"
  
    if array.cfdmesh == True:
        string = array.datatype + " " + array.name + "[216]"
        for i in range(0, len(array.sizes)):
            string += "[" + array.sizes[i] + "]"
    else:
        if array.sizes != []:
            string = array.datatype + " " + array.name + "[" + array.sizes[0] + "]"
            for i in range(1, len(array.sizes)):
                string += "[" + array.sizes[i] + "]"
        else:
            string = array.datatype + " " + array.name

    if array.align==True:
        string += " __attribute__((aligned(64)))"
    string += ";\n"
    return string

def prettyprint_C_allocation(array):
    string = ""
    if array.interleaved != None:
        string = array.name + " = numa_alloc_interleaved(" +  array.interleaved + ");\n"
    elif array.onnode != None:
        string = array.name + " = numa_alloc_onnode(" +  array.onnode + ");\n"     

    if array.interleaved == None and array.onnode == None:
        string = array.name + " = malloc(N * sizeof * " + array.name \
                + " * (N * (N * sizeof ** " + array.name + ")));\n"
        string += "int * const data"+array.name + " = " + array.name + " + N;\n"
        string += "for (tt1 = 0; tt1 < N; tt1++)\n " + array.name + \
                  "[tt1] = data"+ array.name + " + tt1 * N;\n"


    ## Dumb initialization for testing
    it = "tt" 
    count = 1
    tmp = []

    for size in array.sizes:
        iter = it + str(count)
        tmp.append(iter)
        string += "for (" + iter + " = 0; " + iter + " < " + size + "; " + iter + " +=1)\n"
        count += 1

    string += array.name 

    for t in tmp:
        string += "[" + t + "]"
 
    if array.name != "C":
        string += " = tt1 + tt2;\n"
    else:
        string += "= 0;\n"
    """
    if array.interleaved == None and array.onnode == None:
        string = array.name + " = malloc(N" 
        for i in array.sizes[1:]:
            string += "*N"
        string += "*sizeof(" + array.datatype + "));\n"
    ## Dumb initialization for testing
    it = "tt" 
    count = 1
    tmp = []

    for size in array.sizes:
        iter = it + str(count)
        tmp.append(iter)
        string += "for (" + iter + " = 0; " + iter + " < " + size + "; " + iter + " +=1)\n"
        count += 1

    string += array.name 

    string += "[" 
    
    o = 0
    for i in range(0, len(tmp)-1):
        string += tmp[i] 
        string += " + N *("
        o = i
    string += tmp[o] 
    for i in range(0, len(tmp)-1):
        string += ")"


    string += "]"

    tmps = ["tmp1", "tmp2", "v"]
    if array.name in tmps:
        string += " = 0;\n\n"
    else:
        string += " = " + tmp[0]
        for t in tmp[1:]:
            string += " - " + t 
        string += ";\n\n"

    """
    return string


def prettyprint_C_loop(loop, depth, iters, indent):
    
    string = indent        
    parallinfo = ""
    """
    if loop.iterators.__class__.__name__ != "IvieIteratorTile":
        ## Avoiding to rename iterator tile just to make things 
        ## easier for the moment
        iterator = "i" + depth
        if iterator not in iters:
            iters.append(iterator)
        ## redefining iterator name for final printing
        loop.iterators.name = iterator

    else:
    """
    iterator = loop.iterators.name
    iters.append(iterator)
 
    if loop.iterators.kind == "piter":
        if loop.iterators.parallelism == "PROC":
            ## Initialiation and 
            ## Opening loop iterating over procs
            parallinfo += "int ierr, proc, nbprocs, idproc;\n"
            parallinfo += "ierr = MPI_Comm_rank(MPI_COMM_WORLD, &idproc);\n"
            parallinfo += "ierr = MPI_Comm_rank(MPI_COMM_WORLD, &nbprocs);\n\n"

            parallinfo += "for (proc = 0; proc <= nbprocs; proc++) {\n"
        if loop.iterators.parallelism == "THRD":
            parallinfo += "#pragma omp parallel for " 
            if loop.iterators.private_variables != None and \
               loop.iterators.private_variables != []:
                parallinfo += "private("
                for pri in loop.iterators.private_variables[:-1]:
                    parallinfo += pri + ","  
                parallinfo += loop.iterators.private_variables[len(loop.iterators.private_variables)-1]
                parallinfo += ") "


            if loop.iterators.schedule != None:
                parallinfo += "schedule(static, " + loop.iterators.schedule + ")"
            parallinfo += "\n"
        
        if loop.iterators.vec_hints == True:
            parallinfo += "#pragma ivdep\n#pragma vector always" + indent
        parallinfo += "\n"

        if loop.iterators.parallelism == "VEC":
            ### Test
            #parallinfo += "#pragma ivdep\n#pragma vector always\n" + indent
            parallinfo += "#pragma ivdep\n#pragma vector always" + indent
            
    ### In case there is peeling before loop
    for stmt in loop.outer_pre_statements:
        string += prettyprint_C_statement(stmt, indent)
        
    string += parallinfo
 
    string += "for(" + iterator + " = " + loop.iterators.minbound + "; " 
        
    if loop.iterators.reversed == True:
        string += iterator + " > " + loop.iterators.maxbound + "; "
        string += iterator + " -= " + loop.iterators.stride 
    else:
        string += iterator + " < " + loop.iterators.maxbound + "; "
        string += iterator + " += " + loop.iterators.stride

    string += ") {\n"

        
    for data in loop.outer_pre:
        if data.__class__.__name__ == "IvieStatement":
            string += prettyprint_C_statement(data, indent)
        if data.__class__.__name__ == "IvieLoop":
            string += prettyprint_C_loop(data, str(int(depth)), iters, indent)
        
        
    for bod in loop.body:
        if bod.__class__.__name__ == "IvieLoop":
            string += prettyprint_C_loop(bod, str(int(depth) + 1), iters, indent + " ")
        else:
            
            string += prettyprint_C_statement(bod, indent + " ")

    for data in loop.outer_post:
        if data.__class__.__name__ == "IvieStatement":
            string += prettyprint_C_statement(data, indent)
        if data.__class__.__name__ == "IvieLoop":
            string += prettyprint_C_loop(data, str(int(depth)), iters, indent)


    indent += " "

    string += indent + "}\n"

    if loop.iterators.parallelism == "PROC":
        #Closing loop iterating over procs
        string += indent + "}\n ierr = MPI_finalize();\n\n"

    return string
        


def prettyprint_C_statement(statement, indent):
    string = ""

    if statement.atomic == True:
        string += "#pragma omp atomic\n"
    
    string += indent + prettyprint_C_argument(statement.store)

    if statement.store.array.__class__.__name__ == "IvieArrayEntrywise" and statement.store.array.type == "add":
        op = " + "
    else:
        op = " * "

    if statement.store.array.reduction == True:
        red = " += "
    else:
        red = " = "

    if statement.args != []:
        string += red + prettyprint_C_argument(statement.args[0])
        for arg in statement.args[1:]:
            ### Print * only for CFD.
            string +=  op + prettyprint_C_argument(arg)
            #string += " * " + prettyprint_C_argument(statement.args[len(statement.args)-1])
        string += ";\n"
    return string


def prettyprint_C_argument(argument):
    string = ""

    local_indexes = None
    ## This local_indexes variable is used to apply the interchange of 
    ## indexes for VTranspose on a local copy instead of the original 
    ## data structure (otherwise, this interchange will be spread 
    ## in every access function that involves the interchanged indexes.
    ## If not a case of VTranspose, local_indexes is set to the default
    ## argument.indexes.

    if argument.array.__class__.__name__ == "IvieArrayVtranspose":
        parent = []
        permcumul = []
        parent = get_last_physical_parent(argument.array, parent, permcumul)[0]
        string += parent.name
 

        ## Exchange indexes to restore view
        ## Take into cumulation of permutations if existing
        ## from oldest to latest (last element of permcumul to first element due to recursion)
        local_indexes = deepcopy(argument.indexes)
        for cumul in permcumul:
            tmp = local_indexes[int(cumul[0])-1]
            tmp2 = local_indexes[int(cumul[1])-1]
            local_indexes[int(cumul[1])-1] = tmp
            local_indexes[int(cumul[0])-1] = tmp2
        tmp = local_indexes[int(argument.array.rank1)-1]
        tmp2 = local_indexes[int(argument.array.rank2)-1]

        local_indexes[int(argument.array.rank2)-1] = tmp
        local_indexes[int(argument.array.rank1)-1] = tmp2
    else:
        string += argument.array.name
        local_indexes = argument.indexes

    #if int(argument.array.dimension) != len(argument.array.sizes):
    ## Then it means some dimensions must be flattened
    ## For CFD, it does not matter, we know that we want 
    ## one-dimensional arrays. 
    """
    string += "["
        
    for i in range(0, len(local_indexes)-1):            
        if local_indexes[i].garbage == False:
            string += local_indexes[i].name 
            if local_indexes[i+1].garbage == False or \
               local_indexes[i+1].garbage == True and i+1 <= len(local_indexes)-2:
                string += " * (" + local_indexes[i].maxbound + ") + ("
        
    if local_indexes[i+1].garbage == False:
        string += local_indexes[i+1].name 
    for i in range(0, len(local_indexes)-1):
        if local_indexes[i+1].garbage == False:
            string += ")"
    string += "]"
    """
    #else:
    ## Otherwise, do regular printing

  
    for index in local_indexes:
        if index.garbage == False:
            ### This is for CFD, to prevent 
            ### from printing iterators that 
            ### where collapsed
            string += "[" + index.name + "]"

    
    return string


def prettyprint_CFD_C(ivieprog):
    ### Prettyprinting only for CFD
    ### - All arrays are pointers 
    ### - Access functions are "flattened"
    ### - Computations are multiplications only


    string = "int main(int *argc, char **argv) { int N = atoi(argv[1]);\n\n"
    ### temporary

    string += "int tt1, tt2, tt3, tt4, tt5;\n"
    ### 
    for array in ivieprog.virtual_arrays:
        array.dimension = "1"

    for array in ivieprog.physical_arrays:
        array.dimension = "1" 
        #string += prettyprint_CFD_C_declaration(array)
        string += prettyprint_C_declarations(array)
    string += "\n"
        
    for array in ivieprog.physical_arrays:
        string += prettyprint_C_allocation(array)

    core = ""
    """
    with open("init.txt", "r") as init:
        core += init.read()
    """
    iters = []
    core += "double begin = omp_get_wtime();\n"
    for loop in ivieprog.loops:
        depth = 1
        indent = ""
        core += prettyprint_C_loop(loop, str(depth), iters, indent)
    core += "double end = omp_get_wtime();\nprintf(\"Time: %f ms\\n\", end-begin);"
    string += "int "
    for it in iters[:-1]:
        string += it + ", "
    string += iters[len(iters)-1] + ";\n\n" + core 

    with open("verif.txt", "r") as verif:
        string += verif.read()
        
    string += "\nreturn 0;\n}\n"
        
    return string
    

def prettyprint_C(ivieprog):
    string = "int main() {\n\n"
    ### temporary

    string += "int tt1, tt2, tt3, tt4, e;\n"
    ###
    
    for array in ivieprog.physical_arrays:
        #string += prettyprint_C_declaration(array)
        string += prettyprint_CFD_C_declaration(array)
        

    string += "\n"
    """
    for array in ivieprog.physical_arrays:
        string += prettyprint_C_allocation(array)
    """
    core = ""
    
    init_ = ""
    # with open("init.txt", "r") as init:
    #     init_ += init.read()
    
    iters = []
    outofmesh = ""
    init_ += "\ndouble begin = omp_get_wtime();\n"
    core += "for (e = 0; e < 216; e++) {\n"
    for loop in ivieprog.loops:
        depth = 1
        indent = ""
        if loop.flag_not_in_mesh == True:
            outofmesh += prettyprint_C_loop(loop, str(depth), iters, indent)
        else:
            core += prettyprint_C_loop(loop, str(depth), iters, indent)
    core += "}\n"
    core += "double end = omp_get_wtime();\nprintf(\"Time: %f ms\\n\", end-begin);"

    ## Hacky.
    core = core.replace("* u", "* u[e]").replace("v", "v[e]").replace("v[e]ector", "vector").replace("iv[e]dep", "ivdep")
    core = core.replace("tmp1", "tmp1[e]").replace("tmp2", "tmp2[e]").replace("tmp3", "tmp3[e]").replace("tmp4", "tmp4[e]").replace("tmp5", "tmp5[e]").replace("tmp6", "tmp6[e]")
    string += "int "
    for it in iters[:-1]:
        string += it + ", "
    string += iters[len(iters)-1] + ";\n\n" + init_ + outofmesh + core 

    """
    with open("verif.txt", "r") as verif:
        string += verif.read()
    """
    string += "\nreturn 0;\n}\n"


        
    return string
