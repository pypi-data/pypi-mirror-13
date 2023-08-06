#!/usr/bin/env python
import re
from codecs import open
from setuptools import setup

with open('README.rst', encoding='utf8') as readme_file:
    readme = readme_file.read()

with open('maxmindupdater/__init__.py', encoding='utf8') as init_py:
    metadata = dict(re.findall(r"__([a-z]+)__ = '([^']+)'", init_py.read()))


setup(
    name='maxmindupdater',
    version=metadata['version'],
    description=metadata['doc'],
    long_description=readme,
    author='Yola',
    author_email='engineers@yola.com',
    license='MIT (Expat)',
    url=metadata['doc'],
    packages=['maxmindupdater'],
    entry_points={
        'console_scripts': ['maxmind-updater=maxmindupdater.__main__:main'],
    },
    install_requires=[
        'requests >= 2.0.0, < 3.0.0',
        'maxminddb >= 1.0.0, < 2.0.0'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
