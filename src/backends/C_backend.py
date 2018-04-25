from include import *
from copy import deepcopy


def prettyprint_C_iterator(iterator):
    name = iterator.name
    minbound = iterator.minbound
    maxbound = iterator.maxbound
    stride = iterator.stride

    string = "for (" + name + " = " + minbound + "; " +\
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

    string += prettyprint_C_subscript(stmt.store)

    if flag == True:
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
    

def prettyprint_C_loop(loop):

    string = prettyprint_C_iterator(loop.iterator)
    string += " {\n"
    for bod in loop.body:
        if bod.__class__.__name__ == "Loop":
            string += prettyprint_C_loop(bod)
        else:
            string += prettyprint_C_statement(bod, True)
            string += ";\n"
    string += "}\n"

    return string
