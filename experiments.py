import os

from baseline import *
from evaluate import generate_lcs_evaluations, generate_ssn_evaluation
from hmm import *
from ngrams import *
from parse_chords import read_chord_dir, read_chord_file
from prettytable import PrettyTable
from rnn import generate_output

# experiments to run
maxnote_experiments = ["max5", "max5_per_mm"]
seq_len_experiments = [4, 8, 12]
# generate 100 sequences for each type of experiment
num_seqs = 100
# ngrams-specific experiments
n_experiments = [2, 3, 5, 7, 9]
# hmm-specific experiments: emission method
hmm_methods = ["best", "prob"]
# rnn-specific experiments
rnn_seqlength = [20, 50, 100]
rnn_notelength = [25, 35, 50]



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
    if baseline:
        output_dir = os.path.join("outputs", "baseline")
        m = Baseline()
        for seq_len in seq_len_experiments:
            output_seq_dir = gen_dir(os.path.join(output_dir, f"seq{seq_len}"))
            for i in range(num_seqs):
                # generate a sequence
                seq = m.generate(seq_len)
                filepath = os.path.join(output_seq_dir, f"{i}.txt")
                write_seq_to_file(seq, filepath)

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
    if hmm:
        output_dir = os.path.join("outputs", "hmm")
        # maxnote
        for maxnote in maxnote_experiments:
            if not maxnote.endswith("_per_mm"):
                continue
            chord_dir = os.path.join("chords", maxnote)
            # get keys and chords from training corpus
            key_list, chord_list = read_chord_dir(chord_dir)
            output_maxnote_dir = gen_dir(os.path.join(output_dir, maxnote))
            # emission method
            for emission_method in hmm_methods:
                output_m_dir = gen_dir(os.path.join(output_maxnote_dir, emission_method))
                # order
                for n in n_experiments:
                    output_n_dir = gen_dir(os.path.join(output_m_dir, f"n{n}"))
                    # build the ngram model
                    m = HMM(n, key_list, chord_list)
                    # seq_len
                    for seq_len in seq_len_experiments:
                        output_seq_dir = gen_dir(os.path.join(output_n_dir, f"seq{seq_len}"))
                        for i in range(num_seqs):
                            # generate a sequence
                            _, seq = m.generate(seq_len, gen_chord_method=emission_method)
                            filepath = os.path.join(output_seq_dir, f"{i}.txt")
                            write_seq_to_file(seq, filepath)
    # =====
    #  RNN
    # =====
    if rnn:
        output_dir = os.path.join("outputs", "rnn")
        for maxnote in maxnote_experiments:
            chord_dir = os.path.join("chords", maxnote)
            rnn_dir = os.path.join("rnn_weights", maxnote)
            output_maxnote_dir = gen_dir(os.path.join(output_dir, maxnote))
            for seqlength in rnn_seqlength:
                filepath = os.path.join(rnn_dir, f"{seqlength}.hdf5")
                output_seq_dir = gen_dir(os.path.join(output_maxnote_dir, f"seqlength{seqlength}"))
                for notelength in rnn_notelength:
                    output_note_dir = gen_dir(os.path.join(output_seq_dir, f"notes{notelength}"))
                    for i in range(50):
                        output_file = os.path.join(output_note_dir, f"{i}.txt")
                        print(seqlength, notelength, filepath, output_maxnote_dir, output_file)
                        generate_output(seqlength, notelength, filepath, chord_dir, output_file)







