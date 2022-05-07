import argparse
import matplotlib.pyplot as plt
import os

from collections import Counter
from music21 import *


class Tune:
    """ class for a musical piece """
    def __init__(self, mid_fname: str, chord_per_measure: bool = False) -> None:
        # the chord_per_measure flag disgards the possible harmonic rhythm of 2+ chords per measure
        self.chord_per_measure = chord_per_measure

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

    def get_mm_keys(self, nc_threshold: float = 0.6):
        """ predict the key of each measure using the analyze function from music21;
        nc_threshold: threshold below which a measure will be labeled as 'NC';
        """
        num_mm = 0
        for part in self.score.parts:
            num_mm = max(len(part.getElementsByClass('Measure')), num_mm)
        # print(num_mm)
        keys = []
        # measure num starts from 1
        for i in range(num_mm+1)[1:]:
            mm = self.score.measure(i)
            if len(mm.flatten().notes) == 0:
                keys.append("NC")
                continue
            # analyze key for each measure
            k = mm.analyze('key')
            # print(i, k)
            # if the most likely key is below nc_threshold, label the measure as "NC" (no-chord)
            if k.correlationCoefficient < nc_threshold:
                keys.append("NC")
            else:            
                # # get a list of alternativ keys above the alt_key_threshold
                # alt_ks = list(filter(lambda ak: ak.correlationCoefficient > alt_key_threshold, k.alternateInterpretations))
                # alt_knames = [ak.tonic.name for ak in alt_ks]
                # # there can be multiple tags for one measure
                # keys.append([k.tonic.name] + alt_knames)
                keys.append(k.tonic.name)
        return keys

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

    def get_note_dur(self, note, downbeats: list, ts: meter.TimeSignature, isBass: bool = False) -> list:
        """ get a note(chord)'s duration, considering added weights on downbeat and bassline notes.
            chord_unit: float, the max duration for a note (length of a chord_unit: a measure / a half measure).
            returns list[float]: if a note spans into the second half measure, the second element in the list is its dur to add to the second half """
        # variables with a unit of quarterLength all start with 0
        # chord_unit: the unit of a chord in quarterlength
        chord_unit = ts.beatCount * ts.beatDuration.quarterLength
        if not self.chord_per_measure and ts.numerator > 2 and ts.beatCount % 2 == 0:
            chord_unit /= 2
        # end tick of the first chord_unit in the measure
        end_unit1_tick = chord_unit 
        # end tick of the second chord_unit in the measure, if it exists
        end_unit2_tick = chord_unit * 2 
        # the starting tick (position) of note in quarterlength
        start_tick = (note.beat - 1) * ts.beatDuration.quarterLength
        
        isDownbeat = note.beat in downbeats

        # if the chord unit is the entire measure: the note duration can't exceed the remaining duration in the measure from its starting beat
        if len(downbeats) == 1:
            durations = [min(note.quarterLength, end_unit1_tick - start_tick)]
        # if the note is in the second half measure: the note duration can't exceed the remaining duration in the measure from its starting beat
        elif note.beat >= downbeats[1]:
            durations = [min(note.quarterLength, end_unit2_tick - start_tick)]
        # if the note is in the first half measure: the note duration can't exceed the chord unit; record carry-over
        else:
            dur1 = min(note.quarterLength, end_unit1_tick - start_tick)
            # dur2: carry-over to the next half measure
            dur2 = start_tick + note.quarterLength - end_unit1_tick
            if dur2 <= 0:
                durations = [dur1]
            else: 
                durations = [dur1, dur2]
                # print(note, end_unit1_tick, end_unit2_tick, start_tick, note.quarterLength, dur2)
         
        for i, dur in enumerate(durations):
            if isDownbeat or i == 1:
                durations[i] += min(1, dur)
            if isBass:
                durations[i] += min(1, dur)
        return durations

    def count_notes(self, mm: stream.Measure, ts: meter.TimeSignature, isBass: bool = False) -> list:
        """ count the duration for notes in a Measure (usually a chord unit in melody / bassline). 
            returns a list of Counters - each counter is a chord.
            If the beatCount is even in this measure, divide it in half and find chord for each half """
        # beatCount: how many beats are there in a measure (2 for 6/8; 4 for 4/4; 3 for 3/4)
        downbeats = [1.0]
        counters = [Counter()]
        if not self.chord_per_measure and ts.numerator > 2 and ts.beatCount % 2 == 0:
            downbeats.append(ts.beatCount / 2 + 1)
            counters.append(Counter())

        # print(downbeats)

        mm_notes = mm.flat.notes
        # record each note's duration / strength
        for note in mm_notes:
            # print(note.beat)
            # add notes to the appropriate counter
            note_counts = counters[0]
            if len(downbeats) > 1 and note.beat >= downbeats[1]:
                note_counts = counters[1]

            # note can be either a note or a chord...
            if note.isChord:
                # now the beat information is with the chord, but not the notes
                durations = self.get_note_dur(note, downbeats, ts, isBass=isBass)
                for n in note.notes:
                    note_counts.update({n.name: durations[0]})
                    if len(durations) > 1:
                        counters[1].update({n.name: durations[1]})
                    # print(n.name, durations)
            else:
                durations = self.get_note_dur(note, downbeats, ts, isBass=isBass)
                note_counts.update({note.name: durations[0]})
                if len(durations) > 1:
                    counters[1].update({note.name: durations[1]})
                # print(note.name, durations)
        # print(counters)
        return counters

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

        num_mms = max(len(melody_mms), len(bass_mms))

        timesig = melody_mms.measure(1).timeSignature
        for i in range(num_mms):
            chord_counters = []

            hasMelody = i < len(melody_mms)
            hasBass = i < len(bass_mms)

            if hasMelody:
                mm = melody_mms[i]
                timesig = mm.timeSignature or timesig
                # count notes in each measure of the melody line
                chord_counters = self.count_notes(mm, timesig)
            if hasBass:
                bm = bass_mms[i]
                timesig = bm.timeSignature or timesig
                # count notes in each measure of the bass line
                bass_counters = self.count_notes(bm, timesig, isBass=True)
                if chord_counters:
                    for i, c in enumerate(bass_counters):
                        chord_counters[i] += c
                else:
                    chord_counters = bass_counters
            
            chords += chord_counters

        self.chords = chords

    def write(self, min_threshold: float = 1.0, max_notes: int = None):
        """ write to file;
            suffix specifies the configuration of chords (min_threshold & max_notes)"""
        # build file path
        chords_dir = "chords"

        maxnotes_dir = f"max{max_notes}"
        if self.chord_per_measure:
            maxnotes_dir += "_per_mm"
        thresh_suffix = f"thresh{min_threshold}"
        name = ("-").join([self.tune_name, thresh_suffix])

        f_dir = os.path.join(chords_dir, maxnotes_dir)
        if not os.path.exists(f_dir):
            os.mkdir(f_dir)
        
        # write chords to file
        chord_fpath = os.path.join(f_dir, name)
        chords = self.get_chords(min_threshold=min_threshold, max_notes=max_notes)
        if self.chord_per_measure:
            keys = self.get_mm_keys()
            # make sure that we have the same #keys and #chords (excluding s and e chords)
            if len(chords)-2 != len(keys):
                raise ValueError(f"number of chords ({len(chords)}) not equal to number of keys per measure ({len(keys)})")
        with open(chord_fpath, "w") as f:
            for i, chord_notes in enumerate(chords):
                if self.chord_per_measure and i!=0 and i!=len(chords)-1:
                    # i starts from <s>. When i=1, for keys the index is 0
                    mm_keys = keys[i-1]
                    f.write(f"{mm_keys}: ")
                f.write(" ".join(chord_notes))
                f.write("\n")


