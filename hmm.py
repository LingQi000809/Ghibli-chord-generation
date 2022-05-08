import argparse
import numpy as np
import os
import random 

from collections import Counter
from compose import compose
from ngrams import NgramModel
from nltk import ngrams
from nltk import NaiveBayesClassifier
from parse_chords import read_chord_dir, read_chord_file
from tokenize import String
from typing import List


class HMM(object):
    def __init__(self, order: int, keys: list, chords: list, verbose: bool = False):
        """
        order: number of previous hidden states to look at in order to generate the next hidden state;
        keys: a list of keys (hidden states);
        chords: a list of chord strings (observed states)
        """
        self.verbose = verbose
        self.order = order
        self.keys = keys
        self.chords = chords
        # make sure that each key is corresponded to each chord in the training data
        assert(len(self.keys) == len(self.chords))

        # build an ngram for keys
        self.key_ngram = NgramModel(self.order, verbose=self.verbose)
        self.key_ngram.update(keys)

        # a list of all unique keys        
        # (index of each key in this list corresponds to the row in the emission matrix)
        self.unique_keys = list(set(keys))
        # mapping from a key string to its index in unique_keys
        self.key_to_idx = self.build_idx_mapping(self.unique_keys)

        # a list of all unique chords 
        # (index of each chord in this list corresponds to the column in the emission matrix)
        self.unique_chords = list(set(chords))
        # mapping from a chord string to its index in unique_chords
        self.chord_to_idx = self.build_idx_mapping(self.unique_chords)

        # the emission matrix (key -> chord string)
        # [
        #   [prob_0, prob_1, ...] # (for key0)
        #   [prob_0, prob_1, ...] # (for key1)
        #   ...
        # ]
        # each key's value is a list of probability for each possible chord string (fixed index from unique_chords)
        self.key_chord_probs = self.build_key_chord_probs()

    def build_idx_mapping(self, from_unique_list: list) -> dict:
        """ 
        from_unique_list: a list of features (unique keys / chords), without duplicates.
        Returns a dict in the form of {feature_str: index};
        (maps a key string or a chord string to its corresponding index in the emission matrix)
        """
        mapping = {}
        for i, feature in enumerate(from_unique_list):
            assert(feature not in mapping)
            mapping[feature] = i
        return mapping
    
    def build_key_chord_probs(self) -> np.array:
        """
        build the emission matrix, with keys as the hidden states and chord strings as the observed states
        """
        # [
        #   [count_0, count_1, ...] # (for key0)
        #   [count_0, count_1, ...] # (for key1)
        #   ...
        # ]
        key_chord_counts = np.zeros((len(self.unique_keys), len(self.unique_chords)))
        for i in range(len(self.keys)):
            key = self.keys[i]
            key_idx = self.key_to_idx[key]
            chord = self.chords[i]
            chord_idx = self.chord_to_idx[chord]

            # increment the count of this chord in this key
            key_chord_counts[key_idx][chord_idx] += 1
        
        # turn counts into probabilities
        return (key_chord_counts.transpose() / key_chord_counts.sum(axis=1)).transpose()

    def generate(self, seq_len: int, gen_key_method: str = "prob", gen_chord_method: str = "prob") -> list:
        """
        seq_len: number of chords to be produced until encountering ending;
        gen_key_method: (for key's ngram model)
            prob - randomly generate by probability; 
            semi - semi-randomly generate with a random threshold for probability;
        gen_chord_method: (for generating chords from emission matrix)
            prob - randomly generate by probability; 
            best - generate chord of the highest probability;
        Returns the generated chord sequence
        """
        gen_keys = self.key_ngram.generate(seq_len, method=gen_key_method)
        gen_chords = []
        for key in gen_keys:
            key_idx = self.key_to_idx[key]
            chord_probs = self.key_chord_probs[key_idx]
            if gen_chord_method == "prob":
                gen_chord = random.choices(self.unique_chords, weights=chord_probs, k=1)[0]
            elif gen_chord_method == "best":
                gen_chord = self.unique_chords[chord_probs.argmax(axis=0)]
            else:
                raise ValueError("Unrecognized method for generating chords from emission matrix in HMM. Currently supported methods are: 'prob', 'best'.")
            gen_chords.append(gen_chord)
        return gen_keys, gen_chords

def main(args):
    keys, chords = read_chord_dir(args.dir)
    hmm = HMM(5, keys, chords, verbose=True)
    key_seq, chord_seq = hmm.generate(10, gen_key_method="prob", gen_chord_method="prob")
    print(key_seq)
    print(chord_seq)
    compose(chord_seq)

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