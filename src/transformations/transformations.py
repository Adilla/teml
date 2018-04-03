from include.arrays import *
from include.iterators import *
from include.loops import *
from include.program import *
from include.transformations import *


def set_label(loop, outerlabel, outerobject, count, all_schedules):
    label = outerlabel + str(count) + "," + loop.iterators.name + ","
    object_ = outerobject + [count] + [loop.iterators]
    loop.update_label(label) 
    stmtcount = 0
    loopcount = 0
    for bod in loop.body:
        if bod.__class__.__name__ == "IvieStatement":
            stmtlabel = loop.label + str(stmtcount) + "]"
            bod.update_label(stmtlabel)
            stmtobj = []
            stmtobj += object_ + [stmtcount]
            islsched = IslSchedule(bod.name, stmtobj)
            all_schedules.append(islsched)
            stmtcount += 1
    
        elif bod.__class__.__name__ == "IvieLoop":
            
            set_label(bod, loop.label, object_, loopcount, all_schedules)
            loopcount += 1

            
def build_isl_loop_schedule(ivieprog):
    LOOPS = ivieprog.loops
    all_schedules = []
    strr = "["
    count = 0
    for loop in LOOPS:
        set_label(loop, strr, [], count, all_schedules)
        count += 1
    ivieprog.set_isl_loop_schedules(all_schedules)


def build_isl_domain(ivieprog):
    isl_domains = []
    str_schedules = []
    stmtcount = 0
    isl_prog = "{"

    maxlen = len(ivieprog.isl_loop_schedules[0].schedule_object)
    for sched in ivieprog.isl_loop_schedules[1:]:
        if len(sched.schedule_object) > maxlen:
            maxlen = len(sched.schedule_object)

    ivieprog.set_max_schedule(maxlen)

    for sched in ivieprog.isl_loop_schedules:
        string_sched = sched.translate_into_string(ivieprog.max_schedule)
        domain = []
        namelist = "["
        string = ""
        if not isinstance(sched.schedule_object[1], int):
            first = sched.schedule_object[1]
 
            minbound = first.minbound
            maxbound = first.maxbound
            stride = first.stride
            name = first.name
            namelist += name 
            string +=  minbound + " <= " + name + " < " + maxbound       
            # For the stride 
            string += " and " + stride + " * floor((-1 + " + name + ") / " + stride + ") = -1 + " + name

        for i in range(0, len(sched.schedule_object[3:]), 2):
            # To skip integers
            elt = sched.schedule_object[3:][i]
            if not isinstance(elt, int):
                name = elt.name
                namelist += ", " + name
                minbound = elt.minbound
                maxbound = elt.maxbound 
                stride = elt.stride
                string += " and " + minbound + " <= " + name + " < " + maxbound 
                # For the stride 
                string += " and " + stride + " * floor((-1 + " + name + ") / " + stride + ") = -1 + " + name
        namelist += "]"
        stmtcount += 1
        #str_schedules.append("{ S" + str(stmtcount)  + namelist +  " -> " + string_sched + " }")
        str_schedules.append(sched.name + namelist +  " -> " + string_sched + " }")
        # Need to also handled parameters with [N] ->

        domain = sched.name + namelist + " -> " + string_sched + " : "
        #domain = "S" + str(stmtcount) + namelist + " -> " + string_sched + " : "
        #domain = "DS"+ str(stmtcount) + " := { S" + str(stmtcount) + namelist + ": " 
        domain += string + ";"
        isl_prog += domain
        isl_domains.append(domain)
    isl_prog += "}"

    ivieprog.set_isl_program(isl_prog)
    ivieprog.set_isl_loop_schedules_str(str_schedules)
    ivieprog.set_isl_loop_domains(isl_domains)


def execute_scheduler(ivieprog):
    for scheduled in ivieprog.scheduler:
        scheduled.apply_transformation(ivieprog)
