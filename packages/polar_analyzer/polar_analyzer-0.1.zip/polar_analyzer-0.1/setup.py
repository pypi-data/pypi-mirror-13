from setuptools import setup

setup(name='polar_analyzer',
      version='0.1',
      description='maps positive and negative semantic values to words in a string or a text file.',
      url='http://github.com/sherifEwis/polar_analyzer/',
      author='Flying Circus',
      author_email='sherifewis@tickletock.com',
      license='MIT',
      packages=['semantic_analysis'],
      install_requires=[
          'statistics',
          'nltk',
          'matplotlib'
      ],
      zip_safe=False)
