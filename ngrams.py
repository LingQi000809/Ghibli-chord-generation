import argparse
from tokenize import String
from typing import List
from nltk import ngrams
from collections import Counter

def get_ngrams(chords,n):
    """
    takes as input a list of chords represented by Counter objects and
    a value n for the n-gram (2 for bigram, 3 for trigram, etc) and
    returns a list of all the given n-grams in the document
    """
    n_grams = ngrams(chords, n)
    return n_grams       


def main(args):
    ## get list of counters from file
    chords = [['d','b'],['g','d','c','f#','e'],['f','c','a'],['c','a','e-','f'],['c','d','a','f'],['c','c#','g#','f']]
    n = 2
    
    #print(chords)
    
    n_grams = ngrams(chords,n)
    print(type(n_grams))
    for grams in n_grams:
        print(grams)

    

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