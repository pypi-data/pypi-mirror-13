import importlib
import logging

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(
	level = logging.DEBUG,
	format = '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S'
)

class BasicBot(object):
	"""
	A basic AI with a speech adapter

	Args:
		name (str): The name of the AI
		lang (str): The language to speak
	"""

	def __init__(self, name, lang = 'en-us', **kwargs):
		self.name = name
		self.logger = logging.getLogger('myAI')
		self.logger.info('Initializing %s' % (name))

		self.tts = importlib.import_module(
			kwargs.get(
				'tts',
				'myAI.adapters.tts.google'
			)
		).tts(lang)

		self.stt = importlib.import_module(
			kwargs.get(
				'stt',
				'myAI.adapters.stt.google'
			)
		).stt(lang)

	def talk(self):
		"""
		A sequence to collect an input and return a response
		"""

		return self.get_response(self.get_input())

	def get_input(self):
		"""
		Return the processed input
		"""

		return self.stt.process(self.stt.listen())

	def get_response(self, input):
		"""
		Return the AI's response based on the input
		"""

		return self.tts.listen(self.tts.process(input))
