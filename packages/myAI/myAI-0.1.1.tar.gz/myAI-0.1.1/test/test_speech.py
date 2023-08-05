from myAI.adapters.tts import google as gTTS
from myAI.adapters.stt import google as gSTT
import unittest

class TestGoogleSpeech(unittest.TestCase):
	"""
	Tests if Google can correctly turn text-to-speech-to-text
	"""

	def setUp(self):
		self.tts = gTTS.tts()
		self.stt = gSTT.stt()

	def test_speech(self):
		text = 'hello world'
		audio = self.tts.process(text)
		audio = self.stt.convert(audio)
		result = self.stt.process(audio)

		self.assertEqual(text, result)

if __name__ == "__main__":
	unittest.main()
