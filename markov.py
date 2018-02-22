"""
Markov chain composition
"""

import numpy as np
import mido
from composer import Composer


class Markov(Composer):
    """
    A simple markov chain composer.
    """

    def __init__(self, bounds: tuple=(0, 127),
                 priors: int=0):
        """
        Initialize a first-order Markov chain composer.

        :param bounds: the lower and upper bound of MIDI notes for the
        composer, between 0 and 127 inclusive
        :param priors: a bias towards randomness vs. learned frequencies,
        the amount of each note "already seen" by the process
        """

        self.min_b = bounds[0]
        self.max_b = bounds[1]
        self.rnge = bounds[1] - bounds[0]

        self.freqs = np.ones((self.rnge, self.rnge)) * priors

    def train(self, **kwargs):
        """
        Adds to the current Markov transition matrix with note counts from the
        longest tracks in MIDI files in the given filename (or list of names).

        :param fname: a string, the filename to train on
        :param fnames: a list of strings, the filenames to train on, will be
        ignored if fname is given

        :return returns nothing
        """

        if "fname" in kwargs:
            self._learn_from(kwargs["fname"])

        elif "fnames" in kwargs:
            for name in kwargs["fnames"]:
                self._learn_from(name)

    def compose(self, out: str, length: int, delta: int=300):
        """
        Compose a sequence of notes and save them to a specified MIDI file.

        :param length: the number of notes to compose
        :param out: the name of the file to create and save to
        :param delta: the time (in ms) between notes
        """
        # get probabilities from the note counts
        sums = np.sum(self.freqs, 1)
        probs = np.divide(self.freqs, np.maximum(sums, np.ones(sums.shape)))

        # choose random starting note then compose
        start_p = np.sum(probs / np.sum(probs), 1)
        start = np.random.choice(range(self.rnge), p=start_p)
        msgs = [mido.Message('note_on', note=start+self.min_b, time=delta)]
        for i in range(length):
            # get next note's probs, summing to 1 despite floating point issues
            choices = np.dot(probs, self._vectorize(msgs[-1]))
            choices /= np.sum(choices)

            note = np.random.choice(range(self.min_b, self.max_b), p=choices)
            note = mido.Message('note_on', note=note, time=delta)
            msgs.append(note)

        # write MIDI track out to file
        m_out = mido.MidiFile()
        m_out.tracks.append(mido.MidiTrack(msgs))
        m_out.save(out)

    def _vectorize(self, msg: mido.Message) -> np.ndarray:
        """
        An internal helper function to convert a MIDI note_on message into
        a one-hot vector for dotting with a transition matrix.

        :param msg: the MIDI message to vectorize
        :return returns the one-hot vector encoding that message's note
        """
        vector = np.zeros((self.rnge,))
        vector[msg.note - self.min_b] = 1
        return vector

    def _learn_from(self, fname: str):
        """
        An internal helper function to add to the transition matrix from a
        file.

        :param fname: the name of the MIDI file to read from
        """

        midi = mido.MidiFile(fname)

        # find the longest track
        longest = midi.tracks[np.argmax([len(track) for track in midi.tracks])]

        # get note_on MIDI messages and add the transitions to the matrix
        notes = [m for m in longest if m.type == 'note_on']
        for i, msg in enumerate(notes):
            if msg.note in range(self.min_b, self.max_b):
                indx = notes[i-1].note - self.min_b
                self.freqs[msg.note - self.min_b][indx] += 1

        # first one is not a real transition, from end to beginning
        self.freqs[notes[0].note-self.min_b][notes[-1].note-self.min_b] -= 1
