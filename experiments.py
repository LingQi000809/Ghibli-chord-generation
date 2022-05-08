import os

from baseline import *
from evaluate import generate_lcs_evaluations, generate_snn_evaluation
from hmm import *
from ngrams import *
from parse_chords import read_chord_dir, read_chord_file
from prettytable import PrettyTable

# experiments to run
maxnote_experiments = ["max3", "max3_per_mm", "max5", "max5_per_mm"]
seq_len_experiments = [4, 8, 12]
# generate 100 sequences for each type of experiment
num_seqs = 100
# ngrams-specific experiments
n_experiments = [2, 3, 5, 7, 9]

def gen_dir(dir_name: str) -> str:
    """
    make the directory if it doesn't exist. returns the dir_name
    """
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    return dir_name

def write_seq_to_file(seq: list, file_path: str):
    with open(file_path, "w") as f:
        for chord in seq:
            f.write(f"{chord}\n")

def gen_outputs(baseline: bool = True, ngrams: bool = True, hmm: bool = True, rnn: bool = True):
    """
    generate sequences and write to outputs directory for all the experiments
    """
    # ==========
    #  baseline
    # ==========

    # ========
    #  ngrams
    # ========
    if ngrams:
        output_dir = os.path.join("outputs", "ngrams")
        # maxnote
        for maxnote in maxnote_experiments:
            chord_dir = os.path.join("chords", maxnote)
            # get chords from training corpus
            _, chord_list = read_chord_dir(chord_dir)
            output_maxnote_dir = gen_dir(os.path.join(output_dir, maxnote))
            # n
            for n in n_experiments:
                output_n_dir = gen_dir(os.path.join(output_maxnote_dir, f"n{n}"))
                # build the ngram model
                m = NgramModel(n)
                m.update(chord_list)
                # seq_len
                for seq_len in seq_len_experiments:
                    output_seq_dir = gen_dir(os.path.join(output_n_dir, f"seq{seq_len}"))
                    for i in range(num_seqs):
                        # generate a sequence
                        seq = m.generate(seq_len)
                        filepath = os.path.join(output_seq_dir, f"{i}.txt")
                        write_seq_to_file(seq, filepath)
        
    # =====
    #  HMM
    # =====

    # =====
    #  RNN
    # =====

def gen_evaluations(baseline: bool = True, ngrams: bool = True, hmm: bool = True, rnn: bool = True):
    
    if ngrams:
        eval_file = os.path.join("evaluations", "ngrams")
        output_dir = "ngrams"

        # create table
        ngram_table = PrettyTable(["Experiment", "Avg LCS", "Avg SNN"])
        ngram_table.align["Experiment"] = "l" # Left align city names

        # maxnote
        for maxnote in maxnote_experiments:
            output_maxnote_dir = os.path.join(output_dir, maxnote)
            lcs = generate_lcs_evaluations(output_maxnote_dir, maxnote)
            snn = generate_snn_evaluation(output_maxnote_dir, maxnote)
            ngram_table.add_row([f"{maxnote}", lcs, snn])
            # n
            for n in n_experiments:
                output_n_dir = os.path.join(output_maxnote_dir, f"n{n}")
                lcs = generate_lcs_evaluations(output_n_dir, maxnote)
                snn = generate_snn_evaluation(output_n_dir, maxnote)
                ngram_table.add_row([f"{maxnote}:n{n}", lcs, snn])
                # seq_len
                for seq_len in seq_len_experiments:
                    output_seqlen_dir = os.path.join(output_n_dir, f"seq{seq_len}")
                    lcs = generate_lcs_evaluations(output_seqlen_dir, maxnote)
                    snn = generate_snn_evaluation(output_seqlen_dir, maxnote)
                    ngram_table.add_row([f"{maxnote}:n{n}:seq{seq_len}", lcs, snn])

        with open(eval_file, "w") as ef:
            ef.write(str(ngram_table))
            



def main():
    gen_outputs(ngrams=False)
    gen_evaluations()



if __name__ == "__main__":
    main()
