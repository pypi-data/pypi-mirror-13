myAI Wiki
---------

An artificial intelligence written in python

Install
-------

	pip install myAI

Requires
--------

myAI requires [SoX] to process sound. It does this primarily with the `rec`
command and some chained effects. myAI also requires [Festival] to operate
locally. The Festival TTS system synthesises speech locally without the
need for Google.

Usage
-----

```
#!python

from myAI import AI

jarvis = AI.BasicBot('Jarvis')

while True:
	jarvis.talk()
```

How it works
------------

myAI works by listening to your voice until it hears 3 seconds of silence. It
then removes the space before and after the speech, and pads it with an extra
second of silence in the beginning to help better understand what you're
saying. Your speech is processed and a response is created which is played
back for you to hear.

myAI is based on [ChatterBot], a *"machine learning, conversational dialog
engine"*, but with some extra features to make it my AI.

[SoX]: http://sourceforge.net/projects/sox/files/latest/download?source=files
[Festival]: http://www.cstr.ed.ac.uk/projects/festival/
[ChatterBot]: https://github.com/gunthercox/ChatterBot
