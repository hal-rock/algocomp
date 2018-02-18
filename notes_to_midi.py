"""
Transform a list of notes into a midi file, writing that to disk.
"""

import mido
import pickle


def notes_to_midi(file_in, file_out):
    mid = mido.MidiFile()
    notes = pickle.load(open(file_in, 'rb'))

    track = mido.MidiTrack()
    track.name = "algocomp"
    for i, note in enumerate(notes):
        msg = mido.Message('note_on', note=note, time=300)
        track.append(msg)

    mid.tracks.append(track)
    mid.save(file_out)
