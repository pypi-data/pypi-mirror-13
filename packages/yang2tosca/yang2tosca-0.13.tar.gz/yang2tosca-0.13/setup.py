from distutils.core import setup
setup(
  name = 'yang2tosca',
  packages = ['yang2tosca'], # this must be the same as the name above
  package_data={'yang2tosca': ['*.xslt']},
  include_package_data=True,
  version = '0.13',
  description = 'A random test parser',
  author = 'HPE',
  author_email = 'shiva-charan.m-s@hpe.com',
  url = 'https://gerrit.opnfv.org/gerrit/parser', # use the URL to the github repo
  classifiers = [],
)
