import numpy as np
import ja3_distance as ja3dist
import random
import sys

def init_centroids(list, K):
    centroids = ["" for i in range(K)]
    for i in range(0,K):
        centroids[i] = list[random.randrange(0,len(list))]
    return centroids

def find_closest_centroids(list, centroids):
    idx = np.zeros(len(list), dtype=int)
    for i in range(0,len(list)):
        tmp_idx=0
        tmp_dist=sys.maxsize
        for j in range(0,len(centroids)):
            if not centroids[j] == None:
                new_dist=np.sum(ja3dist.distance(list[i],centroids[j])**2)
                if new_dist < tmp_dist:
                    tmp_dist = new_dist
                    tmp_idx = j
        idx[i]=tmp_idx
    return idx

def find_new_centroids(list, idx, K):
    centroids = ["" for i in range(K)]
    for i in range(0,K):
        #print("Looking for new centroid "+str(i))
        idx_i = [j for j in range(len(idx)) if idx[j]==i]
        #print("Group has "+str(len(idx_i))+" elements")
        if not len(idx_i)==0:
            dists = np.zeros((len(idx_i),len(idx_i)),dtype=int)
            tmp_smallest_avg = sys.maxsize
            tmp_smallest_idx = 0
            for u in range(0,len(idx_i)):
                tmp_sum = 0
                for v in range(0,len(idx_i)):
                    if not u == v:
                        tmp_sum = ja3dist.distance(list[idx_i[u]],list[idx_i[v]])
                tmp_avg = tmp_sum/(len(idx_i))
                if tmp_avg < tmp_smallest_avg:
                    tmp_smallest_avg = tmp_avg
                    tmp_smallest_idx = u
            #print("Smallest dist: "+str(tmp_smallest_avg))
            centroids[i] = list[idx_i[tmp_smallest_idx]]
        else:
            #print("Centroid "+str(i)+" is empty.")
            centroids[i] = None
    return centroids

def k_means(list, K, max_iter):
    centroids = init_centroids(list,K)
    for i in range(1,max_iter):
        #print("Iteration "+str(i))
        idx = find_closest_centroids(list, centroids)
        centroids = find_new_centroids(list,idx,K)
    return dict(zip(list,idx)),centroids

# Calculate similarity of top indexes
def get_top_similarity(indexes,ja3s):
    if len(ja3s)==0:
        return 0
    similarity = 0
    top_indexes = []
    for ja3 in ja3s:
        top_indexes.append(indexes[ja3])
    for i in range(0,len(top_indexes)):
        if top_indexes.count(top_indexes[i])-1 > similarity:
            similarity = similarity+1
        if similarity == len(top_indexes):
            return similarity/len(top_indexes)
    return similarity/len(top_indexes)

# Find out which group the ja3 is closest to (return index)
def get_index(centroids, ja3):
    closest = ''
    index = ''
    dist = 100000
    for ind, c in enumerate(centroids):
        if c == None:
            continue
        curr_dist = ja3dist.distance(ja3,c)
        if int(curr_dist) < dist:
            dist = curr_dist
            closest = c
            index=ind
    return index,dist,closest
