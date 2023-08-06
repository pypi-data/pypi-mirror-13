from setuptools import setup
import sopts

setup (
	name ='sopts',
	version = sopts.__version__,
	description ='command line argument parser',
	license = 'GPLv3',
	packages = ['sopts'],
	zip_safe = False ,
	)
