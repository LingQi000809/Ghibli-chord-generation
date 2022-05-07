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


class NgramModel(object):

    def __init__(self, n: int):
        if n < 1:
            raise ValueError("N for an Ngram model must be greater than 0.")
        self.n = n
        # key: context (previous chords); value: a list of candidate next chord;
        # example: {("C E G", "A D F"): ["C E G", "B D G", ...]}
        self.context = {}
        # counter for all the ngrams in the tuple form: ((chord_1, chord_2, ..., chord_n-1), chord_n)
        self.ngram_counter = Counter()
        # mapping from a candid
    
    def get_ngrams(self, data_chords: list) -> list:
        """
        data_chords: all chords from the training data (in sequential order, with proper start symbols added);
        returns a list of ngrams in the tuple form: ((chord_1, chord_2, ..., chord_n-1), chord_n)
        """
        l = [(
            tuple([data_chords[i-p-1] for p in reversed(range(self.n-1))]), 
            data_chords[i]
            ) for i in range(self.n-1, len(data_chords))]
        return l

    def update(self, chord_list: list) -> None:
        """
        Updates Language Model
        chord_list: a list of chords (strings) from the data, in sequential order
        """
        n = self.n

        # add in start symbols to match n
        new_chord_list = []
        for c in chord_list:
            if c == '<s>':
                new_chord_list.extend(['<s>'] * (n-1))
            new_chord_list.append(c)

        # get ngrams
        ngrams = self.get_ngrams(new_chord_list)
        # update the ngram_counter with these ngrams
        self.ngram_counter += Counter(ngrams)

        # update the context
        for ngram in ngrams:
            prev_words, target_word = ngram
            if prev_words in self.context:
                self.context[prev_words].append(target_word)
            else:
                self.context[prev_words] = [target_word]

    def prob(self, context: tuple, next_chord: str):
        """
        Calculates probability of a candidate chord to be generated given a context;
        Returns conditional probability
        """
        try:
            count_of_chord = self.ngram_counter[(context, next_chord)]
            count_of_context = float(len(self.context[context]))
            result = count_of_chord / count_of_context
        except KeyError:
            result = 0.0
        return result
    
    def get_candidates(self, context: tuple) -> dict:
        """ get a mapping from candidate chord to its probability as the next chord given the context """
        candidate_probs = {}
        candidate_chords = self.context[context]
        for c in candidate_chords:
            candidate_probs[c] = self.prob(context, c)
        print(f"context: {context}\ncandidates: {candidate_probs}")
        return candidate_probs

    def gen_chord_semirandom(self, context: tuple):
        """
        Given a context we "semi-randomly" select the next chord to append in a sequence
        """
        # a random r between 0 and 1
        r = random.random()
        # get all candidate chords
        candidate_probs = self.get_candidates(context)

        # accumulate probability from candidate chords by order form highest prob to lowest
        # until greater than the random r
        # semi-random -> next chord
        summ = 0
        for candidate_chord in sorted(candidate_probs):
            summ +=candidate_probs[candidate_chord]
            if summ > r:
                return candidate_chord

    def gen_chord_by_prob(self, context: tuple):
        """
        Given a context we randomly select the next chord by probability
        """
        # get all candidate chords
        candidates = self.get_candidates(context)
        candidate_chords = list(candidates.keys())
        candidate_probs = list(candidates.values())
        # print(candidates, candidate_chords, candidate_probs)
        return random.choices(candidate_chords, weights=candidate_probs, k=1)[0]
    
    def generate(self, seq_len: int, method: str = "prob"):
        """
        seq_len: number of chords to be produced until encountering ending;
        method: prob - randomly generate by probability; 
                semi - semi-randomly generate with a random threshold for probability;
        Returns the generated chord sequence
        """
        n = self.n
        # context_queue: a window of context chords for the next chord to generate
        # start with context of all start symbols
        context_queue = ['<s>'] * (n-1)
        # result keeps track of the final sequence
        result = []
        for i in range(seq_len + n):
            # generate a new chord with the specified method
            if method == "prob":
                new_chord = self.gen_chord_by_prob(tuple(context_queue))
            elif method == "semi":
                new_chord = self.gen_chord_semirandom(tuple(context_queue))
            else:
                raise ValueError("Unrecognized method for generating chords with an Ngrams model. Currently supported methods are: 'prob', 'semi'.")
            
            # append new chord to sequence
            result.append(new_chord)

            # once we reach an ending, the model should not proceed (no chord after ending)
            if new_chord == "<e>":
                break

            # update the context queue like a sliding window
            # remove the first chord - not in the scope of context (prev grams) for the next iteration
            # append newly generated chord - now the most recent context for the next iteration
            context_queue.pop(0)
            context_queue.append(new_chord)
        return result

def main(args):
    _, chord_list = read_chord_dir(args.dir)

    m = NgramModel(3)
    m.update(chord_list)
    # for x in m.ngram_counter:
    #     if x[0][0] == '<s>':
    #         print(x)
    # print(m.ngram_counter)
    seq = m.generate(15, method="semi")
    compose(seq)


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