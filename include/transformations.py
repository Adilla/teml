from copy import deepcopy, copy
from termcolor import colored
import sys


from include.arrays import *
from include.iterators import *
from include.loops import *
from include.program import *
from include.transformations import *

class IvieTransformationCollapse():
    def __init__(self, remaining, collapsed):
        self.remaining = remaining
        self.collapsed = collapsed

    def search_body(self, body, outer):
        if body.iterators.name == self.collapsed.name:
            #print outer.body[0].debug_print()
            #print body.body[0].debug_print()
            outer.body = body.body
        else:
            for bod in body.body:
                if bod.__class__.__name__== "IvieLoop":
                    self.search_body(bod, body)
    

    def apply_transformation(self, ivieprog):
        ### Update remaining iterator and delete 
        ### collapsed one
        new = self.remaining.maxbound + " * " + \
              self.collapsed.maxbound

        self.remaining.update_maxbound(new)
        self.collapsed.mark_as_garbage()

        ### Basically when collapsing, you 
        ### can only collapse two consecutive 
        ### dimensions. So we are going to 
        ### search for remaining iterator and update 
        ### its body. Access functions are handled
        ### when prettyprinting for the moment
      
        body = None
        for loop in ivieprog.loops:
            ### Collapsed iterator cannot be outermost dimension anyway..
            for bod in loop.body:
                if bod.__class__.__name__ == "IvieLoop":
                    self.search_body(bod, loop)

def peel(loop, rank, factor):
    if rank-1 >= 1:
        if loop.iterator.rank == rank-1:
            newb = None
            for bod in loop.body:
                if bod.__class__.__name__ == "Loop":
                    if bod.iterator.rank == rank:
                        mbound = int(bod.iterator.maxbound)
                        bod.iterator.maxbound = str(int(bod.iterator.maxbound) - factor)
                        newb = peeloff(bod.body, rank, mbound, factor)
            loop.body += newb
        else:
            for bod in loop.body:
                if bod.__class__.__name__ == "Loop":
                    peel(bod, rank, factor)

    else:
        mbound = int(loop.iterator.maxbound)
        loop.iterator.maxbound = str(int(loop.iterator.maxbound) - factor)
        newb = peeloff(loop.body, rank, mbound, factor)
                        
        loop.outer_post_statements += newb
   

def peeloff(body, rank, maxbound, factor):
    peeled = []
    for bod in body:
        if bod.__class__.__name__ != "Loop":
            for i in range(factor-1, -1, -1):
                tbod = deepcopy(bod)
                peeloff_expr(tbod, rank, maxbound - i)
                peeled.append(tbod)
        else:
            for i in range(factor-1, -1, -1):
                tbod = deepcopy(bod)
                peeloff_loop(tbod, rank, maxbound -i)
                peeled.append(tbod)
            
    return peeled



def peeloff_loop(loop, rank, val):
    for bod in loop.body:
        if bod.__class__.__name__ == "Expression":
            peeloff_expr(bod, rank, val)
        else:
            peeloff_loop(bod, rank, val)


            
def peeloff_expr(expr, rank, val):
    if expr.store != None:
        update_val_subs(expr.store, rank, val)
    if expr.left != None and expr.left.__class__.__name__ != "Expression":
        update_val_subs(expr.left, rank, val)
    else:
        peeloff_expr(expr.left, rank, val)
    if expr.right != None and expr.right.__class__.__name__ != "Expression":
        update_val_subs(expr.right, rank, val)
    else:
        peeloff_expr(expr.right, rank, val)



def update_val_subs(subs, rank, val):
    for i in range(0, len(subs.access)):
        if "i"+str(rank) == subs.access[i]:
            subs.access[i] = val




