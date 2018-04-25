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
                

class IvieTransformationParallelize():
    def __init__(self, iterator, type_, schedule, private_vars):
        self.iterator = iterator
        self.type_ = type_
        self.schedule = schedule
        self.private_variables = private_vars

    def search_atomic(self, loop):
        for bod in loop.body:
            if bod.__class__.__name__ == "IvieStatement":
                atomic = True
                for index in bod.store.indexes:
                    if index.name == self.iterator.name:
                        atomic = False

                bod.set_atomicity(atomic)
            elif bod.__class__.__name__ == "IvieLoop":
                if bod.iterators.name == self.iterator.name:
                    self.search_atomic(bod)

    def apply_transformation(self, ivieprog):
        self.iterator.set_kind("piter")
        self.iterator.set_parallelism(self.type_)
        self.iterator.set_private_variables(self.private_variables)
        self.iterator.set_schedule(self.schedule)

        for loop in ivieprog.loops:
            if loop.iterators.name == self.iterator.name:
                self.search_atomic(loop)

class IvieTransformationPeel():
    def __init__(self, iterator):
        self.peeled = iterator
      
    def debug_print(self):
        string = colored("Peel ", "green", attrs=["bold"]) + self.peeled.name 
        return string

    def update_schedule(self, isl_schedules):
        news = []
        pos = None
        old = None
        if self.peeled.peel_begin_factor != None:
            for sched in isl_schedules:
                if self.peeled in sched.schedule_object:
                    checklen = len(sched.schedule_object)
                    pos = sched.schedule_object.index(self.peeled)
                    old = sched.schedule_object[pos-1]
                    sched.schedule_object[pos-1] += int(self.peeled.peel_begin_factor)
                    
                    ### If peeling occurs inside a loop, do this
                    ### otherwise, do not generate schedules for 
                    ### single statements
                    if pos-1 != 0:
                        for i in range(0, int(self.peeled.peel_begin_factor)):
                            copy_ = copy(sched.schedule_object)
                            copy_[pos - 1] = copy_[pos - 1] - i - 1
                            copy_[pos] = 0

                            tmp = copy_[pos+2:]
                            copy_[pos:] = tmp
                            new_ = IslSchedule(copy_)
                            news.append(new_)

            if pos-1 == 0:
                for sched in isl_schedules:
                    if sched.schedule_object[pos] != self.peeled:
                        if sched.schedule_object[pos-1] > old:
                            sched.schedule_object[pos-1] += int(self.peeled.peel_begin_factor)
        if self.peeled.peel_end_factor != None:
           
            for sched in isl_schedules:
                if self.peeled in sched.schedule_object:
                
                    checklen = len(sched.schedule_object)
                    pos = sched.schedule_object.index(self.peeled)
                    old = sched.schedule_object[pos-1]

                    #sched.schedule_object[pos-1] += int(self.peeled.peel_factor)
                    
                    ### If peeling occurs inside a loop, do this
                    ### otherwise, do not generate schedules for 
                    ### single statements
                    if pos-1 != 0:
                        for i in range(0, int(self.peeled.peel_end_factor)):
                            
                            copy_ = copy(sched.schedule_object)
                            
                            copy_[pos - 1] = copy_[pos - 1] + i + 1
                            copy_[pos] = 0

                            tmp = copy_[pos+2:]
                            copy_[pos:] = tmp
                            new_ = IslSchedule(copy_)
                            news.append(new_)

                            

            if pos-1 == 0:
                for sched in isl_schedules:
                    if sched.schedule_object[pos] != self.peeled:
                        if sched.schedule_object[pos-1] > old:
                            sched.schedule_object[pos-1] += int(self.peeled.peel_end_factor)

        
        isl_schedules += news
        """
        for cc in isl_schedules:
            print cc.schedule_object
        """
    def increment_indexes(self, loop, incr, newiters, transformations):   
        for i in range(0, len(loop.body)):
            if loop.body[i].__class__.__name__ == "IvieStatement":
                loop.body[i].name += "_p" + incr
                for j in range(0, len(loop.body[i].store.indexes)):
                    if self.peeled.name == loop.body[i].store.indexes[j].name:
                        loop.body[i].store.indexes[j].name = incr
                    else:
                        for newiter in newiters:
                             if loop.body[i].store.indexes[j].name in newiter.name:
                                loop.body[i].store.indexes[j] = newiter

                for k in range(0, len(loop.body[i].args)):
                    for j in range(0, len(loop.body[i].args[k].indexes)):
                        if self.peeled.name == loop.body[i].args[k].indexes[j].name:
                            loop.body[i].args[k].indexes[j].name = incr
                        else:
                            for newiter in newiters:
                                if loop.body[i].args[k].indexes[j].name in newiter.name:
                                    loop.body[i].args[k].indexes[j] = newiter
            else:
                name = loop.body[i].iterators.name + "_p" + str(incr)
                newiter = IvieIteratorVirtualize(name, loop.body[i].iterators)
                old = loop.body[i].iterators
                loop.body[i].iterators = newiter
                newiters.append(newiter)
                transformation = IvieTransformationFuse(old, loop.body[i].iterators)
                transformations.append(transformation)
                self.increment_indexes(loop.body[i], incr, newiters, transformations)
                

    def update_loop_begin(self, loop, prevloop):
        if loop.iterators == self.peeled:
            new_body = []

            min_ = int(self.peeled.minbound)
            max_ = int(self.peeled.peel_begin_factor)
        
            for incr in range(min_, max_):
                body = deepcopy(loop.body)
                for i in range(0, len(body)):
                    if body[i].__class__.__name__ == "IvieStatement":
                        for j in range(0, len(body[i].store.indexes)):
                            if self.peeled.name == body[i].store.indexes[j].name:
                                body[i].store.indexes[j].name = str(incr) 
                

                        for k in range(0, len(body[i].args)):
                            for j in range(0, len(body[i].args[k].indexes)):
                                if self.peeled.name == body[i].args[k].indexes[j].name:
                                    body[i].args[k].indexes[j].name = str(incr)
                    else:
                        name = body[i].iterators.name + "_p" + str(incr)
                        newiter = IvieIteratorVirtualize(name, body[i].iterators)
                        old = body[i].iterators
                        body[i].iterators = newiter
                        newiters = [newiter]

                        self.increment_indexes(body[i], str(incr))
                new_body += body



            if prevloop != None:
                prevloop.body += new_body
            else: 
                loop.outer_pre_statements += new_body

        else:
            for bod in loop.body:
                if bod.__class__.__name__ == "IvieLoop":
                    self.update_loop_begin(bod, loop)


    def update_loop_end(self, loop, prevloop, transformations):
        if loop.iterators == self.peeled:
            new_body = []

            min_ = int(self.peeled.maxbound) - int(self.peeled.peel_end_factor) 
            max_ = int(self.peeled.maxbound)

            for incr in range(min_, max_):
                body = deepcopy(loop.body)
               
                for i in range(0, len(body)):
                    if body[i].__class__.__name__ == "IvieStatement":
                        for j in range(0, len(body[i].store.indexes)):
                            if self.peeled.name == body[i].store.indexes[j].name:
                                body[i].store.indexes[j].name = str(incr) 
                

                        for k in range(0, len(body[i].args)):
                            for j in range(0, len(body[i].args[k].indexes)):
                                if self.peeled.name == body[i].args[k].indexes[j].name:
                                    body[i].args[k].indexes[j].name = str(incr)
                    else:
                        name = body[i].iterators.name + "_p" + str(incr)
                        newiter = IvieIteratorVirtualize(name, body[i].iterators)
                        old = body[i].iterators
                        body[i].iterators = newiter
                        newiters = [newiter]
                        ## Fuse peeled loops
                        transformation = IvieTransformationFuse(old, body[i].iterators)
                        transformations.append(transformation)
                        self.increment_indexes(body[i], str(incr), newiters, transformations)

                new_body += body

            if prevloop != None:
                prevloop.body += new_body
            else: 
                loop.outer_post += new_body

        else:
            for bod in loop.body:
                if bod.__class__.__name__ == "IvieLoop":
                    self.update_loop_end(bod, loop, transformations)



    def apply_transformation(self, ivieprog):
 
        isl_schedules = ivieprog.isl_loop_schedules
        LOOPS = ivieprog.loops
        #self.update_schedule(isl_schedules)
        transformations = []
        for loop in LOOPS:
            if self.peeled.peel_begin_factor != None:
                self.update_loop_begin(loop, None)
        for loop in LOOPS:
            if self.peeled.peel_end_factor != None:
                self.update_loop_end(loop, None, transformations)

        if self.peeled.peel_end_factor != None:
            self.peeled.maxbound = str(int(self.peeled.maxbound) - int(self.peeled.peel_end_factor))
            #self.peeled.maxbound += "-" + self.peeled.peel_end_factor
        

        if self.peeled.peel_begin_factor != None:
            self.peeled.maxbound = str(int(self.peeled.maxbound) + int(self.peeled.peel_end_factor))
            #self.peeled.minbound += " + " + self.peeled.peel_begin_factor

        ## Verify if this is actually accurate, but seems like 
        ## when peeling, dimension is no longer permutable (????)
        ## In case of, we set this as no longer permutable
        self.peeled.set_permutability(False)



        ## Apply fusions
        for trans in transformations:
            trans.apply_transformation(ivieprog)

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


