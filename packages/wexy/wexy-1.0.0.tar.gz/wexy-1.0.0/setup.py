# coding:utf-8

from setuptools import setup, find_packages

long_description = """\
WSGI environ proxy.

See detail @ http://github.com/tomokinakamaru/wexy.

Copyright (c) 2016, Tomoki Nakamaru.

License: MIT
"""

setup(
    author='Tomoki Nakamaru',
    author_email='tomoki.nakamaru@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    description='WSGI environ proxy',
    license='MIT',
    long_description=long_description,
    name='wexy',
    packages=find_packages(),
    platforms='any',
    url='http://github.com/tomokinakamaru/wexy',
    version='1.0.0'
)