def unroll(loop, rank, factor):
    if factor == None:
        # Then full unrolling.
        if rank-1 >= 1:
            #If unrolled is non-outermost
            if loop.iterator.rank == rank-1:
                newb = None
                for i in range(0, len(loop.body)):
                    bod = loop.body[i]
                    if bod.__class__.__name__ == "Loop":
                        if bod.iterator.rank == rank:
                            factor = int(bod.iterator.maxbound)
                            newb = unrolloff(bod.body, rank, factor)

                loop.body = newb
            else:
                for bod in loop.body:
                    if bod.__class__.__name__ == "Loop":
                        unroll(bod, rank, factor)

        else:
            newb = None
            factor = int(loop.iterator.maxbound)
            newb = unrolloff(loop.body, rank, factor)           
            loop.outer_post_statements += newb
            loop.body = None
            loop.iterator = None
            



def unrolloff(body, rank, factor):
    unrolled = []
    for bod in body:
        for i in range(0, factor):
            tbod = deepcopy(bod)
            if bod.__class__.__name__ != "Loop":
                unrolloff_expr(tbod, rank, i)
            else:
                unrolloff_loop(tbod, rank, i)
            unrolled.append(tbod)
            
    return unrolled


def unrolloff_expr(expr, rank, val):
    if expr.store != None:
        update_val_subs(expr.store, rank, val)
    if expr.left != None and expr.left.__class__.__name__ != "Expression":
        update_val_subs(expr.left, rank, val)
    else:
        unrolloff_expr(expr.left, rank, val)
    if expr.right != None and expr.right.__class__.__name__ != "Expression":
        update_val_subs(expr.right, rank, val)
    else:
        unrolloff_expr(expr.right, rank, val)


def unrolloff_loop(loop, rank, val):
    for bod in loop.body:
        if bod.__class__.__name__ == "Expression":
            unrolloff_expr(bod, rank, val)
        else:
            unrolloff_loop(bod, rank, val)


            
def parallelize(loop, rank, type_, schedule):
    if loop.iterator.rank == rank:
        loop.iterator.type_ = type_
        loop.iterator.schedule = schedule
        ## Private variables will be collected
        ## right before code generation.
    else:
        for bod in loop.body:
            if bod.__class__.__name__ == "Loop":
                parallelize(bod, rank, type_, schedule)



def get_loop(l, rank, out):
    if l.iterator.rank != rank:
        for bod in l.body:
            if bod.__class__.__name__ == "Loop":
                out = get_loop(bod, rank, out)
    else:
        out = l
    return out

def fuse(loop, tofuse, rank):
    if loop.iterator.rank != rank:
        for bod in loop.body:
            if bod.__class__.__name__ == "Loop":
                fuse(bod, tofuse, rank)
    else:
        loop.body += tofuse.body

def get_iterator(l, rank, out):
    if l.iterator.rank != rank:
        for bod in l.body:
            if bod.__class__.__name__ == "Loop":
                out = get_iterator(bod, rank, out)
    else:
        out = l.iterator
    return out

def interchange(l, r1, r2, i1, i2):
    ## I ensure that r1 < r2 so that
    ## we first interchange the outermost dimension
    ## then go through innermost dimensions to find
    ## the other one to permute.
    ## Since the transformation is based on dimension ranking,
    ## we do a permutation of iteration ranges, then
    ## restore the proper rank at a given depth.
    ## This swapping also modifies iterator identifications in
    ## the statements because of the principle of ranking.
  
    
    if l.iterator.rank == r1:
        l.iterator = i2
        l.iterator.rank = r1
        l.iterator.name = "i" + str(r1)
        for bod in l.body:
            if bod.__class__.__name__ == "Loop":
                interchange(bod, r1, r2, i1, i2)
                #else:
                #    swap_in_expr(bod, r1, r2)

    elif l.iterator.rank == r2:
        l.iterator = i1
        l.iterator.rank = r2
        l.iterator.name = "i" + str(r2)
    else:
        for bod in l.body:
            if bod.__class__.__name__ == "Loop":
                interchange(bod, r1, r2, i1, i2)
                #else:
            #    swap_in_expr(bod, r1, r2)
    
        # ## Swapping within statement
        # ## With the flag set to False,
        # ## the recursion will continue
        # ## without destroying the permutations
        # for bod in l.body:
        #     print bod.debug_print()
        #     if bod.__class__.__name__ != "Loop":
        #         swap_in_expr(bod, r1, r2, flag)
        #     #else:    
        #     #    interchange(bod, r1, r2, i1, i2, )


