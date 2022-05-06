def longest_common_subsequence(X, Y):
    # find the length of the lists
    m = len(X)
    n = len(Y)

    L = [[None] * (n+1) for i in range(m+1)]

    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1]+1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    return L[m][n]

def main():
    list1 = ['C E- G', 'A- D F', 'B D F G', 'B- C E- G', 'C E- G', 'A- C F', 'B D F G', 'C E- G', 'C E- G', 'A- C F', 'B D G', 'A- C F']
    list2 = ['A- C F', 'C E- G', 'A- D F', 'B D F']

    print(list1)

    print("length of lcs is ", longest_common_subsequence(list1, list2))

main()