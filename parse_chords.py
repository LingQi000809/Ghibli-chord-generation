import argparse
import matplotlib.pyplot as plt
import os

from collections import Counter
from music21 import *


class Tune:
    """ class for a musical piece """
    def __init__(self, mid_fname: str, chord_unit: float = 4.0) -> None:
        self.tune_name, ext = os.path.splitext(os.path.basename(mid_fname))
        # convert the midi file into music21 stream.Score object
        self.score = converter.parse(mid_fname, format='midi', quarterLengthDivisors=[12,16])
        
        # normalize the score to a universal key
        self.key = self.score[0][0].getElementsByClass(key.KeySignature)[0].tonic.name
        print(f"first key: {self.key}")
        self.normalize_score(self.score, self.key)

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

    def normalize_score(self, score: stream.Score, from_tonic: str, to_tonic: str = 'E-'):
        """ normalize key to 3flats (Cm or EbM)
            from_tonic: the first key tonic str of the piece
            to_tonic: the string symbol for the tonic (in Major)
        """
        if from_tonic == to_tonic:
            return
        i = interval.Interval(note.Note(from_tonic), note.Note(to_tonic))
        score.transpose(i, inPlace=True)

    def get_chords(self, min_threshold: float = 1.0, max_notes: int = None) -> list:
        """ get chords from counters. Each chord is represented as a list of note symbols.
            E.g. ['G', 'D', 'C', 'F#', 'E']
            returns a list of lists """
        extracted_chords = [['<s>']]
        for chord in self.chords:
            # filter chords with weight less than min_threshold
            chord_filtered = Counter({c: count for c, count in chord.items() if count >= min_threshold})
            # extract the note symbols as a list ordered by weight, with the max_notes limit
            chord_final = [c for c, count in chord_filtered.most_common(max_notes)]
            extracted_chords.append(chord_final)
        extracted_chords.append(['<e>'])
        return extracted_chords

    def write(self, min_threshold: float = 1.0, max_notes: int = None):
        """ write to file;
            suffix specifies the configuration of chords (min_threshold & max_notes)"""
        # build file path
        chords_dir = "chords"
        maxnotes_dir = f"max{max_notes}"
        thresh_suffix = f"thresh{min_threshold}"
        name = ("-").join([self.tune_name, thresh_suffix])

        f_dir = os.path.join(chords_dir, maxnotes_dir)
        if not os.path.exists(f_dir):
                os.mkdir(f_dir)
        # write to file
        chord_fpath = os.path.join(f_dir, name)
        chords = self.get_chords(min_threshold=min_threshold, max_notes=max_notes)
        with open(chord_fpath, "w") as f:
            for chord in chords:
                for note in chord:
                    f.write(f"{note} ")
                f.write("\n")

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

def read_chord_file(fp):
    """
    reads a txt file that represents a chord generated by parse_chords
    and returns a list of sets of strings
    """
    chords = []
    for chord in fp.readlines():
        temp_chord = chord.strip()
        set_chord = set(temp_chord.split(" "))
        chords.append(set_chord)
    return chords 

def read_chord_dir(dir):
    """Takes a directory of chord files and appends them into one list"""
    for root, dirs, files in os.walk(dir, topdown=False):
        result = []
        for filename in files:
            with open(os.path.join(root, filename)) as fp:
                chords = read_chord_file(fp)
                for chord in chords:
                    result.append(chord)
    return result

def write_midi_to_chords(fname: str, min_threshold: float = 1.0, max_notes: int = None):
    tune = Tune(fname)
    # tune.score.show()
    tune.update_chords()
    tune.write(min_threshold=min_threshold, max_notes=max_notes)
    print(f"written {fname} to chords with min_threshold: {min_threshold}; max_notes: {max_notes}")

def main(args):
    midi_filepath = args.mid
    midi_dir = args.dir
    if midi_filepath:
        write_midi_to_chords(midi_filepath, max_notes=5)
        write_midi_to_chords(midi_filepath)
    # if midi_dir:
    #     for f in os.listdir(midi_dir):
    #         midi_filepath = os.path.join(midi_dir, f)
    #         if os.path.isfile(midi_filepath):
    #             write_midi_to_chords(midi_filepath, max_notes=5)
    #             write_midi_to_chords(midi_filepath)
    chords = read_chord_dir("chords/max5")

    count = Counter()
    chords_str = []
    for chord in chords:
        c = ""
        for note in sorted(list(chord)):
            c += note
        chords_str.append(c)
        count[c] += 1
    print(count)
    plt.hist(chords_str)
    plt.show()
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mid",
        "-m",
        type=str,
        help="filepath of a midi file to parse into chords",
    )
    parser.add_argument(
        "--dir",
        "-d",
        type=str,
        help="filepath of a midi folder to parse each file in that folder into chords",
    )
    args = parser.parse_args()

    main(args)