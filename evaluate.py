from music21 import *

def lcs(X, Y):
    """
    source: https://www.geeksforgeeks.org/python-program-for-longest-common-subsequence/

    returns the length of the longest common subsequence for two lists of chords: X and Y
    """
    
    # find the length of the lists
    m = len(X)
    n = len(Y)

    # declaring the array for storing values
    L = [[None] * (n+1) for i in range(m+1)]

    #builds L[m+1][n+1]
    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1]+1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    return L[m][n]

def same_sequence_number(sequence):
    """
    takes in a sequence of chords and returns the number of pieces in the ghibli corpus
    that have the same chord sequence 
    """
    root_list = []

    # construct chords using .split 
    for chord_in_seq in sequence:
        temp_chord = chord.Chord(chord_in_seq.split(" "))
        root_list.append(temp_chord.root())
    # check the whole corpus --> how to do this efficiently?

    return root_list

def main():
    list1 = ['C E- G', 'A- D F', 'B D F G', 'B- C E- G', 'C E- G', 'A- C F', 'B D F G', 'C E- G', 'C E- G', 'A- C F', 'B D G', 'A- C F']
    list2 = ['A- C F', 'C E- G', 'A- D F', 'B D F']

    print("checking chords: ", same_sequence_number(list1))
    #print("length of lcs is ", lcs(list1, list2))

main()