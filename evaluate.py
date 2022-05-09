import glob
import os

from music21 import *
from parse_chords import read_chord_dir, read_chord_file


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


def generate_lcs_evaluations(gen_directory, piece_dir):
    """
    takes a directory within outputs and finds the longest common subsequence
    for each generated sequence and all the pieces in the corpus. it stores
    the maximum of those LCS values and then moves onto the next generated sequence

    it returns the average max lcs for each generated sequence when compared to the whole corpus.
    """
   
    # directories for the generated sequences and the chord
    gen_path = os.path.join("outputs", gen_directory)
    chord_path = os.path.join("chords", piece_dir)

    lcs_list = []

    _, all_chords = read_chord_dir(chord_path)
    for filepath in glob.glob(f"{gen_path}/**/*.txt", recursive=True):
        with open(filepath, 'r') as f:
            _, gen_seq = read_chord_file(f)
            # longest common subsequence between the current generated sequence and our corpus
            cur_lcs = lcs(gen_seq, all_chords)
            lcs_list.append(cur_lcs)
    print(lcs_list)
    print(f"calculating average lcs from {len(lcs_list)} generated sequences")
    #return the average lcs for each generated sequence
    return sum(lcs_list) / len(lcs_list)


def is_sublist(a, b):
    """
    helper function to see if list a is a sublist of b
    it has to appear in order in b
    """
    for i in range(len(b) - len(a)+1):
        if b[i:i+len(a)] == a:
            return True
    return False

def same_sequence_number(sequence, comp_dir):
    """
    takes in a sequence of chords and returns the number of pieces in the ghibli corpus
    that have the same sequence of roots as the given chord sequence
    """
    root_list = []
    piece_count = 0
    dir = os.path.join("roots", comp_dir)

    # construct chords using .split 
    for chord_in_seq in sequence:
        if chord_in_seq.startswith("<") or not chord_in_seq:
            continue
        temp_chord = chord.Chord(chord_in_seq.split(" "))
        root_list.append(temp_chord.root())

    # converts the list of music21 pitches to a list of strings
    for count, root in enumerate(root_list):
       root_list[count] = root.name
    print(root_list)

    # compares the list of root strings to see if it's a sublist for any piece in the 
    # roots directory
    for filename in os.listdir(dir):
        with open(os.path.join(dir, filename), 'r') as f:
            comp_roots = f.readline().split(" ")
            if is_sublist(root_list, comp_roots):
                piece_count += 1
                # can use this print to check which pieces it appears in
                #print(filename)

    return piece_count 

def generate_ssn_evaluation(gen_dir, comp_dir):
    """
    takes a directory of generated sequences and a comparison folder in the roots
    directory. stores the number of pieces with overlapping root sequences in a list
    and then returns the average number of pieces for the whole list of generated sequences
    """
    
    gen_path = os.path.join("outputs", gen_dir)
    piece_count_list = []

    for filepath in glob.glob(f"{gen_path}/**/*.txt", recursive=True):
        with open(filepath, 'r') as f:
            _, sequence = read_chord_file(f)
            piece_count_list.append(same_sequence_number(sequence, comp_dir))

    print(f"calculating average ssn from {len(piece_count_list)} generated sequences")

    return sum(piece_count_list) / len(piece_count_list)


def creating_root_files(directory):
    """
    reads given directory in the chord directory and writes roots for the chords 
    into a matching file in the roots directory
    """
    r_dir = os.path.join("chords", directory)
    w_dir = os.path.join("roots", directory)

    if not os.path.exists(r_dir):
        return -1
    if not os.path.exists(w_dir):
        os.mkdir(w_dir)

    for filename in os.listdir(r_dir):
        root_list = []
        
        with open(os.path.join(r_dir, filename), 'r') as f:
            _, sequence = read_chord_file(f)
            
            # skip first and last element because those are start and end symbols 
            for chord_in_seq in sequence[1:-1]:
                temp_list = chord_in_seq.strip().split(" ")
                if '' in temp_list:
                    continue
                else:
                    temp_chord = chord.Chord(temp_list)
                    root_list.append(temp_chord.root())
        with open(os.path.join(w_dir, filename), 'w') as f:
            for root in root_list:
                f.write(f"{root} ")         

def main():
    #list1 = ['C E- G', 'A- D F', 'B D F G', 'B- C E- G', 'C E- G', 'A- C F', 'B D F G', 'C E- G', 'C E- G', 'A- C F', 'B D G', 'A- C F']
    #list2 = ['A- C F', 'C E- G', 'A- D F', 'B D F']
    #list3 = ['G D B- C E-', 'E-', 'G C E-', 'E-']

    """with open(os.path.join("roots", "max5", "A_Lost_Child-thresh1.0"), 'r') as f:
        print(f.readline().split(" "))"""

    #creating_root_files("max3")
    
    #print("checking chords: ", same_sequence_number(list3, "max5"))
    #print("length of lcs is ", lcs(list1, list2))

main()