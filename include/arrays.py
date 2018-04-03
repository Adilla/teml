from copy import deepcopy, copy
from termcolor import colored
from loops import *
import sys

class IvieArray():
    ## These memory placement attribute only apply to 
    ## physical arrays. For virtual arrays, this is 
    ## always set to None.
    align = None
    interleaved = None
    onnode = None
    forbid_purge = False
    nb_pages = None
    nb_elt_per_page = None
    elt_ranges = None
    reduction = None
    cfdmesh = False

    def set_interleaved(self, nbpages):
        self.interleaved = nbpages             
        self.onnode = None

    def set_onnode(self, nodeid):
        self.onnode = nodeid
        self.interleaved = None

    def set_nb_pages(self, nb):
        self.nb_pages = nb

    def set_nb_element_per_page(self, nb):
        self.nb_elt_per_page = nb

    def set_elt_ranges(self, ranges):
        self.elt_ranges = ranges

    def set_forbid_purge(self, boolean):
        ### For CFD.
        self.forbid_purge = boolean

    
    """
    def prettyprint_C_declaration(self):
        datatype = None
        sizes = None
        if self.__class__.__name__ != "IvieArrayArray":
            datatype = self.parent.datatype
            sizes = self.parent.sizes
        else:
            datatype = self.datatype
            sizes = self.sizes

        string = datatype + " " + self.name
        for size in sizes:
            string += "[" + size + "]"
        string += ";\n"
        return string

    def prettyprint_C_allocation(self):
        string = ""
        if self.interleaved != None:
            string = self.name + " = numa_alloc_interleaved(" +  self.interleaved + ");\n"
        elif self.onnode != None:
            string = self.name + " = numa_alloc_onnode(" +  self.onnode + ");\n"      
        return string
    """


class IvieArrayArray(IvieArray):
    """ Types:
    name:      string
    dimension: string
    datatype:  string
    sizes:     list of strings """

    def __init__(self, name, dimension, datatype, sizes):
        self.name = name
        self.dimension = dimension
        self.datatype = datatype 
        self.sizes = sizes

    def debug_print(self):
        string = colored("ARRAY:", "red", attrs=["bold"]) + colored(" " + self.name, attrs=["bold"]) + " {" + self.dimension + ", " + self.datatype + ", [" 
        for size in self.sizes:
            string += size + " "
        string += "]}"
        return string