def read_chord_file(fp):
    """
    reads a txt file that represents a chord generated by parse_chords
    and returns 1) a list of keys; 2) a list of chord strings, each note separated by space
    """
    keys = []
    chords = []
    for line in fp.readlines():
        line_split = line.strip().split()
        if line_split[0].endswith(':'):
            keys.append(line_split[0][:-1])
            notes = sorted(line_split[1:])
        else:
            notes = sorted(line_split)
        c = " ".join(notes)
        chords.append(c)
    return keys, chords 

def read_chord_dir(dir: str):
    """Takes a directory of chord files and appends them into one list"""
    for root, dirs, files in os.walk(dir, topdown=False):
        result = []
        for filename in files:
            if filename.startswith('.'):
                continue
            with open(os.path.join(root, filename)) as fp:
                chords = read_chord_file(fp)
                for chord in chords:
                    result.append(chord)
    return result

def write_midi_to_chords(fname: str, min_threshold: float = 1.0, max_notes: int = None, chord_per_measure: bool = False):
    print(f"writing {fname} to chords with min_threshold: {min_threshold}; max_notes: {max_notes}; chord_per_measure: {chord_per_measure}")
    tune = Tune(fname, chord_per_measure=chord_per_measure)
    # tune.score.show()
    tune.update_chords()
    tune.write(min_threshold=min_threshold, max_notes=max_notes)

def main(args):
    midi_filepath = args.mid
    midi_dir = args.dir

    # t = Tune(midi_filepath, chord_per_measure=True)
    # print(t.get_mm_keys())
    # t.score.show()
    # t.update_chords()
    # print(t.chords)
    # write_midi_to_chords(midi_filepath, max_notes=5)

    if midi_filepath:                
        write_midi_to_chords(midi_filepath, max_notes=5, chord_per_measure=True)
        # write_midi_to_chords(midi_filepath, max_notes=5)
        # write_midi_to_chords(midi_filepath)
    if midi_dir:
        for f in os.listdir(midi_dir):
            if f.startswith('.'):
                continue
            midi_filepath = os.path.join(midi_dir, f)
            if os.path.isfile(midi_filepath):
                write_midi_to_chords(midi_filepath, max_notes=5, chord_per_measure=True)
                # write_midi_to_chords(midi_filepath, max_notes=5)
                # write_midi_to_chords(midi_filepath)
    # chords = read_chord_dir("chords/max5")
    # print(chords)
    # print(len(chords))
    # print(len(Counter))
    # count = Counter(chords)
    # print(count)
    # print(len(count))
    # plt.hist(count.keys())
    # plt.show()
    
def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

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
        type=dir_path,
        help="filepath of a midi folder to parse each file in that folder into chords",
    )
    args = parser.parse_args()

    main(args)