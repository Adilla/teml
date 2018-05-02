import subprocess

includes = ["stdio", "stdlib", "unistd", "sys/time", "omp", "libnuma"]
rtclock = "double rtclock() {\n struct timezone Tzp;\n struct timeval Tp;\n int stat;\n stat = gettimeofday(&Tp, &Tzp);"
rtclock += "if (stat != 0) printf(\"Error return from gettimeofday: %d\", stat);\n"
rtclock += "return(Tp.tv_sec + Tp.tv_usec*1.0e-7);\n}"


def add_tensor_param(tensor):
  
    param = tensor.dtype +  " "
    param += tensor.name
    param += "[const restrict " + tensor.shape[0] + "]"
    for sh in tensor.shape[1:]:
        param += "[" + sh + "]"

    return param

def initialization(tensor):
    nest = ""
    out = tensor.name
    for i in range(0, len(tensor.shape)):
        r = str(i+1)
        nest += "for (i" + r + " = 0; i"+ r + " < " + tensor.shape[i] + "; i" + r + "+= 1) {\n"
        out += "[i" + r + "]"
    nest += out + " = " + tensor.initval + ";\n"
    for sh in tensor.shape:
        nest += "}\n"

    return nest


def allocation(tensor):
    alloc = tensor.dtype + " (*" + tensor.name + ")"
    for sh in tensor.shape:
        alloc += "[" + sh + "]"

    allocpolicy = "malloc"
        
    if tensor.allocpolicy == "interleaved":
        allocpolicy = "numa_alloc_interleaved"
    elif tensor.allocpolicy == "onnode":
        allocpolicy = "numa_alloc_onnode"
    elif tensor.allocpolicy == "align":
        allocpolicy = "_mm_malloc"
        
    alloc += " = " + allocpolicy + "(sizeof * " + tensor.name
    if tensor.allocpolicy == "onnode" or tensor.allocpolicy == "align":
        alloc += ", " + tensor.allocattribute
    alloc += ");\n"

    return alloc

def free(tensor):
    free = None

    if tensor.allocpolicy == "interleaved" or tensor.allocpolicy == "onnode":
        free = "numa_free(" + tensor.name + ", sizeof * " + tensor.name + ");\n"
    elif tensor.allocpolicy == "align":
        free = "_mm_free(" + tensor.name + ");\n"
    else:
        free = "free(" + tensor.name + ");\n"

    return free

def template(name, prog, path):
    init = prog.tensors
    code = prog.code


    filename = "tml." + name 

    with open(filename, "w") as source:
        for include in includes:
            inc = "#include <" + include + ".h>\n"
            source.write(inc)
        source.write("\n")
        source.write(rtclock)
        source.write("\n")

        for tensor in init:
            if len(tensor.shape) > prog.maxiter:
                prog.maxiter = len(tensor.shape)
        
        funcname = "void " + name + "("
        for i in range(0, len(init) - 1):
            tensor = init[i]
            funcname += add_tensor_param(tensor) + ",\n"

        funcname += add_tensor_param(init[-1]) + ") {\n\n"

        source.write(funcname)

        iterators = "int "
        for i in range(1, prog.maxiter):
            iterators += "i" + str(i) + ", "

        iterators += "i" + str(i+1)

        iterators += ";\n\n"
        source.write(iterators)

        for tensor in init:
            source.write(initialization(tensor))

        source.write("\n")
        source.write("double begin, end;\n")
        source.write("begin = rtclock();\n")
        source.write(code)
        source.write("end = rtclock();\n")

        source.write("}\n\n");


        source.write("int main(int * argc, char ** argv) {")

        for tensor in init:
            source.write(allocation(tensor))


        source.write("\n")
        call = name + "(" + init[0].name
        for tensor in init[1:]:
            call += ", " + tensor.name
            
        call += ");\n"
        source.write(call)
        source.write("\n")
        for tensor in init:
            source.write(free(tensor))

        source.write("\n")
        source.write("return 0;\n}")

        
            
    bscript = "clang-format tml." + name + "> " + path + "tml." + name + ".c"

    with open("cbscript.sh", "w") as src:
        src.write(bscript)

    subprocess.call(["zsh", "cbscript.sh"])
    subprocess.call(["rm", "cbscript.sh"])
    subprocess.call(["rm", filename])
