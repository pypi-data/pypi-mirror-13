from distutils.core import setup
from setuptools import Extension,find_packages


setup(
  name = 'faerie',
  version = '1.0.1',
  description = '''This is an implementation of `faerie entity extraction <http://dbgroup.cs.tsinghua.edu.cn/ligl/papers/sigmod2011-faerie.pdf>`_
, a dictionary-baesd entity extraction.''',
  author = 'Zheng Tang',
  author_email = 'zhengtan@isi.edu',
  url = 'https://github.com/usc-isi-i2/dig-dictionary-extraction/', # use the URL to the github repo
  packages = find_packages(),
  keywords = ['heap', 'entity_extraction'], # arbitrary keywords
  ext_modules=[Extension(
        'singleheap',
        ['singleheap.c'])],
  install_requires=['nltk']
)