class IvieTransformationReplace():
    
    def __init__(self, dimension, origin, replacer):
        self.dimension = dimension
        self.origin = origin
        self.replacer = replacer 

    def debug_print(self):
        string = colored("Replace array ", "green", attrs=["bold"]) \
                 + self.origin.debug_print() + " with " \
                 + self.replacer.debug_print() + " in " + self.dimension.debug_print()

        return string

    def apply_replacement(self, loop):
        if loop.iterators.name == self.dimension.name:
            for bod in loop.body:
                if bod.__class__.__name__ == "IvieStatement":
                    if bod.store.array.name == self.origin.name:
                        bod.store.array = self.replacer

                    for arg in bod.args:
                        if arg.array.name == self.origin.name:
                            arg.array = self.replacer
                else:
                    self.apply_replacement(bod)
        else:
            for bod in loop.body:
                if bod.__class__.__name__ == "IvieLoop":
                    self.apply_replacement(bod)

    def apply_transformation(self, ivieprog):
        LOOPS = ivieprog.loops
        for loop in LOOPS:
            #print loop.debug_print()
            self.apply_replacement(loop)



class IvieTransformationFuse():
    """ Types:
    remaining: IvieIterator
    fused: IvieIterator. """

    def __init__(self, remaining, fused):
        self.remaining = remaining
        self.fused = fused


    def debug_print(self):
        string = colored("Fuse ", "green", attrs=["bold"]) \
                 + self.fused.debug_print() + " into " \
                 + self.remaining.debug_print() 
        return string



    def legality_check(self, STATEMENTS):
        """ The followings are cases where fusion will fail:
        - remaining and/or fused are marked as garbage
        - remaning and fused do not have the same iteration domain
        - TO BE COMPLETED
        """

        if self.remaining.garbage == True or self.fused.garbage == True:
            sys.exit("[Error][Loop fusion] Use of invalid iterator")

        if self.remaining.minbound != self.fused.minbound or \
           self.remaining.maxbound != self.fused.maxbound or self.remaining.stride != self.fused.stride:
            sys.exit("[Error][Loop fusion] %s and %s do not have the same iteration domain" % (self.remaining, self.fused))

        ### Check how it impacts parallel-specific parameters
        ### -- Do they have the same private variables
        ### -- Are they both parallel ?
    
        ### If one is parallel and the other one sequential, parallel one looses
        ### parallelism
        if self.remaining.kind == "siter" and self.fused.kind == "piter" or \
           self.fused.kind == "siter" and self.remaining.kind == "piter":
            #print "[Warning][Loop fusion] Fusing a parallel dim with a sequential dim; parallelism lost"
            self.remaining.kind = "siter"
            self.fused.kind = "siter"


    def update_isl_schedules(self, isl_schedules):
        pop = None

        for i in range(0, len(isl_schedules)):
            for j in range(0, len(isl_schedules[i].schedule_object)):
                if isl_schedules[i].schedule_object[j] == self.remaining:
                    # Retrieve schedule part to replace fused schedule
                    # and increment last element
                    pop = isl_schedules[i].schedule_object[:j+2]
                    last_elt = pop[len(pop)-1]
                    pop[len(pop) -1] = last_elt + 1
            
        # Replace fused schedule
        #old_pop = None

        for i in range(0, len(isl_schedules)):
            for j in range(0, len(isl_schedules[i].schedule_object)):
                #print isl_schedules[i].schedule_object[j]
                if isl_schedules[i].schedule_object[j] == self.fused:
                    isl_schedules[i].schedule_object[:j+2] = pop
                    
        

    def update_merged_statement(self, loop):
        """ When merging applies, all statements 
        concerned by the fused iterator must be have 
        their indexes updated. """

            
        for bod in loop.outer_pre + loop.body + loop.outer_post:
            if bod.__class__.__name__ == "IvieStatement":
                ## Virtualized for data deps
                #virtname = self.remaining.name + "_" + str(len(self.remaining.virtualized))
                virtname = self.remaining.name
                virtiter = IvieIteratorVirtualize(virtname, self.remaining)
                self.remaining.add_virtualized(virtiter)
                for i in range(0, len(bod.store.indexes)):
                    if bod.store.indexes[i].name == self.fused.name:
                        bod.store.indexes[i] = virtiter
                
                for k in range(0, len(bod.args)):
                    for i in range(0, len(bod.args[k].indexes)):
                        if bod.args[k].indexes[i].name == self.fused.name:
                            bod.args[k].indexes[i] = virtiter
            else:
                self.update_merged_statement(bod)
                


    def get_body(self, loop, body):
        if loop.iterators.name == self.fused.name:
            body += loop.body
        else:
            for i in range(0, len(loop.body)):
                if loop.body[i].__class__.__name__ == "IvieLoop":
                    self.get_body(loop.body[i], body)

            for i in range(0, len(loop.outer_pre)):
                if loop.outer_pre[i].__class__.__name__ == "IvieLoop":
                    self.get_body(loop.outer_pre[i], body)

            for i in range(0, len(loop.outer_post)):
                if loop.outer_post[i].__class__.__name__ == "IvieLoop":
                    self.get_body(loop.outer_post[i], body)

    def update_body(self, loop, body):
        if loop.iterators.name == self.remaining.name:
            loop.body += body
        else:
            for bod in loop.outer_pre + loop.body + loop.outer_post:
                if bod.__class__.__name__ == "IvieLoop":
                    self.update_body(bod, body)


    def cleanup(self, loop):
        for i in range(len(loop.body)-1, -1, -1):
            if loop.body[i].__class__.__name__ == "IvieLoop":
                if loop.body[i].iterators.name == self.fused.name:
                    del loop.body[i]
                else:
                    self.cleanup(loop.body[i])

        for i in range(len(loop.outer_pre)-1, -1, -1):
            if loop.outer_pre[i].__class__.__name__ == "IvieLoop":
                if loop.outer_pre[i].iterators.name == self.fused.name:
                    del loop.outer_pre[i]
                else:
                    self.cleanup(loop.outer_pre[i])

        for i in range(len(loop.outer_post)-1, -1, -1):
            if loop.outer_post[i].__class__.__name__ == "IvieLoop":
                if loop.outer_post[i].iterators.name == self.fused.name:
                    del loop.outer_post[i]
                else:
                    self.cleanup(loop.outer_post[i])


    def apply_transformation(self, ivieprog):

        isl_schedules = ivieprog.isl_loop_schedules
        LOOPS = ivieprog.loops
        STATEMENTS = ivieprog.statements
        self.legality_check(STATEMENTS)        
        #self.update_isl_schedules(isl_schedules)        

        for loop in LOOPS:
            self.update_merged_statement(loop)

        self.fused.mark_as_garbage()


        oldbody = []
        for i in range(0, len(LOOPS)):
            self.get_body(LOOPS[i], oldbody)
            #self.update_body(LOOPS[i], oldbody)
        
        for i in range(0, len(LOOPS)):
            self.update_body(LOOPS[i], oldbody)
        
        for i in range(len(LOOPS)-1, -1, -1):
            if LOOPS[i].iterators.name == self.fused.name:
                del LOOPS[i]
            else:
                self.cleanup(LOOPS[i])



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
        

