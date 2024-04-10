from wmd import WMD
import numpy as np
import math
import libwmdrelax

def euclidean_dist(point1, point2):
    if len(point1) != len(point2):
        raise ValueError("Points must have the same number of dimensions")

    squared_distance = sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2))
    distance = math.sqrt(squared_distance)
    return distance

def par_to_vecs(par,vectorisation_function):
    return [vectorisation_function(sent) for sent in par]

def dist(vecs1,vecs2):
    vec_union = list(vecs1 + vecs2)
    n1,n2 = len(vecs1),len(vecs2)
    n = len(vec_union)
    dist_ = np.zeros((n,n))
    for i in range(n):
        for j in range(i):
            dist_[i,j] = dist_[j,i] = euclidean_dist(vec_union[i],vec_union[j])

    nw1 = [1. for i in range(n1)]+[0. for i in range(n2)]
    nw2 = [0. for i in range(n1)] +[1. for i in range(n2)]
    return np.array(dist_,dtype=np.float32),np.array(nw1,dtype=np.float32),np.array(nw2,dtype=np.float32)


def pars_dist_emd_emdrelaxed(par1,par2,vectorisation_function):
    relax_cache = libwmdrelax.emd_relaxed_cache_init(int(100)) 
    cache = libwmdrelax.emd_cache_init(int(100)) 
 
    vecs1,vecs2 = par_to_vecs(par1,vectorisation_function),par_to_vecs(par2,vectorisation_function)
    dist_,nw1,nw2 = dist(vecs1,vecs2)
    emd = libwmdrelax.emd(nw1,nw2,dist_,cache)
    emd_relaxed = libwmdrelax.emd_relaxed(nw1,nw2,dist_,relax_cache)
    return emd,emd_relaxed

   


    
