from pycparser import parse_file, c_ast, c_parser, c_generator
from redbaron import RedBaron
import re
import subprocess
import copy
import sys

"""
def generate_code_from_node(node):
    generator = c_generator.CGenerator()
    return generator.visit(node)


def process_statement(stmt):
""" """This functions extracts arguments from 
    a statement """ 
"""

    stmt = stmt.replace(" ", "")
    # Remove any operator
 
    tmp = re.sub('[+*-/=()<?:]', ' ', stmt)
 
    tmp = tmp.replace(";", "")
    tmp = tmp.split(" ")

    storarray = tmp[0]
    # clean list
    remarray = filter(lambda a: a != "", tmp[1:])
    return [storarray, remarray]
"""


def identify_object(block, i, iterators, dimension_infos, indent):
    iterator_paral_level = None
    iterator_private = None
    iterator_schedule = None

    dumpstring = c_generator.CGenerator()

    if isinstance(block, c_ast.Pragma):
        ## Supported Pragmas: OpenMP, simd.
        ## More can be added if needed
        if "omp" in block.string:
            iterator_paral_level = "THRD"
            if "private" in block.string:
                iterator_private = re.search(r'private(.*)', block.string).group(0)
            if "schedule" in block.string:
                pass
        if "simd" in block.string:
            iterator_paral_level = "VEC"

        dimension_infos[0] = iterator_paral_level
        dimension_infos[1] = iterator_private
        dimension_infos[2] = iterator_schedule
    
        
    if isinstance(block, c_ast.For):
        ## For loops
        
        ## Original iterator name
        iterator_old_name = block.init.lvalue.name
        
        ## Renaming for single assignment
        iterator_name = iterator_old_name + "_" + str(len(iterators))
        dimension_infos[5].append(iterator_old_name)
    
        
        ## Collecting minbound, maxbound and stride
        iterator_minbound = dumpstring.visit(block.init.rvalue)
        iterator_maxbound = dumpstring.visit(block.cond.right)
        iterator_stride = dumpstring.visit(block.next.rvalue)
        if isinstance(iterator_stride, c_ast.UnaryOp):
            iterator_stride = str(1)

        if len(iterators) > 0:
            # We break loop as soon as latest add is taken into account
            # otherwise, will replace with older iterators
            for i in range(len(iterators) -1, 0, -1):
                if iterators[i][1] in iterator_maxbound:
                    iterator_maxbound = iterator_maxbound.replace(iterators[i][1], iterators[i][2])
                    break 
            for i in range(len(iterators) -1, 0, -1):
                if iterators[i][1] in iterator_minbound:
                    iterator_minbound = iterator_minbound.replace(iterators[i][1], iterators[i][2])
                    break
        #iterator_maxbound = iterator_maxbound.replace("t", "t" + str(i))
        #iterator_minbound = iterator_minbound.replace("t", "t" + str(i))


        ## Building corresponding Ivie iterator declaration
        ivie_iterator = iterator_name + " = iterator(" 
        ivie_iterator += iterator_minbound + ", " + iterator_maxbound + ", "
        ivie_iterator += iterator_stride + ")\n"

        iterators.append([ivie_iterator, iterator_old_name, iterator_name])
        ivie_loop_dim = ""


        
        if dimension_infos[4] != None:
            ivie_loop_dim += dimension_infos[4]
      
        if indent == "":
            ivie_loop_dim += "\n"

        ## Building Ivie loop
        ivie_loop_dim += indent
        ivie_loop_dim += "with " + iterator_name + " as "
        if dimension_infos[0] == "THRD":
            ivie_loop_dim += "piter<level(THRD)"

            if dimension_infos[1] != None:
                ivie_loop_dim += ", " + dimension_infos[1]

            if dimension_infos[2] != None:
                ivie_loop_dim += ", schedule()"

            ivie_loop_dim += ">:\n"
        elif dimension_infos[0] == "VEC":
            ivie_loop_dim += "piter<level(VEC)>:\n"
        else:
            ivie_loop_dim += "siter:\n"
        indent += "  "
            
        # Reset and pass outer dimension for next dim
        dimension_infos[0] = None
        dimension_infos[1] = None
        dimension_infos[2] = None
        dimension_infos[4] = ivie_loop_dim
    

        identify_object(block.stmt, i, iterators, dimension_infos, indent)

    if isinstance(block, c_ast.If):
        ## In case we encounter if-statements.
        iterator_conditions = dumpstring.visit(block.cond)
        dimension_infos[3] = dumpstring.visit(block.cond)
      
        for j in range(0, len(block.iftrue.block_items)):
            block_ = block.iftrue.block_items[j]
            identify_object(block_, i, iterators, dimension_infos, indent)

        if block.iffalse != None:
            for j in range(0, len(block.iffalse.block_items)):
                block_ = block.iffalse.block_items[j]
                identify_object(block_, j, iterators, dimension_infos, indent)
       
    if isinstance(block, c_ast.Assignment):
        ## Managing assignments. In this part of the AST, assignments are 
        ## systematically loop statements
        if not isinstance(block.lvalue, c_ast.ID):
            asstring = dumpstring.visit(block)

            rvalue = dumpstring.visit(block.lvalue)
            list_lvalues = []
        

            tmp = block.rvalue
            while tmp.__class__.__name__ == "BinaryOp":
                list_lvalues.append(dumpstring.visit(tmp.right))
                tmp = tmp.left
            
            # Add last ArrayRef
            list_lvalues.append(dumpstring.visit(tmp))
          
            # If inductive variable, add it to lvalues
            if block.op == "+=":
                list_lvalues.append(rvalue)

            # Reverse so that order of arguments are correct ones
            list_lvalues.reverse()

            #   block.rvalue = block.rvalue.left.left
            #print dumpstring.visit(block.rvalue.left)
            #print generate_code_from_node(block.rvalue.left.left.left)
            #print asstring

            #res = process_statement(asstring)
            #ivie_statement = indent
            #ivie_statement += res[0]#.replace("t", "t" + str(i))
            #ivie_statement += " = f" + str(i) + "("  + res[1][0]#.replace("t", "t" + str(i))
            #for k in range(1, len(res[1])):
            #    ivie_statement += ", " + res[1][k]#.replace("t", "t" + str(i))
            #ivie_statement += ")\n"

            ivie_statement = indent
            ivie_statement += rvalue + " = f"
            ivie_statement += "(" + ", ".join(list_lvalues) + ")\n"

            if len(iterators) > 0:
                # We break loop as soon as latest add is taken into account
                # otherwise, will replace with older iterators
                firstinstance = []
                for i in range(len(iterators) -1, -1, -1):
                    if iterators[i][1] in ivie_statement and iterators[i][1] not in firstinstance:
                        ivie_statement = ivie_statement.replace(iterators[i][1], iterators[i][2])
                        firstinstance.append(iterators[i][1])

            dimension_infos[4] += ivie_statement
  

    if isinstance(block, c_ast.Compound):
        ## A compound corresponds to C blocks { }
        for j in range(0, len(block.block_items)):
            block_ = block.block_items[j]
            identify_object(block_, i, iterators, dimension_infos, indent)



def AST_to_Ivie(program, decls, filename):
    iterators = []
    declprint = ""
    
    ## Generate Ivie declarations
    ## Doing this with string processing 
    ## because I am lazy to parse it with
    ## pycparser.

    
    for dec in decls.split("\n"):
        if dec != "":
            ## Option 1: store these in data structures
            ## and do transformations before generating 
            ## final Ivie prog from which we call codegen
            ## Option 2: directly prettyprint corresponding
            ## Ivie string, then extend codegen with transformations
            ## Dunno yet what is better. Doing option 2 for the moment

            declprint += process_declaration(dec) + "\n"


    

    dimension_infos = [None, None, None, None, "\n", []]
    for i in range(0, len(program)):
        indent = ""
        block = program[i]
        
        identify_object(block, i, iterators, dimension_infos, indent)

    
    for it in iterators:
        print it[0]

    print dimension_infos[4]
    
    if filename != None:
        with open(filename, "w") as source:
            source.write(declprint)
            source.write("\n")
            for it in iterators:
                source.write(it[0])
         
            source.write(dimension_infos[4])




