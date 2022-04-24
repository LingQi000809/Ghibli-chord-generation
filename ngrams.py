import argparse
from tokenize import String
from typing import List
from nltk import ngrams
from collections import Counter

def get_ngrams(chords, n):
    """
    takes as input a list of chords represented by Counter objects and
    a value n for the n-gram (2 for bigram, 3 for trigram, etc) and
    returns a list of all the given n-grams in the document
    """
    n_grams = ngrams(chords, n)
    return n_grams       

def get_examples(folder):
    """
    get_examples will loop through a folder with .txt files (list of list of characters
    representing sequence of chords) for each piece and build a full n-gram Counter set 
    with the following n values:
    2,3,4, and 5 to start  ...


    """
    pass

def main(args):
    ## get list of counters from file
    #chords = [['d','b'],['g','d','c','f#','e'],['f','c','a'],['c','a','e-','f'],['c','d','a','f'],['c','c#','g#','f']]
    #n = 2
    

    #print(args.chords.readlines())

    chords = []
    for chord in args.chords.readlines():
        temp_chord = chord.strip()
        list_chord = temp_chord.split(" ")
        chords.append(list_chord)
    print(chords)
    

    #with open(args.chords, "r") as fp:
    #    lines = fp.readlines()
    #    print(lines)
    
    #n_grams = ngrams(chords,n)
    #print(type(n_grams))
    #for grams in n_grams:
    #    print(grams)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--chords",
        "-c",
        type=argparse.FileType("r"),
        help="list of Counter objects that represents chords",
    )
    args = parser.parse_args()

    main(args)