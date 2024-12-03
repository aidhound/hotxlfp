# -*- coding: utf-8 -*-
from io import open
from setuptools import setup

setup(
    name='hotxlfp',
    version='1.0.2',
    packages=['hotxlfp', 'hotxlfp._compat', 'hotxlfp.helper', 'hotxlfp.formulas', 'hotxlfp.grammarparser'],
    license='MIT',
    author='Leonel Câmara',
    author_email='leonelcamara@gmail.com',
    url='https://github.com/aidhound/hotxlfp',
    download_url='https://github.com/aidhound/hotxlfp/archive/1.0.2.tar.gz',
    keywords=['excel', 'formula', 'parser'],
    install_requires=['ply', 'python-dateutil'],
    long_description='\n'.join(l for l in open('README.md', encoding="utf-8").readlines() if not l.startswith('[!')),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ]
)


