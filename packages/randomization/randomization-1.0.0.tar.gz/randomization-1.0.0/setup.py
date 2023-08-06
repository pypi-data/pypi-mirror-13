""" Package Setup for randomization """

from setuptools import setup

import randomization

def readme():
    """ Helper function to open the readme file """
    with open('README.rst') as readme_file:
        return readme_file.read()

# Check this against the documentation for setuptools
setup(name='randomization',
      version='1.0.0',
      description='Functions to randomize subjects in clinical trials.',
      long_description=readme(),
      keywords='randomization random trial',
      url='http://github.com/louden/randomization',
      author='Christopher Louden',
      author_email='chris@loudenanalytics.com',
      license='MIT',
      packages=['randomization'],
      install_requires=[],
      test_suite='unittest')
