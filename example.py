"""
Example usage of Markov chain (and currently only) composer.
"""

from markov import Markov


# Beethoven's Sonata No. 14 in C# Minor (Moonlight), Opus 27/2
# obtained from www.piano-midi.de/beeth.htm
pieces = ["mond_1.mid", "mond_2.mid", "mond_3.mid"]

# exactly copying the first-order transitions
beethoven = Markov()
beethoven.train(fnames=pieces)
beethoven.compose("less_random.mid", length=300, delta=400)  # 2 minutes long

# with a strongish prior bias towards randomness -- sounds worse, I think
badhoven = Markov(priors=200)
badhoven.train(fnames=pieces)
beethoven.compose("more_random.mid", length=200, delta=300)  # 1 minute long

# now you can play the output files with whatever midi player you have
# though a first-order Markov model really doesn't sound very good
