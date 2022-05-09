import argparse
import os
import random

from collections import Counter

from compose import compose


class Baseline:
    """ class for a baseline model that models chord progression with fixed templates """
    def __init__(self):
         # templates for chord progression
        self.templates = [
            [1, 5, 6, 4],
            [1, 4, 5, 4],
            [2, 5, 1],
            [1, 6, 4, 5],
            [1, 5, 6, 3, 4, 1, 4, 5],
            [4, 5, 3, 6, 2, 5, 1],
            [1, 2, 5, 1],
            [1, 4, 5, 1],
            [1, 6, 5, 1]
        ]

        # scale degree mapped to chord in E-major / C-minor key
        self.sd_chord_mapping = {
            "major": {
                1: ["B- E- G"],
                2: ["A- C F"],
                3: ["B- D G"],
                4: ["A- C E-"],
                5: ["B- D F"],
                6: ["C E- G"],
                7: ["A- D F"]
            },
            "minor": {
                1: ["C E- G"],
                2: ["A- D F"],
                3: ["B- E- G"],
                4: ["A- C F"],
                5: ["B D G"],
                6: ["A- C E-"],
                7: ["B- D F", "B D F"]
            }
        }

    def generate(self, seq_len: int):
        """ generate a chord sequence with minimum length of seq_len """
        # randomly choose a mode
        mode = random.choice(["major", "minor"])
        # sd_to_chord is a dict with {int: list[str]} ({sd: possible chords})
        sd_to_chord = self.sd_chord_mapping[mode]
        # keep track of the length of sequence generated
        cur_len = 0
        seq = []
        while cur_len < seq_len:
            template = random.choice(self.templates)
            # for each scale degree in the template, 
            # randomly choose from the possible chords belonging to that scale degree
            cur_seq = [random.choice(sd_to_chord[sd]) for sd in template]
            seq += cur_seq
            # update length
            cur_len += len(cur_seq)
        return seq[:seq_len]

def main():
    m = Baseline()
    seq = m.generate(10)
    print(seq)
    compose(seq)
    

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # args = parser.parse_args()

    main()