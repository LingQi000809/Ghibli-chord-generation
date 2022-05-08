import random

from music21 import *

def compose(seq: list, show_score: bool = True):
    """ transcribe the chord sequence from strings into music21 Stream.
    seq: list[str], a list of strings representing chords.
    show_score: bool, if set to True, show the score (need MuseScore installed) """
    composition = stream.Stream()
    chord_streams = []
    for i, chord_str in enumerate(seq):
        if chord_str.startswith('<'):
            continue
        if i > 0 and chord_str == seq[i-1]:
            prev_chord_dur = chord_streams[-1].duration.quarterLength
            if prev_chord_dur < 4:
                chord_streams[-1].duration = duration.Duration(prev_chord_dur + 2.0)
            continue

        c = chord.Chord(chord_str.split(), duration=duration.Duration(2.0))
        if len(chord_str.split()) >= 3:
            if c.containsTriad():
                inversion = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
            else:
                inversion = 0
            c.inversion(inversion)
        chord_streams.append(c)
    for c in chord_streams:
        composition.append(c)
    if show_score:
        composition.show()