def interchange_range(iterator, r1, r2):
    if "i"+str(r1) in iterator.minbound:
        iterator.minbound.replace("i"+str(r1), "i"+str(r2)+"_")
    if "i"+str(r1) in iterator.maxbound:
        iterator.maxbound.replace("i"+str(r1), "i"+str(r2)+"_")

    if "i"+str(r2) in iterator.minbound:
        iterator.minbound.replace("i"+str(r2), "i"+str(r1))
    if "i"+str(r2) in iterator.maxbound:
        iterator.maxbound.replace("i"+str(r2), "i"+str(r1))

    # clean up
    iterator.maxbound.replace("_","")
    iterator.minbound.replace("_","")
        
def interchange_stmt(l, r1, r2):

    #interchange_range(l.iterator, r1, r2)
    ## Swapping within statement
    for bod in l.body:
        if bod.__class__.__name__ != "Loop":
            swap_in_expr(bod, r1, r2)
        else:
            interchange_stmt(bod, r1, r2)
                        
  
            
def swap_in_expr(stmt, r1, r2):

    if stmt.store != None:
        swap_in_subs(stmt.store, r1, r2)

    if stmt.left != None and stmt.left.__class__.__name__ != "Expression":
        swap_in_subs(stmt.left, r1, r2)
    else:
        swap_in_expr(stmt.left, r1, r2)

    if stmt.right != None and stmt.right.__class__.__name__ != "Expression":
        swap_in_subs(stmt.right, r1, r2)
    else:
        swap_in_expr(stmt.right, r1, r2)

def swap_in_subs(subs, r1, r2):
    for i in range(0, len(subs.access)):
        if subs.access[i] == "i"+str(r1):
            # just a hack so that when I permute
            # the other rank, it does not modify
            # the newly permuted ones
            subs.access[i] = "i"+str(r2) + "_"
        if subs.access[i] == "i"+str(r2):
            subs.access[i] = "i"+str(r1)

    for i in range(0, len(subs.access)):
        if "_" in subs.access[i]:
            # Clean up the mess
            subs.access[i] = subs.access[i].replace("_","")

    
    
def increment_all_ranks(loop):
    loop.iterator.rank += 1
    loop.iterator.name = "i" + str(loop.iterator.rank)
    for bod in loop.body:
        if bod.__class__.__name__ == "Loop":
            increment_all_ranks(bod)
        else:
            print bod.debug_print()



def stripmine(loop, rank, factor):
    if loop.iterator.rank == rank:
        for bod in loop.body:
            if bod.__class__.__name__ == "Loop":
                update_stripmine_stmts(bod, rank)
            else:
                update_stripmine_expr(bod, rank)

        it = deepcopy(loop.iterator)
        
        #tileit = Iterator(rank, it.minbound, "(" + it.maxbound + ") / " + factor, it.stride)
      
        #loopit = Iterator(rank + 1, factor + " * " + it.name, factor + " * " + it.name + " + (" + factor + " - 1)", it.stride)

        #Assuming for the moment that I only
        # work with integers...
        tileit = Iterator(rank, it.minbound, str(int(it.maxbound) / int(factor)), it.stride)
        loop.iterator = tileit

              
        loopit = Iterator(rank + 1, factor + " * " + it.name, factor + " * " + it.name + " + " +str( int(factor)-1), it.stride)

                
        newloop = Loop(loopit, loop.body)
        loop.body = [newloop]

    else:
        for bod in loop.body:
            if bod.__class__.__name__ == "Loop":
                stripmine(bod, rank, factor)

                
def update_stripmine_stmts(loop, begin_rank):
    ## Here, in every statement, we increment
    ## ranks according to their new position in the
    ## loop, starting from begin_rank.
    
    loop.iterator.rank += 1
    loop.iterator.name = "i"+str(loop.iterator.rank)
    for bod in loop.body:
        if bod.__class__.__name__ != "Loop":
            update_stripmine_expr(bod, begin_rank)
        else:
            update_stripmine_stmts(bod, begin_rank)

