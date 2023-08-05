from myAI import speech
import unittest

class TestSpeech(unittest.TestCase):
	"""
	Tests if the speech module can correctly turn text-to-speech-to-text
	"""

	def setUp(self):
		self.tts = speech.tts()
		self.stt = speech.stt()

	def test_speech(self):
		text = 'hello world'
		audio = self.tts.process(text)
		audio = self.stt.convert(audio)
		result = self.stt.process(audio)

		self.assertEqual(text, result)

if __name__ == "__main__":
	unittest.main()
