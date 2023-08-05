#!/usr/bin/env python

from distutils.core import setup

setup(
    name='python-paycoinrpc',
    version='0.1.1',
    description='Enhanced version of python-jsonrpc for use with Paycoin',
    long_description=open('README.rst').read(),
    author='Mitchell Cash',
    author_email='<mitchell@fastmail.com.au>',
    maintainer='Mitchell Cash',
    maintainer_email='<mitchell@fastmail.com.au>',
    url='http://github.com/mitchellcash/python-paycoinrpc',
    packages=['paycoinrpc'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)
