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
    if loop.iterator.rank == rank-1:
        newb = None
        for bod in loop.body:
            if bod.__class__.__name__ == "Loop":
                if bod.iterator.rank == rank:
                    mbound = int(bod.iterator.maxbound)
                    bod.iterator.maxbound = str(int(bod.iterator.maxbound) - factor)
                    newb = peeloff(bod.body, rank, mbound, factor)
        if loop.iterator.rank > 1:
            loop.body += newb
        else:
            loop.outer_post_statements += newb
    else:
        for bod in loop.body:
            if bod.__class__.__name__ == "Loop":
                    peel(bod, rank, factor)


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
        peeloff_subs(expr.store, rank, val)
    if expr.left != None and expr.left.__class__.__name__ != "Expression":
        peeloff_subs(expr.left, rank, val)
    else:
        peeloff_expr(expr.left, rank, val)
    if expr.right != None and expr.right.__class__.__name__ != "Expression":
        peeloff_subs(expr.right, rank, val)
    else:
        peeloff_expr(expr.right, rank, val)


def peeloff_subs(subs, rank, val):
    for i in range(0, len(subs.access)):
        if "i"+str(rank) == subs.access[i]:
            subs.access[i] = val
                    
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

class IvieTransformationReverse():
    def __init__(self, iterator):
        self.reversed = iterator

    def debug_print(self):
        string = colored("Reverse ", "green", attrs=["bold"]) + self.reversed.name 
        return string
    
    def apply_transformation(self, ivieprog):
        
        minbound = self.reversed.maxbound
        maxbound = self.reversed.minbound
        
        self.reversed.update_minbound(minbound)
        self.reversed.update_maxbound(maxbound)
        self.reversed.set_reversed(True)




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


# def stripmine(outer, current, rank, factor):
#     if current.iterator.rank == rank:
#         it = current.iterator
#         tileit = Iterator(lr, it.minbound, "(" + it.maxbound + ") / " + factor, it.stride)

#         it.rank = rank + 1
#         it.minbound = factor + " * " + tileit.name
#         it.maxbound = factor + " * " + tileit.name + " + (" + factor + " -1)"
#         it.stride = tileit.stride

#         newloop = Loop(tileit, [current])

#         ## This assumes that the loop is perfectly nested..
#         if outer != None:
#             outer.body = [newloop]
#             newloop = outer

#         return newloop


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
        
def unroll(outer, loop, rank, factor):
    if loop.iterator.rank == rank:
        if factor == None:
            factor = int(loop.iterator.maxbound)

        newbody = []
        newbody.append(deepcopy(loop.body))
        for i in range(1, factor):
            #newbody.append(update(deepcopy(loop.body), rank, i))
            newbody.append(deepcopy(loop.body))

        outer.body = [newbody]
            
# def stripmine(outerloop, currentloop, rank):
#     if currentloop.iterator.rank == rank:
#         newloop.body = currentloop.body
#         for bod in newloop.body:
#             if bod.__class__.__name__ == "Loop":
#                 increment_all_ranks(bod)
#         outerloop.body += newloop.body
#     else:
#         for bod in newloop.body:
#             if bod.__class__.__name__ == "Loop":
#                 stripmine(currentloop, bod, rank, newloop)
        

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

