from distutils.core import setup
from version import ver

setup(
  name = 'gprflibraries',
  packages = ['gprflibraries', 'gprflibraries.libraries', 'gprflibraries.resources'],
  include_package_data = True,
  package_data = {'': ['*.robot']},
  version = ver,
  keywords = [],
  classifiers = [],
)
