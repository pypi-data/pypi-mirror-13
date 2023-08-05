#!/usr/bin/env python
from setuptools import setup

setup(
    name='vipython',
    version='0.0.3',
    description='Use vim with the ipython notebook',
    license='MIT',
    url='https://github.com/Russell91/vipython',
    long_description='https://github.com/Russell91/vipython',
    scripts = ['vipython_notebook'],
)

print('''
--------------------------------------------------------------------------------

# To enable vim in your notebooks, type
$ vipython_notebook enable

# To disable, type
$ vipython_notebook disable

''')