# Broken
class IvieTransformationDistribute():
    """ Types:
    parent: IvieIterator
    newiter: IvieIterator
    """

    def __init__(self, parent, newloop, stmts):
        self.parent = parent
        self.newloop = newloop
        self.stmts = stmts


    def debug_print(self):
        string = colored("Distribute: ", "green", attrs=["bold"]) + self.parent.debug_print() + " using (" 
        for iterator in self.newloop:
            string += iterator.debug_print() + "\n "
        string += ")"
        return string

    def check_legality(self):
        """ To make a distribution legal, the new iterator
        must be a replication of parent. 
        [TODO] We also need to check if dependencies aren't broken """
    

        ## Comparison of instances if enough
        if self.new_iterator.parent != None:
            if self.new_iterator.parent != self.parent:
                sys.exit("[Error][Distribute] %s is not equal to %s" % (self.new_iterator.name, self.parent.name))
        else:
            if self.new_iterator.minbound != self.parent.minbound or self.new_iterator.maxbound != self.parent.maxbound or self.new_iterator.stride != self.parent.stride:
                sys.exit("[Error][Distribute] %s is not equal to %s" % (self.new_iterator.name, self.parent.name))  

    
    def update_schedules(self, isl_schedules):
        new_scheds = []
        ## Copy 
        
        tmp= None

        for sched in isl_schedules:
            if self.parent in sched.schedule_object:
                tmp = sched
                break

        for z in range(0, len(self.stmts)):
            new_scheds.append(deepcopy(tmp))

        ### Update schedules that need to be updated
        for sched in isl_schedules:
            if sched.schedule_object[0] > new_scheds[0].schedule_object[0]:
                sched.schedule_object[0] += 1

        for new_sched in new_scheds:
            for i in range(0, len(new_sched.schedule_object)):
                if not isinstance(new_sched.schedule_object[i], int):
                    if new_sched.schedule_object[i].name == self.parent.name:
            
                        new_sched.schedule_object[i-1] += 1

                    for iterator in self.newloop:
                        if iterator.parent.name == new_sched.schedule_object[i].name:
                            new_sched.schedule_object[i] = iterator


        poses = []
        ## Remove old stmts before adding distributed one
        for i in range(0, len(isl_schedules)):
            if isl_schedules[i].name in self.stmts:
                poses.append(i)
        
        for i in sorted(poses, reverse=True):
            isl_schedules.pop(i)
        
        isl_schedules += new_scheds


    def replace_iterator(self, loop, iterator):
        if iterator.parent != None and iterator.parent.name == loop.iterators.name:
            loop.iterators = iterator
            
        poses = []
        for bod in loop.body:
            if bod.__class__.__name__ == "IvieStatement": 
                if bod.name in self.stmts:
                    for i in range(0, len(bod.store.indexes)):
                        if bod.store.indexes[i].name == iterator.parent.name:
                            bod.store.indexes[i] = iterator
                    for i in range(0, len(bod.args)):
                        for j in range(0, len(bod.args[i].indexes)):
                            if bod.args[i].indexes[j].name == iterator.parent.name:
                                bod.args[i].indexes[j] = iterator
                else:
                    poses.append(loop.body.index(bod))
                    
            else: 
                self.replace_iterator(bod, iterator)

        ## Delete unwanted statement
        for i in sorted(poses, reverse=True):
            loop.body.pop(i)
            

    def cleanup(self, loop):
        poses = []
        for bod in loop.body:
            if bod.__class__.__name__ == "IvieStatement":
                if bod.name in self.stmts:
                    poses.append(loop.body.index(bod))
            else:
                self.cleanup(bod)

        for i in sorted(poses, reverse=True):
            loop.body.pop(i)


    def build_new_loop(self, loop, prevloop):
        """ For the new loop to build
        we make a deepcopy and replace 
        all iterators with their respective
        replications. """

        newloop = None
        if loop.iterators.name == self.parent.name:
            newloop = deepcopy(loop)

            self.cleanup(loop)



            for iterator in self.newloop:
                self.replace_iterator(newloop, iterator)

            if prevloop != []:
                prevloop[0].body.append(newloop)
            else:
                prevloop += [newloop]
       
        else:
            for i in range(0, len(loop.body)):
                if loop.body[i].__class__.__name__ == "IvieLoop":
                    self.build_new_loop(loop.body[i], [loop])

      

    def apply_transformation(self, ivieprog):

        LOOPS = ivieprog.loops
        isl_schedules = ivieprog.isl_loop_schedules
        #self.update_schedules(isl_schedules)
        
        for i in range(0, len(LOOPS)):
            tmp = []
            self.build_new_loop(LOOPS[i], tmp)
            if tmp != []:
                LOOPS.insert(i+1, tmp[0])
            
# Broken
class IvieTransformationClone():
    """ Types:
    cloned: IvieIterator
    new_clone: list of IvieIterator. """
    
    old_loop = None

    def __init__(self, cloned, new_clone):
        self.cloned = cloned
        self.new_loop = new_clone


    def debug_print(self):
        string = colored("Clone: ", "green", attrs=["bold"]) + self.cloned.debug_print() + " using (" 
        for iterator in self.new_loop:
            string += iterator.debug_print() + "\n "
        string += ")"
        return string

    def replace_iterator(self, loop, iterator):
        if iterator.parent != None and iterator.parent.name == loop.iterators.name:
            loop.iterators = iterator
            
        for bod in loop.body:
            if bod.__class__.__name__ == "IvieStatement": 
                for i in range(0, len(bod.store.indexes)):
                    if bod.store.indexes[i].name == iterator.parent.name:
                        bod.store.indexes[i] = iterator
                for i in range(0, len(bod.args)):
                    for j in range(0, len(bod.args[i].indexes)):
                        if bod.args[i].indexes[j].name == iterator.parent.name:
                            bod.args[i].indexes[j] = iterator
            else: 
                self.replace_iterator(bod, iterator)


    def build_new_loop(self, loop):
        """ For the new loop to build
        we make a deepcopy and replace 
        all iterators with their respective
        replications. """
        
        newloop = deepcopy(loop)

        for iterator in self.new_loop:
            self.replace_iterator(newloop, iterator)

        return newloop

    def update_schedules(self, isl_schedules):
        new_sched = None
        ## Copy 
        for sched in isl_schedules:
            if self.cloned in sched.schedule_object:
                new_sched = deepcopy(sched)

        ### Update schedules that need to be updated
        for sched in isl_schedules:
            if sched.schedule_object[0] > new_sched.schedule_object[0]:
                sched.schedule_object[0] += 1

        for i in range(0, len(new_sched.schedule_object)):
            if not isinstance(new_sched.schedule_object[i], int):
                if new_sched.schedule_object[i].name == self.cloned.name:
            
                    new_sched.schedule_object[i-1] += 1

                for iterator in self.new_loop:
                    if iterator.parent.name == new_sched.schedule_object[i].name:
                        new_sched.schedule_object[i] = iterator

        isl_schedules.append(new_sched)


    def apply_transformation(self, ivieprog):

        LOOPS = ivieprog.loops
        isl_schedules = ivieprog.isl_loop_schedules
        pos = None
        res = None
        for i in range(0, len(LOOPS)):

            if LOOPS[i].iterators == self.cloned:
                ### Find outermost dimension
                ### For the moment, in the context of CFD
                ### outermost dimensions only are concerned
                res = self.build_new_loop(LOOPS[i])
                
                pos = i

        LOOPS.insert(pos+1, res)


        #self.update_schedules(isl_schedules)


