import subprocess

includes = ["stdio", "stdlib", "unistd", "sys/time", "omp"]
rtclock = "double rtclock() {\n struct timezone Tzp;\n struct timeval Tp;\n int stat;\n stat = gettimeofday(&Tp, &Tzp);"
rtclock += "if (stat != 0) printf(\"Error return from gettimeofday: %d\", stat);\n"
rtclock += "return(Tp.tv_sec + Tp.tv_usec*1.0e-7);\n}"


def add_tensor_param(tensor):
  
    param = tensor.dtype +  " "
    param += tensor.name
    param += "[const restrict " + tensor.shape[0] + "]"
    for sh in tensor.shape:
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

    alloc += " = malloc(sizeof * " + tensor.name + ");\n"


    return alloc

def free(tensor):
    free = "free(" + tensor.name + ");\n"

    return free

def template(name, prog):
    init = prog.tensors
    code = prog.code

    for tensor in init:
        print add_tensor_param(tensor)
    
    filename = "tml." + name 

    with open(filename, "w") as source:
        for include in includes:
            inc = "#include <" + include + ".h>\n"
            source.write(inc)
        source.write("\n")
        source.write(rtclock)
        source.write("\n")

        funcname = "void " + name + "("
        for i in range(0, len(init) - 1):
            tensor = init[i]
            funcname += add_tensor_param(tensor) + ",\n"

        funcname += add_tensor_param(init[-1]) + ") {\n"

        source.write(funcname)


        for tensor in init:
            source.write(initialization(tensor))


        source.write("double begin, end;\n")
        source.write("begin = rtclock();\n")
        source.write(code)
        source.write("end = rtclock();\n")

        source.write("}\n\n");


        source.write("int main(int * argc, char ** argv) {")

        for tensor in init:
            source.write(allocation(tensor))

        
        call = name + "(" + init[0].name
        for tensor in init[1:]:
            call += ", " + tensor.name
            
        call += ");\n"
        source.write(call)
        
        for tensor in init:
            source.write(free(tensor))
            
        source.write("return 0;\n}")

        
            
    bscript = "clang-format tml." + name + "> tml." + name + ".c"

    with open("cbscript.sh", "w") as src:
        src.write(bscript)

    subprocess.call(["zsh", "cbscript.sh"])
    subprocess.call(["rm", "cbscript.sh"])
    subprocess.call(["rm", filename])
