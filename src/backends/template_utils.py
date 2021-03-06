import subprocess

includes = ["stdio", "stdlib", "unistd", "sys/time", "omp"]
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

def hilbert_initialization(tensor):
    nest = ""
    out = tensor.name
    cond = None

    for i in range(0, len(tensor.shape)):
        r = str(i+1)
        nest += "for (i" + r + " = 0; i"+ r + " < " + tensor.shape[i] + "; i" + r + "+= 1) {\n"
        out += "[i" + r + "]"
    if cond != None:
        nest += cond
    nest += out + " = " + tensor.initvalue + " / (i1 + i2 - 1);\n"
    for sh in tensor.shape:
        nest += "}\n"

    return nest
    

def initialization(tensor):
    nest = ""
    out = tensor.name
    cond = None


    ## For matrices only
    if tensor.inittype == "identity":
        cond = "if (i1 == i2)\n"

    if tensor.inittype == "shift_lower":
        cond = "if (i2 == (i1 + 1))\n"

    if tensor.inittype == "shift_upper":
        cond = "if (i2 == (i1 - 1))\n"
        
    
    for i in range(0, len(tensor.shape)):
        r = str(i+1)
        nest += "for (i" + r + " = 0; i"+ r + " < " + tensor.shape[i] + "; i" + r + "+= 1) {\n"
        out += "[i" + r + "]"
    if cond != None:
        nest += cond
    nest += out + " = " + tensor.initvalue + ";\n"
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
    codes = prog.code

    print codes
    for i in range(0, len(codes)):
        code = codes[i]
        filename = "tml." + name + "_" + str(i + 1)

        variant(filename, init, code, prog, name)
                    
        bscript = "clang-format tml." + name + "_" + str(i+1) + "> " + path + "tml." + name + "_" + str(i + 1) + ".c"

        with open("cbscript.sh", "w") as src:
            src.write(bscript)

        subprocess.call(["zsh", "cbscript.sh"])
        subprocess.call(["rm", "cbscript.sh"])
        subprocess.call(["rm", filename])


def variant(filename, init, code, prog, name):
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

        ### Temporary hack: I am assuming a maximum number of iterators.
        ### I still need to fix more nicely this issue.
        for i in range(1, 9):
            iterators += "i" + str(i) + ", "
        
        # iterators = "int "
        # for i in range(1, prog.maxiter):
        #     iterators += "i" + str(i) + ", "

        iterators += "i" + str(i+1)

        iterators += ";\n\n"
        source.write(iterators)

        for tensor in init:
            if tensor.inittype == "hilbert":
                source.write(hilbert_initialization(tensor))
            else:
                source.write(initialization(tensor))

        source.write("\n")
        source.write("double begin, end;\n")
        source.write("begin = rtclock();\n")
        source.write(code)
        source.write("end = rtclock();\n")
        source.write("printf(\"Time: %0.6lfs\\n\", end - begin);\n")
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

        