### Experimental :/
class IvieTransformationPurge():
    """ This transformation is used in the context 
    of operators involved in CFD computations. The operation
    occuring here are very specific and simple. When purging 
    an iterator:
    - in an IslSchedule, the position corresponding to the 
      iterator is set to 0
    - in LOOPS, the body of the corresponding dimension 
      is hoisted out to its outer dimension AND all array
      accesses involving the purged iterator are removed 
      from the statement. 
    
    Types:
       purgeable: IvieIterator
    """

    def __init__(self, purgeable):
        self.purgeable = purgeable

    def debug_print(self):
        string = colored("Purge ", "green", attrs=["bold"]) + self.purgeable.debug_print()
        return string

    def purge_body(self, body):
        """ In every statement, delete array access functions
        that involve self.purgeable. The written element is 
        never concerned. """
 
        for bod in body:
            if bod.__class__.__name__ == "IvieStatement":
                poses = []
                for i in range(0, len(bod.args)):
                    for j in range(0, len(bod.args[i].indexes)):
                        if bod.args[i] != 0 and bod.args[i].array.forbid_purge == False and \
                           bod.args[i].indexes[j] == self.purgeable:
                            ## Replace args to be deleted by 0
                            bod.args[i] = 0
                        elif bod.args[i] != 0 and bod.args[i].indexes[j] == self.purgeable:
                            if bod.args[i].indexes[j].axe_traversal == True:
                                ## For remaining access functions based on self.purgeable (those 
                                ## for which we forbid purging) make these reference fall back 
                                ## on parent reference
                                bod.args[i].indexes[j] = bod.args[i].indexes[j].axe_traversor_parent
                                
                            """
                            ## Now there may be cases where the considered iterator is 
                            ## a replicate that has an AxeTraversor in its genealogy. 
                            ## These must be taken into account also
                            if bod.args[i].indexes[j].__class__.__name__ == "IvieIteratorReplicate":
                                ## We are going to ascend its genealogy to search for
                                ## the last parent that is an Axeitraversor
                                parent = bod.args[i].indexes[j].parent
                                while parent != None:
                                    if parent.__class__.__name__ == "IvieIteratorAxetraversor":
                                        break
                                    else:
                                        parent = parent.parent
                                bod.args[i].indexes[j] = parent
                            """

                ## Clean up list
                bod.args = filter(lambda a: a != 0, bod.args)

            else:
                self.purge_body(bod.body)


    def purge_dimension(self, body):
        for i in range(0, len(body)):
            if body[i].__class__.__name__ == "IvieLoop":
                if body[i].iterators == self.purgeable:
                    body[i] = 0

        body = filter(lambda a: a != 0, body)
        return body
                
    def update_schedule(self, isl_schedules):
        for i in range(0, len(isl_schedules)):
            if self.purgeable in isl_schedules[i].schedule_object:
                pos = isl_schedules[i].schedule_object.index(self.purgeable)
                # Remove element and its associated schedule number 
                # (the preceeding element)
                isl_schedules[i].schedule_object.pop(pos)
                isl_schedules[i].schedule_object.pop(pos-1)
        
    
    def get_body(self, loop):
        getbody = None
        for bod in loop.body:
            if bod.__class__.__name__ == "IvieLoop":
                if bod.iterators == self.purgeable:
                    getbody = bod.body

        if getbody == None:
            for bod in loop.body:
                if bod.__class__.__name__ == "IvieLoop":
                  getbody = self.get_body(bod)
        else:
            ## Modify body content
            ## Hoist body
            ## Remove dimension
   
            self.purge_body(getbody)
            loop.body += getbody
            loop.body = self.purge_dimension(loop.body)

        return getbody
    
    def apply_transformation(self, ivieprog):
        """ Deletes any dimension involving self.purgeable AND 
        any array access function involving this iterator. """

        isl_schedules = ivieprog.isl_loop_schedules
        LOOPS = ivieprog.loops

        self.update_schedule(isl_schedules)
        for loop in LOOPS:
            body = self.get_body(loop)

            

        

