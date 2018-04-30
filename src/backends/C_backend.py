from include import *
from copy import deepcopy


def prettyprint_C_iterator(iterator):
    name = iterator.name
    minbound = iterator.minbound
    maxbound = iterator.maxbound
    stride = iterator.stride
    paraltype = iterator.parallelism
    paralsched = iterator.schedule
    
    string = ""
    if paraltype == "THRD":
        string += "#pragma omp parallel for "
        if paralsched != None:
            string += "schedule(static," + paralsched + ") "
            ## Still need to collect private vars..
        string += "\n"
    elif paraltype == "VEC":
        string += "#pragma ivdep\n#pragma vector always\n"
    string += "for (" + name + " = " + minbound + "; " +\
             name + " <= " + maxbound + "; " + \
             name + " += " + stride + ") "

    return string

def prettyprint_C_subscript(subs):
    string = subs.tensor.name

    for acc in subs.access:
        string += "[" + str(acc) + "]"

    return string

def prettyprint_C_statement(stmt, flag):
    string = ""

    if flag == True:
        ## Flag to know when to print lhv and =
        string += prettyprint_C_subscript(stmt.store)
  
        if stmt.reduced == True:
            if stmt.op == "add":
                string += " += "
            if stmt.op == "sub":
                string += " -= "
            if stmt.op == "mul":
                string += " *= "
            if stmt.op == "div":
                string += " /= "
        else:
            string += " = "

    if stmt.left.__class__.__name__ == "Expression":
        string += prettyprint_C_statement(stmt.left, False)
    else:
        string += prettyprint_C_subscript(stmt.left)

    if stmt.op == "add":
        string += " + "
    elif stmt.op == "sub":
        string += " - "
    elif stmt.op == "mul":
        string += " * "
    else:
        string += " / "
        
    if stmt.right.__class__.__name__ == "Expression":
        string += prettyprint_C_statement(stmt.right, False)
    else:
        string += prettyprint_C_subscript(stmt.right)

    return string
    

def prettyprint_C_loop(loop, max):
    if loop.iterator.rank > max:
        max = loop.iterator.rank
 
    string = prettyprint_C_iterator(loop.iterator)
    string += " {\n"
    for bod in loop.body:
        if bod.__class__.__name__ == "Loop":
            string += prettyprint_C_loop(bod, max)[0]
        else:
            string += prettyprint_C_statement(bod, True)
            string += ";\n"
    string += "}\n"
    
    return [string, max]
