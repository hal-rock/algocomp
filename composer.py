"""
"""


class Composer:
    """
    Base composer class, to be inherited from by specific composers.
    """

    def train(self, **kwargs):
        """
        Should train the composer object on the midi file specified
        by a string, or on the multiple midi files specified in a list
        of strings. Subsequent trainings do not erase previous ones.

        :param fname: a filename, if a single file is to be trained on
        :param fnames: a list of filenames, if multiple files are to be
        trained on

        :return returns nothing
        """
        raise NotImplementedError("this method was not implemented")

    def compose(self, out: str, **kwargs):
        """
        Should generate music based on the composer's trained state.

        :param out: the filename of the generated midi file

        :return returns nothing
        """
        raise NotImplementedError("this method was not implemented")
