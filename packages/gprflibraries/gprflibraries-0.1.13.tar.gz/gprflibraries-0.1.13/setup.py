from distutils.core import setup
setup(
  name = 'gprflibraries',
  packages = ['gprflibraries', 'gprflibraries.libraries', 'gprflibraries.resources'],
  include_package_data = True,
  package_data = {'': ['*.robot']},
  version = '0.1.13',
  keywords = [],
  classifiers = [],
)
