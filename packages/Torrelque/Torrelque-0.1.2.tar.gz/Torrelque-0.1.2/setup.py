try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup
  

setup(
  name             = 'Torrelque',
  version          = '0.1.2',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['torrelque'],
  test_suite       = 'torrelque.test',
  url              = 'https://bitbucket.org/saaj/torrelque',
  license          = 'LGPL-2.1+',
  description      = 'Asynchronous Tornado Redis-based reliable queue package',
  long_description = open('README.txt', 'rb').read().decode('utf-8'),
  install_requires = ['tornado >= 4.2, < 5', 'tornado-redis >= 2.4, < 3'],
  platforms        = ['Any'],
  keywords    = 'python tornado redis asynchronous reliable-queue work-queue',
  classifiers = [
    'Topic :: Database',
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Intended Audience :: Developers'
  ]
)