def update_stripmine_expr(expr, begin_rank):
    if expr.store != None:
        update_stripmine_subs(expr.store, begin_rank)

    if expr.left != None and expr.left.__class__.__name__ != "Expression":
        update_stripmine_subs(expr.left, begin_rank)
    else:
        update_stripmine_expr(expr.left, begin_rank)
        
    if expr.right != None and expr.right.__class__.__name__ != "Expression":
        update_stripmine_subs(expr.right, begin_rank)
    else:
        update_stripmine_expr(expr.right, begin_rank)

def update_stripmine_subs(subs, begin_rank):
   
    for i in range(0, len(subs.access)):
        # Extracting the rank from the name
        lr = int(subs.access[i].replace("i",""))
        if lr >= begin_rank:
            lr += 1
            subs.access[i] = "i"+str(lr)











            

class IvieTransformationTile():    
    """ Types:
    permutable_band: list of IvieIterator. 

    Loop tiling is a composition of strip mining and 
    interchange """

    def __init__(self, permutable_band):
        self.permutable_band = permutable_band

    def debug_print(self):
        string = colored("Tile band", "green", attrs=["bold"]) + " (" 
        for iterator in self.permutable_band:
            string += "[" + iterator.debug_print() + \
                      ", " + iterator.tile_parent.debug_print() + "]\n" 
        string += ")"
        return string

    def legality_check(self):
        for iterator in self.permutable_band:
            if iterator.garbage == True:
                sys.exit("[Error][Loop tiling] %s is garbage" % iterator.name)
            if iterator.permutable == False:
                sys.exit("[Error][Loop tiling] %s is not permutable" % iterator.name)
            """
            if iterator.tilesize == None:
                sys.exit("Tile size not specified for %s" % iterator.name)
            """

    def apply_stripmine(self, iterator, ivieprog):
    
        transformation = IvieTransformationStripmine(iterator)
        """
        transformation.apply_stripmine()
        transformation.update_schedules(isl_schedules)
        """
        transformation.apply_transformation(ivieprog)

    def apply_interchange(self, ivieprog):
        """ At each step, a tile iterator is permuted with 
        its preceding iterators only if the preceding is not 
        tile iterator. This process is repeated k times as 
        k times is enough to ensure that all tile iterators 
        are set to the outermost dimensiosn. """


        isl_schedules = ivieprog.isl_loop_schedules
        for k in range(0, len(self.permutable_band) - 1):
            for i in range(0, len(isl_schedules)):
          
                for j in range(len(isl_schedules[i].schedule_object) - 1, 0, -1):
                    data = isl_schedules[i].schedule_object[j]
                    if data.__class__.__name__ == "IvieIteratorTile" and (j - 2 >= 0) and data.permutable == True:
                        tmp = isl_schedules[i].schedule_object[j-2]
                        if tmp.__class__.__name__ == "IvieIteratorIterator" and tmp.permutable == True:
                            transformation = IvieTransformationInterchange(data, tmp)
                            transformation.apply_transformation(ivieprog)
                            

    def apply_transformation(self, ivieprog):
        """ For the tiling to be valid, all iterators must 
        be marked as permutable """


        LOOPS = ivieprog.loops
        isl_schedules = ivieprog.isl_loop_schedules

        self.legality_check()
        ## If the program reached this point, then 
        ## all iterators are permutable: do the tiling.
        for iterator in self.permutable_band:
            self.apply_stripmine(iterator, ivieprog)

        self.apply_interchange(ivieprog)