class Stripmine():
  
    def __init__(self, label, loopin, lrank, factor):
        self.label = label
        self.loopin = loopin
        self.lrank = lrank
        self.factor = factor
        self.apply_stripmine(1)

    def debug_print(self):
        string = colored("Stripmine ", "green", attrs=["bold"]) \
                 + self.iterator.debug_print() + " with " \
                 + self.iterator.tile_parent.debug_print()
        return string


    def apply_stripmine(self, depth):

        loopout = deepcopy(self.loopin)

        print loopout.iterator.name
      
        if loopout.iterator.name == "i" + self.lrank:
            print "hurray"
        else:
            for bod in loopout.body:
                if bod.__class__.__name__ == "Loop":
                    bod.apply_stripmine(depth)
    
        # depth = 1
        # if lrank == 1:
        #     pass
        # else:
            
        
    #     #self.iterator.set_tile_parent(self.tile_iterator)
    #     new_minbound = self.iterator.tile_parent.name
    #     new_maxbound = "min(" + self.iterator.tile_parent.maxbound + ", "
    #     new_maxbound += self.iterator.tile_parent.name + " + " + self.iterator.tile_parent.stride + ")"
    #     self.iterator.update_minbound(new_minbound)
    #     self.iterator.update_maxbound(new_maxbound)
    #     self.iterator.tile_parent.kind = self.iterator.kind
    #     self.iterator.tile_parent.parallelism = self.iterator.parallelism
    #     if self.iterator.private_variables != None:
    #         self.iterator.tile_parent.private_variables = self.iterator.private_variables.append(self.iterator.name)
    #     else:
    #         self.iterator.tile_parent.private_variables = [self.iterator.name]
    #     self.iterator.tile_parent.schedule = self.iterator.schedule
    #     self.iterator.tile_parent.set_permutability(self.iterator.permutable)


    # def update_loop(self, loop):
    #     for i in range(0, len(loop.body)):
    #         if loop.body[i].__class__.__name__ == "IvieLoop":
    #             if loop.body[i].iterators.name == self.iterator.name:
              
    #                 capsule = IvieLoop(self.iterator.tile_parent, [loop.body[i]])
    #                 loop.body[i] = capsule
    #             else:
    #                 self.update_loop(loop.body[i])
    


    # def apply_transformation(self, ivieprog):  
    #     LOOPS = ivieprog.loops

    #     self.legality_check()
    #     self.apply_stripmine()
    #     #self.update_schedules(isl_schedules)

    #     for i in range(0, len(LOOPS)):
    #         if LOOPS[i].iterators.name == self.iterator.name:
    #             capsule = IvieLoop(self.iterator.tile_parent, [LOOPS[i]])
    #             LOOPS[i] = capsule
    #         else:
    #             self.update_loop(LOOPS[i])


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

                    
class IvieTransformationInterchange():
    """ Types:
    iterator1: IvieIterator
    iterator2: IvieIterator. """


    def __init__(self, iterator1, iterator2):
        self.iterator1 = iterator1
        self.iterator2 = iterator2
        self.set_atomic = []
    
    def debug_print(self):
        string = colored("Interchange ", "green", attrs=["bold"]) \
                 + self.iterator1.debug_print() + " with " \
                 + self.iterator2.debug_print() 
        return string

    

    def legality_check(self, DEPS):
        #### From a fully hand coded program, also providing meta informations
        #### specifying that both iterators are permutable is enough. 
        #### In case no "perm" is specified, then no interchange is possible.
        #### When automating from cfdlang, we can assume that all loops
        #### are permutable


        ## 1. Any of these iterators must be garbage
        if self.iterator1.garbage == True or self.iterator2.garbage == True:
            sys.exit("Cannot apply transformation on garbage iterator")

        ## 2. If they are not garbage then thy must be permutable
        if self.iterator1.permutable == False or self.iterator2.permutable == False:
            sys.exit("Cannot interchange non permutable iterator")
            
        ## 3. If they are permutable then we must check if there are any 
        ##    write-after-write dependency on one of them (if parallel)
        ##    In this case, the waw dependency is deleted and the 
        ##    concerned statement is set to atomic
        

        if self.iterator1.permutable == True:
            if self.iterator1.kind == "piter":
                for i in range(0, len(DEPS)):
                    ## If WAW on the same element in the same instruction
                    ## ACHTUNG: broken!! 
                    if DEPS[i].garbage == False and DEPS[i].type == "waw" and \
                       DEPS[i].source.string == DEPS[i].sink.string:
                        for index in DEPS[i].source.indexes:
                            if (index.name == self.iterator1.name) or (index.parent != None and index.parent.name == self.iterator1.name):
                                self.set_atomic.append(DEPS[i].source)
                                DEPS[i].mark_as_garbage()
                                #print "[Warning][Loop interchange] WAW dependency on interchanged iterator; setting concerned statements as atomic"

                
                        

    def update_iterators(self, loop):
        loop.flag = False

        #### Exchange parallel contexts

        kind1 = self.iterator1.kind
        partype1 = self.iterator1.parallelism
        private1 = self.iterator1.private_variables

        kind2 = self.iterator2.kind
        partype2 = self.iterator2.parallelism
        private2 = self.iterator2.private_variables

        self.iterator1.kind = kind2
        self.iterator1.parallelism = partype2
        self.iterator1.private_variables = private2

        self.iterator2.kind = kind1
        self.iterator2.parallelism = partype1
        self.iterator2.private_variables = private1

        if self.iterator1.private_variables != None:
            if self.iterator1.name in self.iterator1.private_variables:
                self.iterator1.private_variables.remove(self.iterator1.name)
                self.iterator1.private_variables.append(self.iterator2.name)
        if self.iterator2.private_variables != None:
            if self.iterator2.name in self.iterator2.private_variables:
                self.iterator2.private_variables.remove(self.iterator2.name)
                self.iterator2.private_variables.append(self.iterator1.name)

        if loop.iterators.name == self.iterator2.name and loop.flag == False:
            loop.iterators = self.iterator1
            loop.flag = True
        if loop.iterators.name == self.iterator1.name and loop.flag == False:
            loop.iterators = self.iterator2
            loop.flag = True
        
        ### Set to atomic statement that requires that
        for bod in loop.body:
            if bod.__class__.__name__ == "IvieLoop":
                self.update_iterators(bod)
            elif bod.__class__.__name__ == "IvieStatement":
                if bod.store in self.set_atomic:
                    bod.update_atomicity(True)


    def apply_transformation(self, ivieprog):
        isl_schedules = ivieprog.isl_loop_schedules
        LOOPS = ivieprog.loops
        DEPS = ivieprog.dependencies
        self.legality_check(DEPS)

        for loop in LOOPS:
            self.update_iterators(loop)

        ## Check if both concerned iterators
        ## are in the same sched. If not
        ## interchanging is not possible
        """
        for i in range(0, len(isl_schedules)):
            if self.iterator1 in isl_schedules[i].schedule_object and \
               self.iterator2 in isl_schedules[i].schedule_object:
                ## We are now going to exchange their position 
                pos1 = isl_schedules[i].schedule_object.index(self.iterator1)
                pos2 = isl_schedules[i].schedule_object.index(self.iterator2)
                isl_schedules[i].schedule_object[pos1] = self.iterator2
                isl_schedules[i].schedule_object[pos2] = self.iterator1
        """


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

            

        

