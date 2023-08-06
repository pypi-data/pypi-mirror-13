# aupyom

[![Build Status](https://travis-ci.org/pierre-rouanet/aupyom.svg?branch=master)](https://travis-ci.org/pierre-rouanet/aupyom)

Real-time Audio time-scale and pitch modification Python library.

# Documentation

Aupyom is the pure-python library designed to allow for quick and easy sounds mixing. It has been designed to let you shift the pitch and change the time-scale of sounds in real time.

As aupyom API is really simple, you only need to know a few methods to start playing, the documentation is given as few demonstration notebooks:

* [Playing and mixing multiple sounds](./examples/Playing\ and\ mixing\ multiple\ sounds.ipynb)
* [Live modification of the pitch and time-scale of sounds](./examples/Live\ modification\ of\ the\ pitch\ and\ time-scale\ of\ sounds.ipynb)

# Installation

The last stable release is available on PyPI. It can be install via:

```bash
pip install aupyom
```

You can also install it from source:
```bash
python setup.py install
```

## Dependencies

Aupyom works with Python >= 2.7 and Python>=3.4.

Aupyom requires different libraries:
* [numpy](http://www.numpy.org): for the low-level sound processing
* [librosa](https://github.com/bmcfee/librosa): for higher-level sound processing and IO
* [sounddevice](http://python-sounddevice.readthedocs.org/): a python bindings for the [PortAudio](http://www.portaudio.com) library - used to play sounds

# Integration with Poppy robots

Aupyom has been originally designed in the context of the [Poppy-project](https://www.poppy-project.org) aiming at developing open-source and easy-to-use robots. They are notably used in educational context for teaching computer science and discover IoT and robotics.

[Dedicated demonstration notebooks]() have been designed showing how the movement of a robot can be used to lively modify sound pitch and time-scale!

[![Vimeo Preview](./doc/vimeo-preview.jpg)](https://vimeo.com/107599850)

Thanks to that, aupyom has also been connected to [Snap!](http://snap.berkeley.edu) a variant of the famous visual programming language allowing the design of interface for intuitively modifying and mixing of sounds.

![IMAGE] (TODO IMAGE)
