from copy import deepcopy, copy
from termcolor import colored
import sys
        



class IslSchedule():
    """ Types:
    schedule_object: list of integers and IvieIterators."""
    
    def __init__(self, name, objects):
        #self.schedule_string = string
        #self.schedule_list_string = list_string
        self.name = name
        self.schedule_object = objects
    

    def debug_print(self):
        string = "## Begin [\n"
        for obj in self.schedule_object:
            if isinstance(obj, int):
                string += str(obj)
            else:
                string += obj.debug_print()
            string += ", \n"

        string += "] ## End"
        return string

    def translate_into_string(self, maxlen):
        string = "[" + str(self.schedule_object[0])
        itertypes = ["IvieIteratorIterator", "IvieIteratorTile", 
                     "IvieIteratorAxetraversor","IvieIteratorReplicate"]
        for data in self.schedule_object[1:]:
            if isinstance(data, int):
                string += ", " +str(data)
            elif data.__class__.__name__ in itertypes:
                string += ", " + data.name
            else:
                pass

        ## Schedules lengths need to be aligned 
        ## we therefore fill with 0 remaining 
        ## slots
        cp = maxlen
        if len(self.schedule_object) < cp:
            gap = cp - len(self.schedule_object)

            for i in range(0, gap):
                string += ", " + str(0)
            
        string += "]"
        return string
    


class Program():
    tensors = []
    maxiter = 1
    def __init__(self, tensors, code):
        self.tensors = tensors
        self.code = code

    """
    def __init__(self, rarrays, varrays, iterators, loops, scheduler, statements, dependencies):
        self.physical_arrays = rarrays
        self.virtual_arrays = varrays
        self.iterators = iterators
        self.loops = loops
        self.scheduler = scheduler
        self.statements = statements
        self.dependencies = dependencies
        self.isl_loop_schedules_str = None
        self.isl_loop_schedules = None
        self.isl_loop_domains = None
        self.isl_program = None
        self.max_schedule = None
        self.mpi = False
        self.cuda = False
        self.variants = []
    
    def add_program_variant(self, variant):
        self.variants.append(variant)

    def set_isl_loop_schedules(self, schedules):
        self.isl_loop_schedules = schedules

    def set_isl_loop_domains(self, domains):
        self.isl_loop_domains = domains

    def set_isl_program(self, prog):
        self.isl_program = prog
        
    def set_isl_loop_schedules_str(self, str_):
        self.isl_loop_schedules_str = str_

    def set_max_schedule(self, max_):
        self.max_schedule = max_

    def debug_print(self):
        string = " -- Physical arrays -- \n\n"
        for array in self.physical_arrays:
            string += array.debug_print() + "\n"
            
        string += "\n -- Virtual arrays -- \n\n"
        for array in self.virtual_arrays:
            string += array.debug_print()+ "\n"

        string += "\n -- Iterators -- \n\n"
        for iterator in self.iterators:
            string += iterator.debug_print() + "\n"

        string += "\n -- Loops -- \n\n"
        for loop in self.loops:
            string += loop.debug_print() + "\n"
        
        string += "\n -- Transformations scheduler -- \n\n"
        for scheduled in self.scheduler:
            if scheduled != None:
                string += scheduled.debug_print() + "\n"
        
        string += "\n -- Isl loop schedules -- \n\n"
        if self.isl_loop_schedules != None:
            for schedule in self.isl_loop_schedules:
                string += schedule.debug_print() + "\n"

        return string

    """
