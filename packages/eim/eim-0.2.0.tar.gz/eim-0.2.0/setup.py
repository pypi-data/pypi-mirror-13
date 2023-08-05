from setuptools import setup

setup(
    name='eim',
    version='0.2.0',
    packages=['eim',
              'eim.tools'],
    url='http://www.musicsensorsemotion.com/',
    license='',
    author='Brennon Bortz',
    author_email='brennon@vt.edu',
    description='Library for interacting with Emotion and Motion resources',
    install_requires=['pymongo', 'pandas', 'mongoengine']
)
