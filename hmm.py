import argparse
from tokenize import String
from typing import List
from nltk import ngrams
from nltk import NaiveBayesClassifier
from collections import Counter
from parse_chords import read_chord_dir, read_chord_file
import os
import random 
from compose import compose


class HMM(object):
    def __init__(self):
        ...

def main(args):
    keys, chords = read_chord_dir(args.dir)


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