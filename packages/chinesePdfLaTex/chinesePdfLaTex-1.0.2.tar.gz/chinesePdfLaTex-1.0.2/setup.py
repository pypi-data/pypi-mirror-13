# coding=utf-8
'''
Created on Dec 30, 2015

@author: yangjie
'''
from setuptools import setup, find_packages
setup(
    name='chinesePdfLaTex',
    version='1.0.2',
    keywords=('chinese', 'pdflatex', 'index', 'bookmark'),
    description='chinese index and book mard with pdflatex tool',
    license='Free',
    author='yangjie',
    author_email='chnyangjie@163.com',
    url='http://wizard.ren',
    platforms='any',
    packages=find_packages('src'),
    package_dir={'': 'src'}

)
