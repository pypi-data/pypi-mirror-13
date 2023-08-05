import sys
from distutils.core import setup, Extension

majv = 1
minv = 0

if sys.version_info < (3,):
	print("This library is only tested with Python 3.4")
	sys.exit(1)

bluray = Extension(
	'_bluread',
	define_macros = [
		('MAJOR_VERSION', str(majv)),
		('MINOR_VERSION', str(minv))
	],
	include_dirs = ['/usr/include/libbluray'],
	libraries = ['bluray'],
	sources = ['src/bluread.c']
)

setup(
	name = 'bluread',
	version = '%d.%d'%(majv,minv),
	description = 'Python wrapper for libbluray',
	author = 'Colin ML Burnett',
	author_email = 'cmlburnett@gmail.com',
	url = "https://github.com/cmlburnett/PyDvdRead",
	packages = ['bluread'],
	ext_modules = [bluray],
	classifiers = [
		'Programming Language :: Python :: 3.4'
	]
)

