import random

from music21 import *

def compose(seq: list, show_score: bool = True):
    """ transcribe the chord sequence from strings into music21 Stream.
    seq: list[str], a list of strings representing chords.
    show_score: bool, if set to True, show the score (need MuseScore installed) """
    composition = stream.Stream()
    for chord_str in seq:
        if chord_str.startswith('<'):
            continue
        # TODO: varying duration?
        c = chord.Chord(chord_str.split(), duration=duration.Duration(2.0))
        print(chord_str)
        if len(chord_str.split()) >= 3:
            inversion = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
            c.inversion(inversion)
        composition.append(c)
    composition.show()