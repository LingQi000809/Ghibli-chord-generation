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
    seq_length = 100
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
    return vocab,total
        

def main(args):
    seq_length = 100
    _, text = parse_chords.read_chord_dir(args.dir)
    vocab, total = get_vocab(text)
    vocab = sorted(list(vocab))
    n_vocab = len(vocab)
    char_to_int = dict((c, i) for i, c in enumerate(vocab))
    int_to_char = dict((i, c) for i, c in enumerate(vocab))
    # print(char_to_int)
    # print("Total Vocab: ",len(vocab))
    # print("Total Notes: ", len(total))
    # print(total)

    dataX, dataY = create_datasets(total, char_to_int, seq_length)
    n_patterns = len(dataX)
    X = numpy.reshape(dataX, (n_patterns, seq_length, 1))
    X = X/float(n_vocab)
    y = np_utils.to_categorical(dataY)
    model = Sequential() 
    model.add(LSTM(256, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(y.shape[1], activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    
    # filepath="weights-improvement-{epoch:02d}-{loss:.4f}.hdf5"
    # checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=True, mode='min')
    # callbacks_list = [checkpoint]
    # model.fit(X, y, epochs=20, batch_size=128, callbacks=callbacks_list)

    filename = "weights-improvement-20-1.7721.hdf5"
    model.load_weights(filename)
    model.compile(loss='categorical_crossentropy', optimizer='adam')

    start = numpy.random.randint(0, len(dataX)-1)
    pattern = dataX[start]
    print("Seed:")
    print("\"", ''.join([int_to_char[value] for value in pattern]), "\"")
    # generate characters
    with open("generate.txt", "a") as fp:
        for i in range(1000):
            x = numpy.reshape(pattern, (1, len(pattern), 1))
            x = x / float(n_vocab)
            prediction = model.predict(x, verbose=0)
            index = numpy.argmax(prediction)
            result = int_to_char[index]
            seq_in = [int_to_char[value] for value in pattern]
            fp.write(result)
            pattern.append(index)
            pattern = pattern[1:len(pattern)]
        print("\nDone.")


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