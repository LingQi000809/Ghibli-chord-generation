import argparse
from tokenize import String
from typing import List
from nltk import ngrams
from collections import Counter
from parse_chords import read_chord_file
import os


def get_examples(dir, n):
    """
    FIX THIS 
    get_examples will loop through a folder with .txt files (list of list of characters
    representing sequence of chords) for each piece and build a full n-gram Counter set 
    with the following n values:
    2,3,4, and 5 to start  ...
    """
    # read files from directory using jack's function
    # pass that into ngrams here
    n_counter = Counter(ngrams())

    #return the counter
    return n_counter


def main(args):
    chords = read_chord_file(args.chords)
    print(chords)

    n = 2

    n_grams = ngrams(chords,n)
    for grams in n_grams:
        print(grams)


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--chords",
        "-c",
        type=argparse.FileType("r"),
        help="txt file containing list of sets of string that represents chords",
    )
    parser.add_argument(
        "--path",
        "-p",
        type=dir_path,
        help="directory path for reading files",
    )
    args = parser.parse_args()

    main(args)