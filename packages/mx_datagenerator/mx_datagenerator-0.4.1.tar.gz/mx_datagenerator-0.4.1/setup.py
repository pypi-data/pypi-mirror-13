# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

path = '%s/data_source/CP.json' % os.path.dirname(os.path.realpath(__file__))

setup(name='mx_datagenerator',
      version='0.4.1',
      description='Generador de datos específicamente creado para México',
      url='https://github.com/ericking97/MX_datagen.git',
      author='ericking97',
      author_email='ericking97@hotmail.com',
      license='MIT',
      packages=find_packages(),
      data_files=[(path, ['mx_datagen/data_source/CP.json'])],
      zip_safe=False)
