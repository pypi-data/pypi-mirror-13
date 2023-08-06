# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='apiclient-requests',
    version='0.1.0',
    packages=[
        'apiclient',
    ],
    author='Suraj Arya',
    author_email='suraj.p.arya@gmail.com',
    description='A simple python client for the perfios APIs',
    url='https://github.com/suraj-arya/apiclient-requests',
    license='MIT',

    install_requires=[
        "requests==2.5.1"
    ],
)
