
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
