from distutils.core import setup

with open('README') as file:
	long_description = file.read()

setup(
	name='log2web',
	version='0.0.5',
	py_modules=['log2web'],
	author ='becxer',
	author_email='becxer87@gmail.com',
	url = 'https://github.com/becxer/log2web',
	description ='Make log file to tail-watchable through web',
	long_description = long_description,
	license='MIT',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Topic :: Software Development :: Build Tools',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7',
	],
	entry_points={
		'console_scripts':[
			'log2web = log2web:main',
		]
	}
)


	
