
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
        if data not in dic:
            dic[data] = shape[int(data)-1]

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
