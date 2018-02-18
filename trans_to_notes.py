"""
Turn a note transition matrix and starting note into a sequence of notes.
"""

import numpy as np
import pickle


def trans_to_notes(trans_in, notes_out, length, start):
    trans = np.load(trans_in)

    notes = [start]
    for i in range(length):
        next = np.dot(trans, vectorize(notes[i]))
        notes.append(np.random.choice(range(128), p=next))

    pickle.dump(notes, open(notes_out, 'wb'))


def vectorize(note):
    vec = np.zeros(shape=(128,), dtype=np.int32)
    vec[note] = 1
    return vec
