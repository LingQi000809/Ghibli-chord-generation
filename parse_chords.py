import argparse
import os

from collections import Counter
from music21 import *

class Tune:
    """ class for a musical piece """
    def __init__(self, mid_fname: str, chord_unit: float = 4.0) -> None:
        # convert the midi file into music21 stream.Score object
        self.score = converter.parse(mid_fname, format='midi', quarterLengthDivisors=[12,16])
        transposed_score = stream.Score(id='tScore')
        for part in self.score:
            flat_transposed_part = part.flatten()
            self.normalize_score(flat_transposed_part)
            

        # time signature
        # NOTE: we only deal with 1 time signature per tune for now
        self.mm_beats = self.score.getTimeSignatures()[0].barDuration.quarterLength
        # unit in terms of quarter note to evaluate as a chord
        # (e.g. default to 4.0 -> evaluate chords per measure in 4/4 times)
        # NOTE: currently not used. treating each measure as 1 chord
        # TODO: generalize to any time signature
        self.chord_unit = chord_unit
        # first beat in each chord_unit
        self.downbeats = []
        for i in range(int(self.mm_beats)):
            if i % self.chord_unit == 0:
                self.downbeats.append(i + 1)

        # list of Counters of (note_str: duration_num), to be updated
        # e.g. (E: 8, G: 2.5, B: 1, F: 0.5)
        self.chords = []

    def normalize_score(self, score: stream.Score, to_tonic: str = 'E-'):
        """ normalize key to 3flats (Cm or EbM)
            to_tonic: the string symbol for the tonic (in Major)
        """
        # keys = score.getElementsByClass(key.KeySignature)
        # print(len(keys))
        # for k in keys:
        #     print(k)
        # starting_tonic = keys[0].tonic.name
        # i = interval.Interval(note.Note(starting_tonic), note.Note(to_tonic))
        # score.transpose(i, inPlace=True)

    def get_chords():
        # threshold & max num of notes
        ...

    def write():
        # write to file


    def get_note_dur(self, note, isBass: bool = False) -> float:
        """ get a note(chord)'s duration, considering added weights on downbeat and bassline notes"""
        dur = min(note.quarterLength, self.chord_unit)
        if note.beat in self.downbeats:
            dur += min(1, dur)
        if isBass:
            dur += min(1, dur)
        return dur

    def count_notes(self, mm: stream.Measure, isBass: bool = False) -> Counter:
        """ count the duration for notes in a Measure (usually a chord unit in melody / bassline) """
        note_counts = Counter()
        mm_notes = mm.flat.notes

        # record each note's duration / strength
        for note in mm_notes:
            # note can be either a note or a chord...
            if note.isChord:
                # now the beat information is with the chord, but not the notes
                dur = self.get_note_dur(note, isBass=isBass)
                for n in note.notes:
                    note_counts.update({n.name: dur})
                    # print(n.name, dur)
            else:
                dur = self.get_note_dur(note, isBass=isBass)
                note_counts.update({note.name: dur})
                # print(note.name, dur)
        return note_counts

    def update_chords(self):
        """ parse chord information by counting notes per chord unit """
        # elements in chords are note counters for each chord unit 
        chords = []
        # score -> parts (melody line & bass line)
        parts = self.score.getElementsByClass(stream.Part)
        melody_part = parts[0]
        bass_part = parts[1]
        # parts -> measures (melody line & bass line)
        melody_mms = melody_part.getElementsByClass(stream.Measure)
        bass_mms = bass_part.getElementsByClass(stream.Measure)

        for i, mm in enumerate(melody_mms):
            # print('measure ', i)
            # print('melody: ')
            # count notes in each measure of the melody line
            melody_counter = self.count_notes(mm)
            # count notes in each measure of the bass line
            # print('bass: ')
            bass_counter = self.count_notes(bass_mms[i], isBass=True)
            chord = melody_counter + bass_counter
            chords.append(chord)

        self.chords = chords

    def simp_chords(self):
        """ simplify chords: filter out non-chord tones in melody """
        ...

def main(args):
    midi_fname = args.mid
    tune = Tune(midi_fname)
    # tune.score.show()
    tune.update_chords()
    print(tune.chords)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mid",
        "-m",
        type=str,
        help="name of a midi file to parse into chords",
    )
    args = parser.parse_args()

    main(args)