from setuptools import setup

setup(name='kissanime_dl',
	version='1.1.5',
	description='Easy downloading .mp4s from kissanime.to',
	url="https://github.com/wileyyugioh/kissanime_dl",
	author='Wiley Y.',
	author_email="wileythrowaway001@gmail.com",
	license='MIT',
	packages=['kissanime_dl'],
	install_requires=[
	'requests',
	'lxml'
	],
	zip_safe=False,
	scripts=['bin/kissanime-dl']
	)