import importlib
import logging

logging.getLogger('requests').setLevel(logging.WARNING)
logging.basicConfig(
	level = logging.DEBUG,
	format = '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
	datefmt = '%Y-%m-%d %H:%M:%S'
)

class Bot(object):
	"""
	The parent of all AI bots containing basic functions to interact

	Args:
		name (str): The name of the AI
		lang (str): The language to speak
	"""

	def __init__(self, name, lang = 'en-us', **kwargs):
		self.name = name
		self.logger = logging.getLogger('myAI')
		self.logger.info('Initializing %s' % (name))

	def talk(self):
		"""
		A sequence to collect an input and return a response
		"""

		return self.get_response(self.get_input())

	def get_input(self, input = None):
		"""
		Return the processed input

		Args:
			input (bin): Optional binary audio to process
		"""

		return self.stt.process(input)

	def get_response(self, input = None):
		"""
		Return the AI's response based on the input

		Args:
			input (str): The input statement to the bot
		"""

		return self.tts.process(input)

class BasicBot(Bot):
	"""
	A basic AI with a speech adapter

	Args:
		name (str): The name of the AI
		lang (str): The language to speak
	"""

	def __init__(self, name, lang = 'en-us', **kwargs):
		super().__init__(name, lang, **kwargs)

		self.tts = importlib.import_module(
			kwargs.get(
				'stt',
				'myAI.adapters.tts.google'
			)
		).tts(lang)

		self.stt = importlib.import_module(
			kwargs.get(
				'stt',
				'myAI.adapters.stt.google'
			)
		).stt(lang)

class LocalBot(Bot):
	"""
	A local AI with a speech adapter

	Args:
		name (str): The name of the AI
		lang (str): The language to speak
	"""

	def __init__(self, name, lang = 'en-us', **kwargs):
		super().__init__(name, lang, **kwargs)

		self.tts = importlib.import_module(
			kwargs.get(
				'tts',
				'myAI.adapters.tts.festival'
			)
		).tts(lang)

	def get_input(self):
		"""
		Return the processed input
		"""

		self.logger.warn('Local speech-to-text has not yet been implemented')
		return input('Input: ')
