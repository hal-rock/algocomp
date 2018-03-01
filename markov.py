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
        self.tmax = 500 # reasonable max delay between notes

        self.n_freqs = np.ones((self.rnge, self.rnge)) + priors
        self.v_freqs = np.ones((127, 127)) + priors
        self.t_freqs = np.ones((self.tmax, self.tmax)) + priors

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

    def compose(self, out: str, length: int):
        """
        Compose a sequence of notes and save them to a specified MIDI file.

        :param length: the number of notes to compose
        :param out: the name of the file to create and save to
        """
        # get probabilities from the note counts
        n_sums = np.sum(self.n_freqs, 1)
        v_sums = np.sum(self.v_freqs, 1)
        t_sums = np.sum(self.t_freqs, 1)
        n_probs = np.divide(self.n_freqs, n_sums)
        v_probs = np.divide(self.v_freqs, v_sums)
        t_probs = np.divide(self.t_freqs, t_sums)

        # choose random starting note then compose
        start_p = np.sum(n_probs / np.sum(n_probs), 1)
        start = np.random.choice(range(self.rnge), p=start_p)
        msgs = [mido.Message('note_on', note=start+self.min_b, time=0)]

        for i in range(length):
            # get next note's probs, summing to 1 despite floating point issues
            n_choices = np.dot(n_probs, self._vectorize(msgs[-1], 'note'))
            v_choices = np.dot(v_probs, self._vectorize(msgs[-1], 'velo'))
            t_choices = np.dot(t_probs, self._vectorize(msgs[-1], 'time'))
            n_choices /= np.sum(n_choices)
            v_choices /= np.sum(v_choices)
            t_choices /= np.sum(t_choices)

            # choose a random note and add it to the composition
            note = np.random.choice(range(self.min_b, self.max_b), p=n_choices)
            velo = np.random.choice(range(127), p=v_choices)
            time = np.random.choice(range(self.tmax), p=t_choices)
            note = mido.Message('note_on', note=note, velocity=velo, time=time)
            msgs.append(note)

        # write MIDI track out to file
        m_out = mido.MidiFile()
        m_out.tracks.append(mido.MidiTrack(msgs))
        m_out.save(out)

    def _vectorize(self, msg: mido.Message, typ: str) -> np.ndarray:
        """
        An internal helper function to convert a MIDI note_on message into
        a one-hot vector for dotting with a transition matrix.

        :param msg: the MIDI message to vectorize
        :return returns the one-hot vector encoding that message's note
        """
        # unfortunately the logic is different for each case
        if typ == 'note':
            vector = np.zeros((self.rnge,))
            vector[msg.note - self.min_b] = 1
        elif typ == 'velo':
            vector = np.zeros((127,))
            vector[msg.velocity] = 1
        elif typ == 'time':
            vector = np.zeros((self.tmax,))
            vector[msg.time] = 1

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

        # get note_on MIDI messages and add the transitions to the matrices
        notes = [m for m in longest if m.type == 'note_on']
        for i, msg in enumerate(notes):
            if msg.note in range(self.min_b, self.max_b):
                indx = notes[i-1].note - self.min_b
                self.n_freqs[msg.note - self.min_b][indx] += 1
                self.v_freqs[msg.velocity][notes[i-1].velocity] += 1
                if max(msg.time, notes[i-1].time) < self.tmax:
                    self.t_freqs[msg.time][notes[i-1].time] += 1

        # first one is not a real transition, from end to beginning
        self.n_freqs[notes[0].note-self.min_b][notes[-1].note-self.min_b] -= 1
        self.v_freqs[notes[0].velocity][notes[-1].velocity] -= 1
        self.v_freqs[notes[0].time][notes[-1].time] -= 1
