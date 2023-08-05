import subprocess
import calendar
import requests
import json
import math
import nltk
import time
import re

LANGUAGES = {
	'af' : 'Afrikaans',
	'sq' : 'Albanian',
	'ar' : 'Arabic',
	'hy' : 'Armenian',
	'ca' : 'Catalan',
	'zh' : 'Chinese',
	'zh-cn' : 'Chinese (Mandarin/China)',
	'zh-tw' : 'Chinese (Mandarin/Taiwan)',
	'zh-yue' : 'Chinese (Cantonese)',
	'hr' : 'Croatian',
	'cs' : 'Czech',
	'da' : 'Danish',
	'nl' : 'Dutch',
	'en' : 'English',
	'en-au' : 'English (Australia)',
	'en-uk' : 'English (United Kingdom)',
	'en-us' : 'English (United States)',
	'eo' : 'Esperanto',
	'fi' : 'Finnish',
	'fr' : 'French',
	'de' : 'German',
	'el' : 'Greek',
	'ht' : 'Haitian Creole',
	'hi' : 'Hindi',
	'hu' : 'Hungarian',
	'is' : 'Icelandic',
	'id' : 'Indonesian',
	'it' : 'Italian',
	'ja' : 'Japanese',
	'ko' : 'Korean',
	'la' : 'Latin',
	'lv' : 'Latvian',
	'mk' : 'Macedonian',
	'no' : 'Norwegian',
	'pl' : 'Polish',
	'pt' : 'Portuguese',
	'pt-br' : 'Portuguese (Brazil)',
	'ro' : 'Romanian',
	'ru' : 'Russian',
	'sr' : 'Serbian',
	'sk' : 'Slovak',
	'es' : 'Spanish',
	'es-es' : 'Spanish (Spain)',
	'es-us' : 'Spanish (United States)',
	'sw' : 'Swahili',
	'sv' : 'Swedish',
	'ta' : 'Tamil',
	'th' : 'Thai',
	'tr' : 'Turkish',
	'vi' : 'Vietnamese',
	'cy' : 'Welsh'
}

class tts(object):
	def __init__(self, lang = 'en-us'):
		"""
		Text-to-Speech (TTS) is an interface to Google's TTS api

		Args:
			lang (str): The language to use (default: en-us)
		"""

		if lang.lower() not in LANGUAGES:
			raise Exception('Language not supported: %s' % lang)
		else:
			self.lang = lang.lower()

		self.token_key = None

	def process(self, text = None):
		"""
		Processes a given text to speech

		Args:
			text (str): The text to process
		"""

		if not text:
			return
		else:
			text = nltk.sent_tokenize(text)

		result = b''
		for idx, part in enumerate(text):
			payload = {
				'ie' : 'UTF-8',
				'q' : part,
				'tl' : self.lang,
				'total' : len(text),
				'idx' : idx,
				'client' : 't',
				'textlen' : len(part),
				'tk' : self._token(part)
			}
			headers = {
				'Referer' : 'http://translate.google.com/',
				'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
			}

			try:
				r = requests.get('https://translate.google.com/translate_tts', params = payload, headers = headers)
				r.raise_for_status()

				for chunk in r.iter_content(chunk_size = 1024):
					result += chunk
			except Exception as e:
				raise

		return result

	def listen(self, speech):
		"""
		Plays a binary mp3 with SoX

		Args:
			speech (bin): The binary mp3 to play
		"""

		subprocess.Popen(
			'play -t mp3 - -q',
			stdin = subprocess.PIPE,
			stderr = subprocess.DEVNULL,
			shell = True
		).communicate(speech)

	def _rshift(self, val, n):
		return val>>n if val >= 0 else (val+0x100000000)>>n

	def _work_token(self, a, salt):
		for i in range(0, len(salt) - 2, 3):
			char = salt[i + 2]
			d = ord(char[0]) - 87 if char >= 'a' else int(char)
			d = self._rshift(a, d) if salt[i + 1] == '+' else a << d
			a = a + d & 4294967295 if salt[i] == '+' else a ^ d

		return a

	def _token(self, text, seed = None):
		if self.token_key is None and seed is None:
			timestamp = calendar.timegm(time.gmtime())
			hours = int(math.floor(timestamp / 3600))
			self.token_key = hours

		e = 0
		f = 0
		d = [None] * len(text)

		for c in text:
			g = ord(c)

			if 128 > g:
				d[e] = g
				e += 1
			elif 2048 > g:
				d[e] = g >> 6 | 192
				e += 1
			else:
				if 55296 == (g & 64512) and f + 1 < len(text) and 56320 == (ord(text[f + 1]) & 64512):
					f += 1
					g = 65536 + ((g & 1023) << 10) + (ord(text[f]) & 1023)
					d[e] = g >> 18 | 240
					e += 1
					d[e] = g >> 12 & 63 | 128
					e += 1
				else:
					d[e] = g >> 12 | 224
					e += 1
					d[e] = g >> 6 & 63 | 128
					e += 1
					d[e] = g & 63 | 128
					e += 1

		a = seed if seed is not None else self.token_key

		if seed is None:
			seed = self.token_key

		for value in d:
			a += value
			a = self._work_token(a, '+-a^+6')

		a = self._work_token(a, '+-3^+b+-f')

		if 0 > a:
			a = (a & 2147483647) + 2147483648

		a %= 1E6
		a = int(a)

		return str(a) + '.' + str(a ^ seed)

class stt(object):
	def __init__(self, lang = 'en-us'):
		"""
		Speech-to-Text (STT) is an interface to Google's STT api

		Args:
			lang (str): The language to use (default: en-us)
		"""

		if lang.lower() not in LANGUAGES:
			raise Exception('Language not supported: %s' % lang)
		else:
			self.lang = lang.lower()

		self.get_profile()

	def process(self, speech):
		"""
		Processes a given speech to text

		Args:
			speech (bin): The binary flac to process
		"""

		url = 'http://www.google.com/speech-api/v2/recognize?client=chromium&lang=%s&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw' % (self.lang)
		headers = {'Content-Type': 'audio/x-flac; rate=48000'}
		response = requests.post(url, data = speech, headers = headers).text

		result = None
		for line in response.split('\n'):
			try:
				result = json.loads(line)['result'][0]['alternative'][0]['transcript']
				break
			except:
				pass

		return result

	def convert(self, speech, format = 'mp3'):
		"""
		Converts audio of the format, format, to flac

		Args:
			speech (bin): The binary audio to convert
			format (str): The format of the audio (default = mp3)
		"""

		p = subprocess.Popen(
			'sox -t %s - -t flac - rate 48k' % (format),
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			shell = True
		)
		stdout, stderr = p.communicate(speech)

		return stdout

	def listen(self):
		"""
		Records a sample of speech
		"""

		p = subprocess.Popen(
			'rec -c 1 -r 48k -q -t flac - noisered - 0.21 silence -l 1 0.0 1% 1 3.0 5% pad 1 0',
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.DEVNULL,
			shell = True
		)
		stdout, stderr = p.communicate(self.profile)

		return stdout

	def get_profile(self):
		"""
		Records a 5 second sample for noise reduction
		"""

		print('Recording noise profile')
		self.profile = subprocess.check_output(
			'rec -c 1 -r 48k -q -n noiseprof - trim 0 5',
			stderr = subprocess.DEVNULL,
			shell = True
		)
		print('Done.')
