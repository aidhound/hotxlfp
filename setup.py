# -*- coding: utf-8 -*-
from io import open
from setuptools import setup

setup(
    name='hotxlfp',
    version='0.0.11',
    packages=['hotxlfp', 'hotxlfp._compat', 'hotxlfp._compat.py3', 'hotxlfp.helper', 'hotxlfp.formulas', 'hotxlfp.grammarparser'],
    license='MIT',
    test_suite='tests',
    author='Leonel Câmara',
    author_email='leonelcamara@gmail.com',
    url='https://github.com/aidhound/hotxlfp',
    download_url='https://github.com/aidhound/hotxlfp/archive/0.0.11.tar.gz',
    keywords=['excel', 'formula', 'parser'],
    install_requires=['ply', 'python-dateutil'],
    long_description='\n'.join(l for l in open('README.md', encoding="utf-8").readlines() if not l.startswith('[!')),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ]
)


