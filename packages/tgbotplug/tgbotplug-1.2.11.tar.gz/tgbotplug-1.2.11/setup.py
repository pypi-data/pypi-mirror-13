#!/usr/bin/env python
import os
import re
import sys
from setuptools import setup

if sys.argv[-1] == 'pub':
    os.system('python setup.py sdist upload')
    sys.exit()

if sys.argv[-1] == 'pubtest':
    os.system('python setup.py sdist upload -r https://testpypi.python.org/pypi')
    sys.exit()

try:
    import pypandoc
    README = pypandoc.convert(os.path.join(os.path.dirname(__file__), 'README.md'), 'rst')
except(IOError, ImportError):
    README = open('README.md').read()

if sys.argv[-1] == 'readmerst':
    print(README)
    sys.exit()

# allow setup.py to be run from any path
os.chdir(os.path.dirname(os.path.abspath(__file__)))

__version__ = ''
with open('tgbot/__init__.py', 'r') as fd:
    __version__ = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(),
        re.MULTILINE
    ).group(1)

if not __version__:
    raise RuntimeError('Cannot find version information')

setup(
    name='tgbotplug',
    version=__version__,
    packages=['tgbot'],
    include_package_data=True,
    license='MIT License',
    description='Telegram plugin-based bot',
    long_description=README,
    url='https://github.com/fopina/tgbotplug',
    download_url='https://github.com/fopina/tgbotplug/tarball/v' + __version__,
    author='Filipe Pina',
    author_email='fopina@skmobi.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'requests==2.7.0',
        'peewee==2.8.0',
        'enum==0.4.6',
    ],
    keywords=['telegram', 'bot']
)
