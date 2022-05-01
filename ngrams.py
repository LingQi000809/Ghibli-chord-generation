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

    def __init__(self, n):
        self.n = n

        # dictionary that keeps list of candidate words given context
        self.context = {}

        # keeps track of how many times ngram has appeared in the text before
        self.ngram_counter = {}

    def update(self, dir) -> None:
        """
        Updates Language Model
        :param sentence: input text
        """
        n = self.n
        ngrams = get_ngrams(n, read_chord_dir(dir))
        for ngram in ngrams:
            if ngram in self.ngram_counter:
                self.ngram_counter[ngram] += 1.0
            else:
                self.ngram_counter[ngram] = 1.0

            prev_words, target_word = ngram
            if prev_words in self.context:
                self.context[prev_words].append(target_word)
            else:
                self.context[prev_words] = [target_word]

    def prob(self, context, token):
        """
        Calculates probability of a candidate token to be generated given a context
        :return: conditional probability
        """
        try:
            count_of_token = self.ngram_counter[(context, token)]
            count_of_context = float(len(self.context[context]))
            result = count_of_token / count_of_context

        except KeyError:
            result = 0.0
        return result
    
    def random_token(self, context):
        """
        Given a context we "semi-randomly" select the next word to append in a sequence
        :param context:
        :return:
        """
        r = random.random()
        map_to_probs = {}
        token_of_interest = self.context[context]
        for token in token_of_interest:
            map_to_probs[token] = self.prob(context, token)

        summ = 0
        for token in sorted(map_to_probs):
            summ += map_to_probs[token]
            if summ > r:
                return token
    
    def generate_text(self, token_count: int):
        """
        :param token_count: number of words to be produced
        :return: generated text
        """
        n = self.n
        context_queue = ['<s>', 'C E- G']
        beginning = context_queue.copy()
        result = []
        for _ in range(token_count):
            obj = self.random_token(tuple(context_queue))
            result.append(obj)
            if n > 1:
                context_queue.pop(0)
                if obj == '.':
                    context_queue = (n - 1) * ['<s>']
                else:
                    context_queue.append(obj)
        print(beginning + result)
        return beginning + result

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

def get_ngrams(n: int, tokens: list) -> list:
    """
    :param n: n-gram size
    :param tokens: tokenized sentence
    :return: list of ngrams
    ngrams of tuple form: ((previous wordS!), target word)
    """
    l = [(tuple([tokens[i-p-1] for p in reversed(range(n-1))]), tokens[i]) for i in range(n-1, len(tokens))]
    return l


def predict(gram, counts : Counter):
    n = len(gram)
    numer = counts.get(gram)
    i_minus_1_gram = gram[1:]
    denom = counts.get(i_minus_1_gram)
    return numer/denom 

    

def main(args):
    m = NgramModel(3)
    m.update(args.dir)
    
    text = m.generate_text(10)
    compose(text)


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