import levenshtein as lv
import numpy as np
import matplotlib.pyplot as plt

# Distance is calculated by separating each section of a JA3 pre-hash
# string (version, cipher suites, extensions, supported groups, EC formats),
# considering each as a separate word, and comparing the distances of
# two such words using levenshtein distance. The overall distance of two
# JA3 pre-hash strings is the sum of distances of each section.

def arrify_ja3(ja3_string):
    ja3_arr = ja3_string.split(",")
    
    if not len(ja3_arr)==5:
        print("Not a proper JA3 pre-hash string: "+ja3_string)
        exit(1)

    for i in range(0, len(ja3_arr)):
        ja3_arr[i] = ja3_arr[i].split("-")

    return ja3_arr

# Return the ciphers and extensions as (x,y) coordinates
# calculated from levenshtein distance to origo (0,0)
def distance_coordinates(ja3):
    ja3_arr = arrify_ja3(ja3)
    #print("ja3: {}".format(ja3))
    #print("ja3_arr[0]: {}".format(ja3_arr[0]))
    #print("ja3_arr[1]: {}".format(ja3_arr[1]))
    #print("ja3_arr[2]: {}".format(ja3_arr[2]))
    #print("ja3_arr[3]: {}".format(ja3_arr[3]))
    #print("ja3_arr[4]: {}".format(ja3_arr[4]))
    #x = lv.levenshtein_ja3_prehash(ja3_arr[1],"0")
    #y = lv.levenshtein_ja3_prehash(ja3_arr[2],"0")
    return [lv.levenshtein_ja3_prehash(ja3_arr[0],"0"),lv.levenshtein_ja3_prehash(ja3_arr[1],"0"),lv.levenshtein_ja3_prehash(ja3_arr[2],"0"),lv.levenshtein_ja3_prehash(ja3_arr[3],"0"),lv.levenshtein_ja3_prehash(ja3_arr[4],"0")]

def distance(ja3_1,ja3_2):
    ja3_arr1 = arrify_ja3(ja3_1)
    ja3_arr2 = arrify_ja3(ja3_2)

    dist = np.zeros((len(ja3_arr1)))

    for i in range(0, len(ja3_arr1)):
        dist[i] = lv.levenshtein_ja3_prehash(ja3_arr1[i],ja3_arr2[i])

    #print("ja3_1: {}".format(ja3_1))
    #print("ja3_2: {}".format(ja3_2))
    #print("distance: {}".format(str(dist)))
    return np.sum(dist)

def ja3s_to_coords(ja3s):
    coords = []
    for ja3 in ja3s:
        coords.append(distance_coordinates(ja3))
    return coords

def get_label(v):
    if v == 0:
        return "Version"
    elif v == 1:
        return "Cipher Suites"
    elif v == 2:
        return "Extensions"
    elif v == 3:
        return "Supported Groups"
    elif v == 4:
        return "Point Formats"
    else:
        print("False value: {}".format(v))
        exit()
    

def plot_scatter(prod1, prod2, ja3s_1, ja3s_2, x, y, filename):
    coordinates1 = ja3s_to_coords(ja3s_1)
    coordinates2 = ja3s_to_coords(ja3s_2)
    #v1 = coordinates1
    #v2 = coordinates2
    if not coordinates1 == []:
        c0,c1,c2,c3,c4 = zip(*coordinates1)
        v1 = [c0,c1,c2,c3,c4]
    else:
        v1 = [None,None,None,None,None]
    if not coordinates2 == []:
        d0,d1,d2,d3,d4 = zip(*coordinates2)
        v2 = [d0,d1,d2,d3,d4]
    else:
        v2 = [None,None,None,None,None]
    fig = plt.figure()
    plt.scatter(v1[x],v1[y],c="red",marker="o",label="{}".format(prod1))
    plt.scatter(v2[x],v2[y],c="blue",marker="x",label="{}".format(prod2))
    l1 = get_label(x)
    l2 = get_label(y)
    plt.xlabel(l1)
    plt.ylabel(l2)
    plt.legend(bbox_to_anchor =(0.65, 1.15))
    #plt.show()
    fig.savefig(filename)
    plt.close(fig)

def plot_scatter_three(prod1, prod2, prod3, ja3s_1, ja3s_2, ja3s_3, x, y, filename):
    coordinates1 = ja3s_to_coords(ja3s_1)
    coordinates2 = ja3s_to_coords(ja3s_2)
    coordinates3 = ja3s_to_coords(ja3s_3)
    if not coordinates1 == []:
        c0,c1,c2,c3,c4 = zip(*coordinates1)
        v1 = [c0,c1,c2,c3,c4]
    else:
        v1 = [None,None,None,None,None]
    if not coordinates2 == []:
        d0,d1,d2,d3,d4 = zip(*coordinates2)
        v2 = [d0,d1,d2,d3,d4]
    else:
        v2 = [None,None,None,None,None]
    if not coordinates3 == []:
        e0,e1,e2,e3,e4 = zip(*coordinates3)
        v3 = [e0,e1,e2,e3,e4]
    else:
        v3 = [None,None,None,None,None]
    fig = plt.figure(figsize=(6.4, 6.6))
    plt.scatter(v1[x],v1[y],c="red",marker="o",label="{}".format(prod1))
    plt.scatter(v2[x],v2[y],c="blue",marker="x",label="{}".format(prod2))
    plt.scatter(v3[x],v3[y],c="limegreen",marker="*",label="{}".format(prod3))
    l1 = get_label(x)
    l2 = get_label(y)
    plt.xlabel(l1)
    plt.ylabel(l2)
    #plt.legend(loc='upper right')
    plt.legend(bbox_to_anchor =(0.70, 1.16))
    #plt.show()
    fig.savefig(filename)
    plt.close(fig)
