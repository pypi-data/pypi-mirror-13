# -*- coding: utf-8 -*-

from distutils.core import setup
from setuptools import find_packages

setup(name='somebod',
      version='0.1.1',
      author='Guillaume Thomas',
      author_email='guillaume.thomas642@gmail.com',
      license='LICENCE.txt',
      description='Somebod contrib',
      url='https://github.com/gtnx/somebod',
      install_requires=map(lambda line: line.strip("\n"),
                           open("requirements.txt", "r").readlines()),
      include_package_data=True,
      packages=find_packages(),
      )