def gen_evaluations(baseline: bool = True, ngrams: bool = True, hmm: bool = True, rnn: bool = True):
    
    # ==========
    #  baseline
    # ==========
    if baseline:
        eval_file =  os.path.join("evaluations", "baseline")
        output_dir = "baseline"

        # create table
        baseline_table = PrettyTable(["Experiment", "Avg LCS", "Avg SSN"])
        baseline_table.align["Experiment"] = "l" # Left align
        # max_note corpus to compare to
        for maxnote in maxnote_experiments:
            # seq_len
            for seq_len in seq_len_experiments:
                output_seqlen_dir = os.path.join(output_dir, f"seq{seq_len}")
                # todo: compare with which maxnote directory
                lcs = generate_lcs_evaluations(output_seqlen_dir, maxnote)
                ssn = generate_ssn_evaluation(output_seqlen_dir, maxnote)
                baseline_table.add_row([f"seq{seq_len} vs. {maxnote}", lcs, ssn])

        with open(eval_file, "w") as ef:
            ef.write(str(baseline_table))


    # ========
    #  ngrams
    # ========
    if ngrams:
        eval_file = os.path.join("evaluations", "ngrams")
        output_dir = "ngrams"

        # create table
        ngram_table = PrettyTable(["Experiment", "Avg LCS", "Avg SSN"])
        ngram_table.align["Experiment"] = "l" # Left align

        # maxnote
        for maxnote in maxnote_experiments:
            output_maxnote_dir = os.path.join(output_dir, maxnote)
            lcs = generate_lcs_evaluations(output_maxnote_dir, maxnote)
            ssn = generate_ssn_evaluation(output_maxnote_dir, maxnote)
            ngram_table.add_row([f"{maxnote}", lcs, ssn])
            # n
            for n in n_experiments:
                output_n_dir = os.path.join(output_maxnote_dir, f"n{n}")
                lcs = generate_lcs_evaluations(output_n_dir, maxnote)
                ssn = generate_ssn_evaluation(output_n_dir, maxnote)
                ngram_table.add_row([f"{maxnote}:n{n}", lcs, ssn])
                # seq_len
                for seq_len in seq_len_experiments:
                    output_seqlen_dir = os.path.join(output_n_dir, f"seq{seq_len}")
                    lcs = generate_lcs_evaluations(output_seqlen_dir, maxnote)
                    ssn = generate_ssn_evaluation(output_seqlen_dir, maxnote)
                    ngram_table.add_row([f"{maxnote}:n{n}:seq{seq_len}", lcs, ssn])

        with open(eval_file, "w") as ef:
            ef.write(str(ngram_table))

    # =====
    #  HMM
    # =====
    if hmm:
        eval_file = os.path.join("evaluations", "hmm")
        output_dir = "hmm"

        # create table
        hmm_table = PrettyTable(["Experiment", "Avg LCS", "Avg SSN"])
        hmm_table.align["Experiment"] = "l" # Left align

        # maxnote
        for maxnote in maxnote_experiments:
            if not maxnote.endswith("_per_mm"):
                continue
            output_maxnote_dir = os.path.join(output_dir, maxnote)
            lcs = generate_lcs_evaluations(output_maxnote_dir, maxnote)
            ssn = generate_ssn_evaluation(output_maxnote_dir, maxnote)
            hmm_table.add_row([f"{maxnote}", lcs, ssn])
            # emission method
            for emission_method in hmm_methods:
                output_m_dir = os.path.join(output_maxnote_dir, emission_method)
                lcs = generate_lcs_evaluations(output_m_dir, maxnote)
                ssn = generate_ssn_evaluation(output_m_dir, maxnote)
                hmm_table.add_row([f"{maxnote}:{emission_method}", lcs, ssn])
                # order
                for n in n_experiments:
                    output_n_dir = os.path.join(output_m_dir, f"n{n}")
                    lcs = generate_lcs_evaluations(output_n_dir, maxnote)
                    ssn = generate_ssn_evaluation(output_n_dir, maxnote)
                    hmm_table.add_row([f"{maxnote}:{emission_method}:n{n}", lcs, ssn])
                    # seq_len
                    for seq_len in seq_len_experiments:
                        output_seqlen_dir = os.path.join(output_n_dir, f"seq{seq_len}")
                        lcs = generate_lcs_evaluations(output_seqlen_dir, maxnote)
                        ssn = generate_ssn_evaluation(output_seqlen_dir, maxnote)
                        hmm_table.add_row([f"{maxnote}:{emission_method}:n{n}:seq{seq_len}", lcs, ssn])

        with open(eval_file, "w") as ef:
            ef.write(str(hmm_table))
    # =====
    #  RNN
    # =====

def main():
    gen_outputs(baseline=False, ngrams=False, hmm=False, rnn=True)


if __name__ == "__main__":
    main()
