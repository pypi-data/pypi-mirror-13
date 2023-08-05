from distutils.core import setup

majv = 1
minv = 0

setup(
	name = 'crudexml',
	version = "%d.%d" %(majv,minv),
	description = "Python module that implements a crude XML DOM",
	author = "Colin ML Burnett",
	author_email = "cmlburnett@gmail.com",
	url = "",
	packages = ['crudexml'],
	package_data = {'crudexml': ['crudexml/__init__.py']},
	classifiers = [
		'Programming Language :: Python :: 3.4'
	]
)
