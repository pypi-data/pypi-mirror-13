from distutils.core import setup
setup(
  name = 'mysample',
  packages = ['mysample'], # this must be the same as the name above
  version = '0.1',
  description = 'A random test parser',
  author = 'HPE',
  author_email = 'shiva-charan.m-s@hpe.com',
  url = 'https://gerrit.opnfv.org/gerrit/parser', # use the URL to the github repo
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)
