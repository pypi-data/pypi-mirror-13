# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='adminactionview',
    version='0.2',
    author='Michiel De Paepe',
    author_email='michiel.de.paepe@gmail.com',
    packages=find_packages(),
    url='https://github.com/MichielDePaepe/adminactionview',
    license='MIT licence, see LICENCE.txt',
    description='Add an intermediate page to the django admin when preforming actions. Here you can define extra parameters for your action',
    long_description=open('README.txt').read(),
    include_package_data=True,
    zip_safe=False,
)
