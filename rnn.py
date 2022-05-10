import parse_chords 
import numpy
import os
import time
import argparse
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.callbacks import ModelCheckpoint
from keras.utils import np_utils

def create_datasets(notes, char_to_int, seq_length):
    dataX = []
    dataY = []
    n_chars = len(notes)
    
    for i in range(0, n_chars - seq_length, 1):
        seq_in = notes[i:i + seq_length]
        seq_out = notes[i + seq_length]
        dataX.append([char_to_int[char] for char in seq_in])
        dataY.append(char_to_int[seq_out])
    return dataX, dataY

def get_vocab(l):
    vocab = set()
    total = []
    for s in l:
        notes = s.split()
        for note in notes:
            vocab.add(note)
            total.append(note)
        total.append(" ")
    vocab.add(" ")
    return vocab,total

def raw_to_output(l):
    result = []
    for s in l:
        if s == "<e>":
            break
        if s == " ":
            result.append("\n")
        else:
            result.append(s)
            result.append(" ")
    result.append("\n")
    return result 

def get_last_chord_of_seed(l):
    result = []
    index = len(l)-1
    con = True 
    while(con):
        cur_char = l[index]
        if cur_char == " ":
            if index==len(l)-1:
                pass
            else:
                 con = False 
        result.append(cur_char)
        index -= 1
    result.reverse()
    return result

def generate_output(seq_length, notelength, filename, dir, output_file):
    _, text = parse_chords.read_chord_dir(dir)
    vocab, total = get_vocab(text)
    vocab = sorted(list(vocab))
    n_vocab = len(vocab)
    char_to_int = dict((c, i) for i, c in enumerate(vocab))
    int_to_char = dict((i, c) for i, c in enumerate(vocab))

    dataX, dataY = create_datasets(total, char_to_int, seq_length)
    n_patterns = len(dataX)
    X = numpy.reshape(dataX, (n_patterns, seq_length, 1))
    X = X/float(n_vocab)
    y = np_utils.to_categorical(dataY)
    model = Sequential()
    model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2]), return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(256))
    model.add(Dropout(0.2))
    model.add(Dense(y.shape[1], activation='softmax'))

    model.load_weights(filename)
    model.compile(loss='categorical_crossentropy', optimizer='adam')

    start = numpy.random.randint(0, len(dataX)-1)
    pattern = dataX[start]
    seed = [int_to_char[value] for value in pattern]
    last_chord = get_last_chord_of_seed(seed)
    
    # generate characters
    chords = []
    for i in last_chord:
        chords.append(i)
    j = 0
    while j < notelength:
        x = numpy.reshape(pattern, (1, len(pattern), 1))
        x = x / float(n_vocab)
        prediction = model.predict(x, verbose=0)
        index = numpy.argmax(prediction)
        result = int_to_char[index]
        if result != " ":
            j += 1
        seq_in = [int_to_char[value] for value in pattern]
        chords.append(result)
        pattern.append(index)
        pattern = pattern[1:len(pattern)]
    print("\nDone.")
    
    chords = raw_to_output(chords)
    if chords[0] == "\n":
        chords = chords[1:]
    with open(output_file, "x") as fp:
        fp.write(''.join(chords))

        

def main(args):
    generate_output(100, 25, "rnn_weights/max5_per_mm/100.hdf5", "chords/max5_per_mm", "OUTPUTS")


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