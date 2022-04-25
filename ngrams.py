import argparse
from tokenize import String
from typing import List
from nltk import ngrams
from collections import Counter
from parse_chords import read_chord_dir, read_chord_file
import os


def build_gram_counter(dir, n):
    """
    takes in a directory to read from args.dir and 
    turns it into a list of tuples of length n (n-grams).
    then constructs a Counter object for these n-grams
    """
    chords = read_chord_dir(dir)
    chord_grams = ngrams(chords, n)
    n_counter = Counter()
    
    for gram in chord_grams:
        # will need to make this check more robust
        if gram[0] == '<e>':
            continue
        n_counter[gram] += 1
        
    return n_counter


def naive_bayes(gram_counter):
    pass


def main(args):
    gram_counter = build_gram_counter(args.dir, 3)
    print(gram_counter)


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
        help="filepath of a txt file containing list of sets of string that represents chords",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=dir_path,
        help="directory path for reading chord txt files",
    )
    args = parser.parse_args()

    main(args)