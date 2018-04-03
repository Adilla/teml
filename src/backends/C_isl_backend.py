from islpy import *
from islpy import _isl


def set_statements(ast, ivieprog):
    """ Program generated with isl have statements 
    in the form of S(i, j). We need to replace these
    by the actual statements. """

    ### BROKEN 

    #print ast.for_get_body()
    try:
        children = ast.block_get_children()
        n = children.n_ast_node()
    except _isl.Error:
        body = ast.for_get_body()
        print ast.for_get_iterator()
        print ast.for_get_init()
        print ast.for_get_cond()
        print ast.for_get_inc()
    """
    for i in range(0, n):
        local_ast = children.get_ast_node(i)
        print i
        try:
            local_ast.block_get_children()
        except _isl.Error:
            print local_ast.for_get_body()
        else:
            set_statements(local_ast, ivieprog)
    """



def generate_C_from_AST(ast):
    p = Printer.to_str(ast.get_ctx())
    p = p.set_output_format(format.C)
    p = p.print_ast_node(ast)    
 
    #print ast.block_get_children().get_ast_node(1).for_get_body()
    print(p.get_str())



def build_AST(ivieprog):
    isl_schedules = ivieprog.isl_loop_schedules_str
    isl_domains = ivieprog.isl_loop_domains

    """
    for sched in isl_schedules:
        print sched

    for dom in isl_domains:
        print dom
    """
    
    contxt = Set("{ : }")
    build = AstBuild.from_context(contxt)
    ast = build.node_from_schedule_map(UnionMap(ivieprog.isl_program))
    
    #ast = None
    #print ast
    return ast


def backend(ivieprog):
    ast = build_AST(ivieprog)
    set_statements(ast, ivieprog)
    print generate_C_from_AST(ast)
    
    

