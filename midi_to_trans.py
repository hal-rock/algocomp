"""
Convert a midi file to a transition matrix and save that matrix to disk.
"""

import numpy as np
import mido


def midi_to_trans(fname_in: str, fname_out: str):
    midi_in = mido.MidiFile(fname_in)

    # longest track is most likely to have actual notes
    longest = midi_in.tracks[0]
    for track in midi_in.tracks:
        if len(track) > len(longest):
            longest = track

    # transition matrix of our track
    trans_mat = transition(longest)

    # save to a file and done
    np.save(fname_out, trans_mat)


def transition(track):
    notes = np.zeros(shape=(128, 128), dtype=np.int32)

    only_notes = [m for m in track if m.type == 'note_on']
    for i, msg in enumerate(only_notes):
        notes[msg.note][only_notes[i-1].note] += 1

    # normalize to probabilities, don't divide by zero
    notes = np.divide(notes, np.maximum(sum(notes), np.ones(notes.shape)))

    return notes
