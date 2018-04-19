
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
        return collect_ranks(dic, expr.left)
    else:
        dic = get_rank(expr.left, dic)
        return dic
    
    if expr.right.__class__.__name__ == "Expression":
        return collect_ranks(list, expr.right)
    else:
        dic = get_rank(expr.left, dic)
        return dic


def get_constraints(branch, consts):
    for i in range(0, len(branch.tensor.shape)):
        c = " 0 <= " +  branch.access[i] + " < " + branch.tensor.shape[i]

        consts.append(c)

    return consts
        
def collect_constraints(consts, expr):
    if expr.left.__class__.__name__ == "Expression":
        return collect_constraints(consts, expr.left)
    else:
        consts = get_constraints(expr.left, consts)
        return consts

    if expr.right.__class__.__name__ == "Expression":
        return collect_constraints(consts, expr.right)
    else:
        consts = get_constraints(expr.left, consts)
        return consts
