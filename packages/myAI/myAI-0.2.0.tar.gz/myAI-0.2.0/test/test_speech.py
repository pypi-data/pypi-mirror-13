from myAI.adapters.tts import google as gTTS
from myAI.adapters.stt import google as gSTT
from myAI.adapters.tts import festival
import unittest

class TestGoogleSpeech(unittest.TestCase):
	"""
	Tests if Google can correctly turn text-to-speech-to-text
	"""

	def setUp(self):
		self.tts = gTTS.tts()
		self.stt = gSTT.stt()

	def test_hello_world(self):
		text = 'hello world'
		audio = self.tts.process(text, 'stdout')
		audio = self.stt.convert(audio)
		result = self.stt.process(audio)

		self.assertEqual(text, result)

	def test_invalid_language(self):
		self.assertRaises(Exception, lambda: gTTS.tts('mumbo-jumbo'))
		self.assertRaises(Exception, lambda: gSTT.stt('mumbo-jumbo'))

	def test_no_text(self):
		self.assertFalse(self.tts.process(''))
		self.assertFalse(self.stt.process(''))

class TestFestival(unittest.TestCase):
	"""
	Tests if Festival can correctly turn text-to-speech
	"""

	def setUp(self):
		self.tts = festival.tts()

	def test_hello_world(self):
		text = 'hello world'
		audio = self.tts.process(text, 'stdout')

		self.assertNotEqual('', audio)

	def test_invalid_language(self):
		self.assertRaises(Exception, lambda: festival.tts('mumbo-jumbo'))

	def test_no_text(self):
		self.assertFalse(self.tts.process(''))

if __name__ == "__main__":
	unittest.main()
