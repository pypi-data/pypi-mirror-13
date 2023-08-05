from distutils.core import setup
setup(
  name = 'gprflibraries',
  packages = ['gprflibraries', 'gprflibraries.libraries', 'gprflibraries.resources'],
  include_package_data = True,
  package_data = {'': ['*.robot']},
  version = '1.0.0',
  keywords = [],
  classifiers = [],
)
