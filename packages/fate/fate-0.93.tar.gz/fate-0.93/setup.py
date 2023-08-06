#!/usr/bin/env python
from os.path import dirname, join
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name == 'mbcs')
    codecs.register(func)

from setuptools import setup, find_packages

def read(filename):
    """
    Read content from utility files
    """

    return open(join(dirname(__file__), filename)).read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '0.93'

setup(
    name='fate',
    version=version,
    install_requires=requirements,
    author='Karan Sharma',
    author_email='karansharma1295@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/mr-karan/fate/',
    license='MIT',
    description='Browse FontAwesome Icons in your terminal',
    long_description=read('README.rst'),
    scripts=['bin/fate'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Text Processing :: Fonts',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
