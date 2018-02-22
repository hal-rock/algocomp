# Fun with algorithmic composition

This is a place to play around with algorithmic composition and a tool for me 
to practice making non-terrible software. Currently the only thing I have 
working is a simple first-order Markov chain composer, but that should change. 


## Installation

There's not really much to install; just clone the repository and use the files 
from the directory, or move them anywhere you want. I'll probably add this to 
PyPI if/when it's less barebones. 


## Current requirements

* Python 3.5 or higher (because of type hints)
* mido
* numpy
* a MIDI synthesizer (if you want to hear the results)


## (Likely) Future requirements

* nupic
* PyTorch

## Examples

Again, there's not really much yet, but running looking at `example.py` will 
show a couple of simple use cases, and running it will give you some bad 
Markov music to listen to (a couple of statistical butcherings of Beethoven's 
Sonata No. 14 in C# minor, specifically). 