class IvieArrayReplicate(IvieArray):
    """ Types:
    name:   string
    parent: IvieArray """

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent 
        self.dimension = parent.dimension
        self.datatype = parent.datatype
        self.sizes = parent.sizes

    def debug_print(self):
        string = colored("Replicate: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" + self.parent.debug_print() + "}"
        return string

class IvieArrayTranspose(IvieArray):
    """ Types:
    name:   string
    parent: IvieArray
    rank1:  string
    rank2:  string """

    def __init__(self, name, parent, rank1, rank2):
        self.name = name
        self.parent = parent
        self.rank1 = rank1
        self.rank2 = rank2
        self.dimension = parent.dimension
        self.sizes = parent.sizes
        self.datatype = parent.datatype
        self.loop = None

    def debug_print(self):
        string = colored("Transpose: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + "{" + self.parent.debug_print() + ", " + self.rank1 + ", " + self.rank2 + "}"
        return string

    ## DEPS useless here
    def build(self, iterators, DEPS, V_ARRAYS):
        ### At = transpose(A, 1, 2)                                                                                                                            
        ### ...                                                                                                                                               
        ### build(At, [ta_1, ta_2])                                                                                                                            
        ###                                                                                                                                      
        ### must generate on of the following loops                                                                                             
        ###       
        ### Av = vtranspose(A, 1, 2)        
        ### with ta_1 as siter:          
        ###   with ta_2 as siter:        
        ###     At[ta_1][ta_2] = _tr(Av[ta_1][ta_2])   
        ###         
        ###   OOR  
        ###       
        ### Av = vtranspose(At, 1, 2)                    
        ### with ta_1 as siter:                         
        ###   with ta_2 as siter:                      
        ###     Av[ta_1][ta_2] = _tr(A[ta_1][ta_2])   
        ###                                          
        ### For the moment, we handle regular reads (option 2)                     
        ### By default, iterators are set as permutable and parallel
        ### TODO: fix bug when build is within loop. 
        ### Create statement and innermost loop                                       

        for iter_ in iterators:
            iter_.set_kind("piter")
            pos = iterators.index(iter_)
            iter_.set_private_variables(iterators[pos:])
            iter_.set_permutability(True)
        
        source = self.parent
        newvirt = IvieArrayVtranspose(self.name + "_t",  self, self.rank1, self.rank2)
        V_ARRAYS.append(newvirt)
        written = IvieArgument(newvirt, iterators, "")
        ### Perte d'information pour les index complique!
        read    = IvieArgument(self.parent, iterators, "")
        statement = IvieStatement("_transpose" + self.name, written, [read])

        innermost = IvieLoop(iterators[-1], [statement])
    
        ### Build loop from innermost to outermost dimension                   
        for i in range(len(iterators)-2, -1, -1):
            innermost = IvieLoop(iterators[i], [innermost])
        
        self.loop = innermost
        self.loop.flag_not_in_mesh = True
        return self.loop

class IvieArrayVtranspose(IvieArray):
    """ Types:
    name:   string
    parent: IvieArray
    rank1:  string
    rank2:  string
    """
    def __init__(self, name, parent, rank1, rank2):
        self.name = name
        self.parent = parent
        self.rank1 = rank1
        self.rank2 = rank2
        self.dimension = parent.dimension
        self.sizes = parent.sizes
        self.datatype = parent.datatype

    def debug_print(self):
        string = colored("Virtual transpose: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" + self.parent.debug_print() + ", " + self.rank1 + ", " + self.rank2 + "}"
        return string

class IvieArraySelect(IvieArray):
    """ Types:
    name:  string
    pairs: list of pairs of [string, IvieArray] """

    def __init__(self, name, pairs):
        self.name = name
        self.conditions = pairs

    def debug_print(self):
        string = colored("Select: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" 
        for condition in self.conditions:
            string += "[" + condition[0] + ", " + condition[1].debug_print() + "]"
        string += "}"

        return string

### Experimental (CFD)
class IvieArrayIntermediate(IvieArray):
    
    def __init__(self, name, origin):
        self.name = name
        self.parent = origin
        self.dimension = origin.dimension
        self.sizes = origin.sizes
        self.datatype = origin.datatype
        self.forbid_purge = origin.forbid_purge

    def debug_print(self):
        string = colored("Intermediate: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" + self.origin.debug_print() + "}"
        return string


class IvieArrayScalarMul(IvieArray):
    def __init__(self, name, parent1, parent2):
        self.name = name
        self.parent1 = parent1
        self.parent2 = parent2
        ## Parent 1 is the scalar! Therefore, we must take the dimension
        self.datatype = parent2.datatype
        self.dimension = parent2.dimension
        self.sizes = parent1.sizes    
        self.loop = None

    def debug_print(self):
        string = colored("ScalarMul: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" + self.parent1.debug_print() + ", " + self.parent2.debug_print() + "}"
        return string

    ## V_ARRAYS useless here
    def build(self, iterators, DEPS, V_ARRAYS):
        for iter_ in iterators:
            iter_.set_kind("piter")
            pos = iterators.index(iter_)
            iter_.set_private_variables(iterators[pos:])
            iter_.set_permutability(True)

        written = IvieArgument(self, iterators, "")
        read1 = IvieArgument(self.parent1, [], "")
        read2 = IvieArgument(self.parent2, iterators, "")

        statement = IvieStatement("_scalarmul" + self.name, written, [read1, read2])
        
        # ### Creating required dependencies 
        # ### For the moment, enough for interchanges
        # dep1 = IvieDependency("raw", written, written, iterators[0].name + " != 0")
        # dep2 = IvieDependency("waw", written, written, iterators[0].name + " != 0")
        # dep3 = IvieDependency("rar", written, written, iterators[0].name + " != 0")
        # DEPS.append(dep1)
        # DEPS.append(dep2)
        # DEPS.append(dep3)


        innermost = IvieLoop(iterators[-1], [statement])
        
        for i in range(int(self.dimension)-2, -1, -1):
            innermost = IvieLoop(iterators[i], [innermost])
            
        self.loop = innermost
        return self.loop



class IvieArrayEntrywise(IvieArray):
    def __init__(self, name, parent1, parent2, type):
        self.name = name
        self.parent1 = parent1
        self.parent2 = parent2
        ## Either parent1 or parent2 for the 3 followings. Doesnt matter
        self.datatype = parent1.datatype
        self.dimension = parent1.dimension
        self.sizes = parent1.sizes    
        self.loop = None
        self.type = type
        self.reduction = False

    def debug_print(self):
        string = colored("Entrywise: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" + self.parent1.debug_print() + ", " + self.parent2.debug_print() + "}"
        return string

    ## V_ARRAYS useless here
    def build(self, iterators, DEPS, V_ARRAYS):
        ### Construction d'un template, pour le moment je ne 
        ### sais pas quel sont les iterateurs qui seront assignes
        ### a cette boucle.

        ### Attention, le outerproduct n'est pas commutatif
        ### L'ordre specifie des 'parent' sera l'ordre 
        ### defini pour assigner les iterateurs plus tard
        for iter_ in iterators:
            iter_.set_kind("piter")
            pos = iterators.index(iter_)
            iter_.set_private_variables(iterators[pos:])
            iter_.set_permutability(True)

        written = IvieArgument(self, iterators, "")
        read1 = IvieArgument(self.parent1, iterators, "")
        read2 = IvieArgument(self.parent2, iterators, "")

        statement = IvieStatement("_entrywise" + self.name, written, [read1, read2])

        
        # ### Creating required dependencies 
        # ### For the moment, enough for interchanges
        # dep1 = IvieDependency("raw", written, written, iterators[0].name + " != 0")
        # dep2 = IvieDependency("waw", written, written, iterators[0].name + " != 0")
        # dep3 = IvieDependency("rar", written, written, iterators[0].name + " != 0")
        # DEPS.append(dep1)
        # DEPS.append(dep2)
        # DEPS.append(dep3)


        ## The structure of the entrywise multiplication allows to recognize
        ## which iterators could be unrolled and/or vectorized.
        ## iterators[j-1] is the loop enclosing the 
        ## reduction loop. Find a way to simd-ize this one.

        ## The way variants are generated could be cleaner... 
        ## For the moment, we do it as follows.

        v = 1
        m = len(iterators)
        j = 3
        ### Combining full unrolling on one dimension and vectorization of previous one
        for p in range(j, -1, -1):
            if p == 3:
                ## Trick to align variants to those generated by contractions
                with open("variant_" + str(v) + ".txt", "a+") as source:
                    source.write("parallelize(" + iterators[1].name + ", VEC, None, None)\n")
                    source.write("unroll(" + iterators[2].name + ", " + iterators[2].maxbound + ")\n")
                v += 1
            else:
                if p == 2:
                    with open("variant_" + str(v) + ".txt", "a+") as source:
                        source.write("parallelize(" + iterators[p-1].name + ", VEC, None, None)\n")
                        source.write("unroll(" + iterators[p].name + ", " + iterators[p].maxbound + ")\n")
                        v += 1
                else:
                    if p-1 >= 0:
                        with open("variant_" + str(v) + ".txt", "a+") as source:
                            source.write("parallelize(" + iterators[p-1].name + ", VEC, None, None)\n")
                            source.write("unroll_and_fuse(" + iterators[p].name + ", " + iterators[p].maxbound + ")\n")
                        v += 1


        ### Combining unrolling and vectorization on same dimension. 
        ### Unrolling beyond half the concerned loop seems pointless.
        for p in range(j, -1, -1):
            if p == 3:
                count = 2
                while count < ((int(iterators[2].maxbound) / 2) + 1):
                    with open("variant_" + str(v) + ".txt", "a+") as source:
                        source.write("unroll(" + iterators[2].name + ", " + str(count) + ")\n")
                        source.write("parallelize(" + iterators[2].name + ", VEC, None, None)\n")
                        v += 1
                    count *= 2
            else:
                if p == 2:
                    count = 2
                    while count < ((int(iterators[p].maxbound) / 2) + 1):
                        with open("variant_" + str(v) + ".txt", "a+") as source:
                            source.write("unroll(" + iterators[p].name + ", " + str(count) + ")\n")
                            source.write("parallelize(" + iterators[p].name + ", VEC, None, None)\n")
                            v += 1
                        count *= 2
                else:
                    count = 2
                    while count < ((int(iterators[p].maxbound) / 2) + 1):
                        with open("variant_" + str(v) + ".txt", "a+") as source:
                            source.write("unroll_and_fuse(" + iterators[p].name + ", " + str(count) + ")\n")
                            source.write("parallelize(" + iterators[p].name + ", VEC, None, None)\n")
                            v += 1
                        count *= 2


        ## Applying vectorization only and letting the compiler do the unrolling.
        for p in range(m, -1, -1):
            if p == 3:
                with open("variant_" + str(v) + ".txt", "a+") as source:
                    source.write("parallelize(" + iterators[2].name + ", VEC, None, None)\n")
                v += 1
            else:
                with open("variant_" + str(v) + ".txt", "a+") as source:
                    source.write("parallelize(" + iterators[p].name + ", VEC, None, None)\n")
                v += 1



        ## Applying unrolling only.
        for p in range(j, -1, -1):
            if p == 3:
                count = 2
                while count < ((int(iterators[2].maxbound) / 2) + 1):
                    with open("variant_" + str(v) + ".txt", "a+") as source:
                        source.write("unroll(" + iterators[2].name + ", " + str(count) + ")\n")
                        v += 1
                    count *= 2
            else:
                if p == 2:
                    count = 2
                    while count < ((int(iterators[p].maxbound) / 2) + 1):
                        with open("variant_" + str(v) + ".txt", "a+") as source:
                            source.write("unroll(" + iterators[p].name + ", " + str(count) + ")\n")
                            v += 1
                        count *= 2
                else:
                    count = 2
                    while count < ((int(iterators[p].maxbound) / 2) + 1):
                        with open("variant_" + str(v) + ".txt", "a+") as source:
                            source.write("unroll_and_fuse(" + iterators[p].name + ", " + str(count) + ")\n")
                            v += 1
                        count *= 2


        innermost = IvieLoop(iterators[-1], [statement])

        
        for i in range(int(self.dimension)-2, -1, -1):
            innermost = IvieLoop(iterators[i], [innermost])
            
        self.loop = innermost
        return self.loop

        
class IvieArrayContraction(IvieArray):

    def __init__(self, name, parent1, parent2, axes1, axes2):
        self.name = name
        self.parent1 = parent1
        self.parent2 = parent2
        self.axes1 = axes1
        self.axes2 = axes2
        self.datatype = self.parent1.datatype
        ## Dimension is the sum of dimensions minus the number of 
        ## pairs of contractions
        self.dimension = str(int(self.parent1.dimension) + int(self.parent2.dimension) - len(axes1) - len(axes2))
        self.reduction = True
        self.sizes = []

        for i in range(0, len(self.parent1.sizes)):
            if str(i+1) not in self.axes1:
                self.sizes.append(parent1.sizes[i])
        
        
        for i in range(0, len(self.parent2.sizes)):
            if str(i+1) not in self.axes2:
                self.sizes.append(parent2.sizes[i])
  
        
        self.loop = None

        
    def debug_print(self):
        string = colored("Contraction: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" + self.parent1.debug_print() + ", " + self.parent2.debug_print() + "}"
        return string


    def build(self, iterators, DEPS, V_ARRAYS):
    
        ### Construction d'un template, pour le moment je ne 
        ### sais pas quel sont les iterateurs qui seront assignes
        ### a cette boucle.

        ### This builds a naive contraction where last iterator
        ### of list is the iterator that traverses contracted
        ### axes

        for iter_ in iterators:
            iter_.set_kind("piter")
            pos = iterators.index(iter_)
            iter_.set_private_variables(iterators[pos:])
            iter_.set_permutability(True)
         
        ### First position iterator traversing axes then
        ### fill up the rest with the other iterators
        ### in the lexicographical order
        iters1 = [None] * (int(self.parent1.dimension))
        iters2 = [None] * (int(self.parent2.dimension))
        


        k = len(self.axes1)
        for axe in self.axes1:
            iters1[int(axe)-1] = iterators[-k]
            k -= 1

        k = len(self.axes2)
        for axe in self.axes2:
            iters2[int(axe)-1] = iterators[-k]
            k -= 1
        
        #old = deepcopy(iterators)

        j = 0
        for i in range(0, int(self.parent1.dimension)):
            if iters1[i] == None:
                iters1[i] = iterators[j]
                j += 1
            
        offset = int(self.parent1.dimension)-1
        for i in range(0, int(self.parent2.dimension)):
            if iters2[i] == None:
                iters2[i] = iterators[j]
                j += 1
 


        # ### The structure of the contraction allows to recognize
        # ### which iterators could be unrolled and/or vectorized.
        # ### iterators[j-1] is the loop enclosing the 
        # ### reduction loop. Find a way to simd-ize this one.

        # ### The way variants are generated could be cleaner... 
        # ### For the moment, we do it as follows.

        # v = 1
        # ### Combining full unrolling on one dimension and vectorization of previous one
        # for p in range(j, -1, -1):
        #     if p == j:
        #         with open("variant_" + str(v) + ".txt", "a+") as source:
        #             source.write("parallelize(" + iterators[p-1].name + ", VEC, None, None)\n")
        #             source.write("unroll(" + iterators[p].name + ", " + iterators[p].maxbound + ")\n")
        #             v += 1
        #     else:
        #         if p-1 >= 0:
        #             with open("variant_" + str(v) + ".txt", "a+") as source:
        #                 source.write("parallelize(" + iterators[p-1].name + ", VEC, None, None)\n")
        #                 source.write("unroll_and_fuse(" + iterators[p].name + ", " + iterators[p].maxbound + ")\n")
        #                 v += 1

        # ### Combining unrolling and vectorization on same dimension. 
        # ### Unrolling beyond half the concerned loop seems pointless.
        # for p in range(j, -1, -1):
        #     if p == j:
        #         count = 2
        #         while count < ((int(iterators[p].maxbound) / 2) + 1):
        #             with open("variant_" + str(v) + ".txt", "a+") as source:
        #                 source.write("unroll(" + iterators[p].name + ", " + str(count) + ")\n")
        #                 source.write("parallelize(" + iterators[p].name + ", VEC, None, None)\n")
        #                 v += 1
        #             count *= 2
        #     else:
        #         count = 2
        #         while count < ((int(iterators[p].maxbound) / 2) + 1):
        #             with open("variant_" + str(v) + ".txt", "a+") as source:
        #                 source.write("unroll_and_fuse(" + iterators[p].name + ", " + str(count) + ")\n")
        #                 source.write("parallelize(" + iterators[p].name + ", VEC, None, None)\n")
        #                 v += 1
        #             count *= 2

        # ## Applying vectorization only and letting the compiler do the unrolling.
        # for p in range(j, -1, -1):
        #     with open("variant_" + str(v) + ".txt", "a+") as source:
        #         source.write("parallelize(" + iterators[p].name + ", VEC, None, None)\n")
        #     v += 1

        # ## Applying unrolling only.
    
        # for p in range(j, -1, -1):
        #     if p == j:
        #         count = 2
        #         while count < ((int(iterators[p].maxbound) / 2) + 1):
        #             with open("variant_" + str(v) + ".txt", "a+") as source:
        #                 source.write("unroll(" + iterators[p].name + ", " + str(count) + ")\n")
        #                 v += 1
        #             count *= 2
        #     else:
        #         count = 2
        #         while count < ((int(iterators[p].maxbound) / 2) + 1):
        #             with open("variant_" + str(v) + ".txt", "a+") as source:
        #                 source.write("unroll_and_fuse(" + iterators[p].name + ", " + str(count) + ")\n")
        #                 v += 1
        #             count *= 2

        ### Also prepare vtransposes if existing
        tmp_iters1 = []
        tmp_iters2 = []
        
        for i in iters1:
            #print i
            tmp_iters1.append(iterators.index(i))

        permutations = []
        cast = []
        tmp_list = tmp_iters1
        i = 0
        while len(tmp_list) >= 2:
            if tmp_list != []:
                mn = min(tmp_list)
                mx = max(tmp_list)

                if tmp_list.index(mn) != 0:
                    rank1 = tmp_iters1.index(mn) + 1
                    rank2 = i + 1
                    if [rank1, rank2] not in cast:
                        permutations.append([rank1, rank2])
                        cast.append([rank2, rank1])

                        tt1 = iters1[rank1-1]
                        tt2 = iters1[rank2-1]
                        iters1[rank1-1] = tt2
                        iters1[rank2-1] = tt1
                        


                if len(tmp_list) > 2 and tmp_list.index(mx) != len(tmp_list)-1:
                    rank1 = tmp_iters1.index(mx) + 1
                    rank2 = len(tmp_iters1)-i
                    if [rank1, rank2] not in cast:
                        permutations.append([rank1, rank2])
                        cast.append([rank2, rank1])
                        tt1 = iters1[rank1-1]
                        tt2 = iters1[rank2-1]
                        iters1[rank1-1] = tt2
                        iters1[rank2-1] = tt1

            i += 1
            tmp_list = tmp_list[i:-i]
           


        for i in iters2:
            tmp_iters2.append(iterators.index(i))

        permutations2 = []
        cast2 = []
        tmp_list = tmp_iters2
        i = 0
        while len(tmp_list) >= 2:
            if tmp_list != []:
                mn = min(tmp_list)
                mx = max(tmp_list)

                if tmp_list.index(mn) != 0:
                    rank1 = tmp_iters2.index(mn) + 1
                    rank2 = i + 1
                    if [rank1, rank2] not in cast2:
                        permutations2.append([rank1, rank2])
                        cast2.append([rank2, rank1])
                        tt1 = iters2[rank1-1]
                        tt2 = iters2[rank2-1]
                        iters2[rank1-1] = tt2
                        iters2[rank2-1] = tt1

                if len(tmp_list) > 2 and tmp_list.index(mx) != len(tmp_list)-1:
                    rank1 = tmp_iters2.index(mx) + 1
                    rank2 = len(tmp_iters2)-i

                    if [rank1, rank2] not in cast2:
                        permutations2.append([rank1, rank2])
                        cast2.append([rank2, rank1])
                        tt1 = iters2[rank1-1]
                        tt2 = iters2[rank2-1]
                        iters2[rank1-1] = tt2
                        iters2[rank2-1] = tt1

            i += 1
            tmp_list = tmp_list[i:-i]
  

        par1 = self.parent1
        for i in range(len(permutations)-1, -1, -1):
            new = IvieArrayVtranspose(self.parent1.name + "__" + str(i), par1, str(permutations[i][0]), str(permutations[i][1]))
            V_ARRAYS.append(new)
            par1 = new


        par2 = self.parent2
        for i in range(len(permutations2)-1, -1, -1):
            new = IvieArrayVtranspose(self.parent2.name + "__" + str(i), par2, str(permutations2[i][0]), str(permutations2[i][1]))
            V_ARRAYS.append(new)
            par2 = new

            
        
        written = IvieArgument(self, iterators[:-len(self.axes1)], "")
        #read1 = IvieArgument(self.parent1, iters1, "")
        #read2 = IvieArgument(self.parent2, iters2, "")

        read1 = IvieArgument(par1, iters1, "")
        read2 = IvieArgument(par2, iters2, "")


        ### Creating required dependencies 
        ### For the moment, enough for interchanges
        # dep1 = IvieDependency("raw", written, written, iterators[0].name + " != 0")
        # dep2 = IvieDependency("waw", written, written, iterators[0].name + " != 0")
        # dep3 = IvieDependency("rar", written, written, iterators[0].name + " != 0")
        # DEPS.append(dep1)
        # DEPS.append(dep2)
        # DEPS.append(dep3)
        statement = IvieStatement("_contraction" + self.name, written, [read1, read2])
        innermost = IvieLoop(iterators[-1], [statement])
        
        for i in range(len(iterators)-2, -1, -1):
            innermost = IvieLoop(iterators[i], [innermost])
            
        self.loop = innermost

        ##print self.loop.debug_print()
        return self.loop


class IvieArrayOuterproduct(IvieArray):
    
    def __init__(self, name, parent1, parent2):
        self.name = name
        self.parent1 = parent1
        self.parent2 = parent2
        self.datatype = self.parent1.datatype
        # print int(parent1.dimension)
        # print parent2
        # print parent1
        # print int(parent2.dimension)
        self.dimension = str(int(parent1.dimension) + int(parent2.dimension))
        self.sizes = self.parent1.sizes + self.parent2.sizes
    
        self.loop = None

        #print self.debug_print()

    def debug_print(self):
        string = colored("Outerproduct: ", "red", attrs=["bold"]) + colored(self.name, attrs=["bold"]) + " {" + self.parent1.debug_print() + ", " + self.parent2.debug_print() + "}"
        return string

    ## V_ARRAYS useless here
    def build(self, iterators, DEPS, V_ARRAYS):
        ### Construction d'un template, pour le moment je ne 
        ### sais pas quel sont les iterateurs qui seront assignes
        ### a cette boucle.

        ### Attention, le outerproduct n'est pas commutatif
        ### L'ordre specifie des 'parent' sera l'ordre 
        ### defini pour assigner les iterateurs plus tard
        for iter_ in iterators:
            iter_.set_kind("piter")
            pos = iterators.index(iter_)
            iter_.set_private_variables(iterators[pos:])
            iter_.set_permutability(True)

        written = IvieArgument(self, iterators, "")
        read1 = IvieArgument(self.parent1, iterators[:2], "")
        read2 = IvieArgument(self.parent2, iterators[2:], "")

        statement = IvieStatement("_outerproduct" + self.name, written, [read1, read2])

        
        # ### Creating required dependencies 
        # ### For the moment, enough for interchanges
        # dep1 = IvieDependency("raw", written, written, iterators[0].name + " != 0")
        # dep2 = IvieDependency("waw", written, written, iterators[0].name + " != 0")
        # dep3 = IvieDependency("rar", written, written, iterators[0].name + " != 0")
        # DEPS.append(dep1)
        # DEPS.append(dep2)
        # DEPS.append(dep3)


        innermost = IvieLoop(iterators[-1], [statement])

        
        for i in range(int(self.dimension)-2, -1, -1):
            innermost = IvieLoop(iterators[i], [innermost])
            
        self.loop = innermost
        return self.loop
