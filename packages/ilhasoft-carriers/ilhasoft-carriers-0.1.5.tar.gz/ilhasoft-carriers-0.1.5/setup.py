# -*- coding: utf-8 -*-
from distutils.core import setup

CLASSIFIERS = [
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development',
]

setup(
    name='ilhasoft-carriers',
    version='0.1.5',
    author='Teeh Amaral - Ilhasoft',
    author_email='ed.amaral@ilhasoft.com.br',
    packages=['carrier'],
    url='https://github.com/Ilhasoft/carriers',
    license='BSD licence, see LICENCE.txt',
    description='Library consultation phone carriers around the world.',
    download_url="https://github.com/Ilhasoft/carriers/archive/master.zip",
    keywords=['carriers', 'ilhasoft', 'mobile', 'ilhasoft-carriers'],
    classifiers=CLASSIFIERS,
)