class IvieTransformationUnroll():
    
    def __init__(self, iterator):
        self.iterator = iterator
        self.innerfuse = False

    def debug_print(self):
        string = colored("Unroll ", "green", attrs=["bold"]) + \
                 self.iterator.debug_print() + " by factor " + \
                 self.iterator.unroll_factor 
        return string

    def set_innerfuse(self):
        self.innerfuse = True

    def legality_check(self):
        if self.iterator.garbage == True:
            sys.exit("Cannot unroll %s: garbage" % self.iterator.name)
        if self.iterator.unroll_factor == None:
            sys.exit("Unroll factor is not provided for %s" % self.iterator.name)

    def update_schedule(self, isl_schedules):
        news = []
        for sched in isl_schedules:
            if self.iterator in sched.schedule_object:
                name = sched.name
                pos = sched.schedule_object.index(self.iterator)
                for i in range(0, int(self.iterator.unroll_factor)-1):
                    copy_ = copy(sched.schedule_object)
                    copy_[pos + 1] = i + 1
                    new_ = IslSchedule(name + "_" + str(i), copy_)
                    news.append(new_)
        isl_schedules += news

    def increment_indexes(self, loop, incr, flag, transformations, newiters):
        
        for i in range(0, len(loop.body)):
            if loop.body[i].__class__.__name__ == "IvieStatement":
                loop.body[i].name += "_" + incr
                if self.iterator.unroll_factor != self.iterator.maxbound:

                    for j in range(0, len(loop.body[i].store.indexes)):
                        if self.iterator.name == loop.body[i].store.indexes[j].name:
                            loop.body[i].store.indexes[j].name += " + " + incr
                        else:
                            for newiter in newiters:
                                if loop.body[i].store.indexes[j].name in newiter.name:
                                    loop.body[i].store.indexes[j] = newiter
                        
                    for k in range(0, len(loop.body[i].args)):
                        for j in range(0, len(loop.body[i].args[k].indexes)):
                            if self.iterator.name == loop.body[i].args[k].indexes[j].name:
                                loop.body[i].args[k].indexes[j].name += "+ " + incr
                            else:
                                for newiter in newiters:
                                    if loop.body[i].args[k].indexes[j].name in newiter.name:
                                        loop.body[i].args[k].indexes[j] = newiter

                else:
                    for j in range(0, len(loop.body[i].store.indexes)):
                        if self.iterator.name == loop.body[i].store.indexes[j].name:
                            loop.body[i].store.indexes[j].name = incr
                        """
                        else:
                            for newiter in newiters:
                                if loop.body[i].store.indexes[j].name in newiter.name:
                                    loop.body[i].store.indexes[j] = newiter
                        """

                    for k in range(0, len(loop.body[i].args)):
                        for j in range(0, len(loop.body[i].args[k].indexes)):
                            if self.iterator.name == loop.body[i].args[k].indexes[j].name:
                                loop.body[i].args[k].indexes[j].name = incr
                            """
                            else:
                                for newiter in newiters:
                                    if loop.body[i].args[k].indexes[j].name in newiter.name:
                                        loop.body[i].args[k].indexes[j] = newiter
                            """
                            
                
            else:
                name = loop.body[i].iterators.name + "_" + str(int(incr))
                newiter = IvieIteratorVirtualize(name, loop.body[i].iterators)
                old = loop.body[i].iterators
                loop.body[i].iterators = newiter
                newiters.append(newiter)
                if self.innerfuse == True:
                    transformation = IvieTransformationFuse(old, loop.body[i].iterators)
                    transformations.append(transformation)
                self.increment_indexes(loop.body[i], incr, flag, transformations, newiters)


    def update_zero(self, loop):
        for i in range(0, len(loop.body)):
            if loop.body[i].__class__.__name__ == "IvieStatement":
                #print loop.body[i].debug_print()
                for j in range(0, len(loop.body[i].store.indexes)):
                    if self.iterator.name == loop.body[i].store.indexes[j].name:
                        loop.body[i].store.indexes[j].name = '0' 
                for k in range(0, len(loop.body[i].args)):
                    for j in range(0, len(loop.body[i].args[k].indexes)):
                        if self.iterator.name == loop.body[i].args[k].indexes[j].name:
                            loop.body[i].args[k].indexes[j].name = '0'         
            if loop.body[i].__class__.__name__ == "IvieLoop":
                self.update_zero(loop.body[i])
                
    def update_body(self, loop, prevloop, transformations):
        if loop.iterators.name == self.iterator.name:
            new_body = []

            if self.iterator.unroll_factor == self.iterator.maxbound:
                self.update_zero(loop)
                

            for incr in range(0, int(self.iterator.unroll_factor)-1):
                #tmp = deepcopy(loop)
                #self.increment_indexes(loop, str(i + 1))
                body = deepcopy(loop.body)
                

                for i in range(0, len(body)):
                    if body[i].__class__.__name__ == "IvieStatement":
                        body[i].name += "_" + str(int(incr)+1)

                        if self.iterator.unroll_factor != self.iterator.maxbound:
                            for j in range(0, len(body[i].store.indexes)):
                                if self.iterator.name == body[i].store.indexes[j].name:
                                    body[i].store.indexes[j].name += " + " + str(int(incr) + 1) 
                            for k in range(0, len(body[i].args)):
                                for j in range(0, len(body[i].args[k].indexes)):
                                    if self.iterator.name == body[i].args[k].indexes[j].name:
                                        body[i].args[k].indexes[j].name += " + " + str(int(incr) + 1)          
                        else:
                            for j in range(0, len(body[i].store.indexes)):
                                if self.iterator.name == body[i].store.indexes[j].name:
                                    body[i].store.indexes[j].name = str(int(incr) + 1) 
                            for k in range(0, len(body[i].args)):
                                for j in range(0, len(body[i].args[k].indexes)):
                                    if self.iterator.name == body[i].args[k].indexes[j].name:
                                        body[i].args[k].indexes[j].name = str(int(incr) + 1)         
                                    
                    else:
                        name = body[i].iterators.name + "_" + str(int(incr) + 1)
                        newiter = IvieIteratorVirtualize(name, body[i].iterators)
                        old = body[i].iterators
                        body[i].iterators = newiter
                        newiters = [newiter]
                        if self.innerfuse == True:
                            transformation = IvieTransformationFuse(old, body[i].iterators)
                            transformations.append(transformation)
                        self.increment_indexes(body[i], str(int(incr) + 1), 0, transformations, newiters)
                
                new_body += body 
       
            loop.body += new_body

            if self.iterator.unroll_factor == self.iterator.maxbound:
                ## Add unrolled body to previous dimension
                prevloop.body += loop.body
                ## Delete dimension of unrolled loop
                prevloop.body = filter(lambda a: a != loop, prevloop.body)

            
        else:
            for bod in loop.body:
                if bod.__class__.__name__ == "IvieLoop":
                    self.update_body(bod, loop, transformations)

    def apply_transformation(self, ivieprog):
    
        isl_schedules = ivieprog.isl_loop_schedules
        LOOPS = ivieprog.loops
        self.legality_check()
        

        nb_iterations = (int(self.iterator.maxbound) - int(self.iterator.minbound)) 
        remainder = nb_iterations % int(self.iterator.unroll_factor)
        
        
        if remainder != 0:
            ## Unrolling with factor non-multiple.
            ## Peel. 
            ## Don't know yet if one must peel at the end or 
            ## beginning. For the moment, I just assume it's 
            ## at the end.
            self.iterator.set_peel_end_factor(remainder)
            transformation = IvieTransformationPeel(self.iterator)
            transformation.apply_transformation(ivieprog)
   
        # Unroll
        if int(self.iterator.unroll_factor) > 1:
            self.iterator.update_stride(self.iterator.unroll_factor)

   
        # Update loop body structure
        transf = []
        
        for i in range(0, len(LOOPS)):
            self.update_body(LOOPS[i], None, transf)
        
            

        #self.update_schedule(isl_schedules)

        ## If there are loop fusions to apply, it will happen here.
        for trans in transf:
            trans.apply_transformation(ivieprog)
        
        """
        if self.iterator.unroll_factor == self.iterator.maxbound:
            self.iterator.mark_as_garbage()
        """

