from subprocess import call

source = "helmholtz.ivie"
final  = "helmholtz_comp"
iv     = ".ivie"

compositions = ["\nfuse(i1, j1) \nfuse(i1, k1) \nfuse(i1, l1) \nfuse(i2, j2) \nfuse(i2, k2) \nfuse(i2, l2) \nfuse(i3, j3) \nfuse(i3, k3) \nfuse(i3, l3) \nfuse(j4, k4) \nfuse(j4, l4) \nparallelize(i1, THRD, None, [i2, i3, j4])", \
                "\ninterchange(j2, j4) \ninterchange(j3, j2) \ninterchange(k3, k4) \nparallelize(i1, THRD, None, [i2, i3]) \nparallelize(j1, THRD, None, [j2, j3, j4]) \nparallelize(k1, THRD, None, [k2, k3, k4]) \nparallelize(l1, THRD, None, [l2, l3, l4])", \
                "\ninterchange(j2, j4) \ninterchange(j3, j2) \ninterchange(k3, k4) \nfuse(j1, k1) \nfuse(j4, k2) \nfuse(j2, k4) \nfuse(j3, k3) \nfuse(j1, l1) \nfuse(j4, l2) \nfuse(j2, l3) \nfuse(j3, l4) \nfuse(i1, j1) \nfuse(i2, j4) \nfuse(i3, j2) \nparallelize(i1, THRD, None, [i2, i3, j3])", \
                "\ninterchange(j2, j4) \ninterchange(j3, j2) \ninterchange(k3, k4) \nfuse(j1, k1) \nfuse(j4, k2) \nfuse(j2, k4) \nfuse(j3, k3) \nfuse(j1, l1) \nfuse(j4, l2) \nfuse(j2, l3) \nfuse(j3, l4) \nfuse(i1, j1) \nfuse(i2, j4) \nfuse(i3, j2) \nti1 = tile_iterator(i1, 128) \nti2 = tile_iterator(i2, 128) \nti3 = tile_iterator(i3, 128) \ntile(i1, i2, i3) \nparallelize(ti1, THRD, None, [ti2, ti3, i1, i2, i3, j3])"]


with open(source, "r") as inputfile:
    data = inputfile.read()    
    data += "\n"
    for i in range(1, len(compositions)+1):
        with open(final + str(i) + iv, "w") as outputfile:
            outputfile.write(data + compositions[i-1])


with open("helmholtz.ivie", "a") as inputfile:
    # Just to avoid redundancy
    #inputfile = inputfile.replace("\nparallelize(i1, THRD, None, [i2, i3]) \nparallelize(j1, THRD, None, [j2, j3, j4]) \nparallelize(k1, THRD, None, [k2, k3, k4]) \nparallelize(l1, THRD, None, [l2, l3, l4])", "")
    inputfile.write("\nparallelize(i1, THRD, None, [i2, i3]) \nparallelize(j1, THRD, None, [j2, j3, j4]) \nparallelize(k1, THRD, None, [k2, k3, k4]) \nparallelize(l1, THRD, None, [l2, l3, l4])")
    inputfile.write("\n")
