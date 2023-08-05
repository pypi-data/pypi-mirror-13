from setuptools import setup

def format(input, start = 0):
	result = ''
	indent = False
	count = 0

	with open(input, 'r') as file:
		for line in file:
			if count > start:
				if line[:1] == '\t' and not indent:
					indent = True
					result += '::\n\n'

				if line[:1].isalnum() and indent:
					indent = False

				result += line.replace('> ', '\t')
			count += 1

	return result

blurb = 'An artificial intelligence written in python\n'
ld = blurb + format('README.md', 3)
print(ld, end='\n\n')

setup(
	name = 'myAI',
	version = '0.1.1',
	author = 'Justin Willis',
	author_email = 'sirJustin.Willis@gmail.com',
	packages = ['myAI',],
	url = 'https://bitbucket.org/bkvaluemeal/myai',
	license = 'ISC License',
	description = 'An artificial intelligence written in python',
	long_description = ld,
	install_requires = [
		'nltk >= 3.1',
		'requests >= 2.9.1'
	],
)
