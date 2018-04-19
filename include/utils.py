import re

def swap(list, e1, e2):
    tmp = list[e2]
    list[e2] = list[e1]
    list[e1] = tmp
    
    return list


def swap_rec(list, pairs, depth, depthmax):
    newlist = list
    if depth < depthmax:
        newlist = swap(list, int(pairs[depth][0])-1, int(pairs[depth][1])-1)
        return swap_rec(newlist, pairs, depth+1, depthmax)
    else:
        return newlist


def get_rank(branch, dic):
    shape = branch.tensor.shape
    access = branch.access

    for data in access:
        index = access.index(data)
        dic.update({data:shape[index]})
        #dic[data] = shape[index]
    return dic

def collect_ranks(dic, expr):
    ## Simplistic implementation
    if expr.left.__class__.__name__ == "Expression":
        dic = collect_ranks(dic, expr.left)
    else:
        dic = get_rank(expr.left, dic)
    
    if expr.right.__class__.__name__ == "Expression":
        dic = collect_ranks(list, expr.right)
    else:
        dic = get_rank(expr.left, dic)

    return dic


def get_constraints(branch, ind, consts):
    print branch.tensor.shape
    print branch.tensor.name
    print branch.access
    for i in range(0, len(branch.tensor.shape)):
        c = "0 <= " +  branch.access[i] + " < " + branch.tensor.shape[i]

        rr = re.compile(r"[i?]\w+\b")
        index = rr.findall(branch.access[i])[0]
        
        #index = "i"+ re.findall(r"i(.)+", branch.access[i])[0]

        if index not in ind:
            ind.append(index)
            

        if c not in consts:
            consts.append(c)

    return consts
        
def collect_constraints(consts, ind, expr):
  
    if expr.left.__class__.__name__ == "Expression":
        consts = collect_constraints(consts, ind, expr.left)
    else:
        consts = get_constraints(expr.left, ind, consts)

    
    if expr.right.__class__.__name__ == "Expression":
        consts = collect_constraints(consts, ind, expr.right)
    else:
        consts = get_constraints(expr.right, ind, consts)
    return consts
