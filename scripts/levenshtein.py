import numpy as np

def levenshtein_ja3_prehash(s, t, ratio_calc = False):
    """ Modified from https://www.datacamp.com/community/tutorials/fuzzy-string-python
        Calculates levenshtein distance between two ja3_prehash strings.
        If ratio_calc = True, the function computes the levenshtein distance ratio
        of similarity between two ja3_prehash strings.
    """
    # Initialize
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype=int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the distance matrix to compute the cost

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col]+1,
                                     distance[row][col-1]+1,
                                     distance[row-1][col-1]+cost)
    if ratio_calc == True:
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        return distance[row][col]
