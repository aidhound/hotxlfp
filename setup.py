# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='hotxlfp',
    version='0.0.1',
    packages=['hotxlfp',],
    license='MIT',
    test_suite='tests',
    author='Leonel Câmara',
    url='https://github.com/aidhound/hotxlfp',
    keywords=['excel', 'formula', 'parser'],
    install_requires=open('requirements.txt').readlines(),
    long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)


