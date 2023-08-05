from distutils.core import setup
setup(
  name = 'some-test-package',
  packages = ['mypackage'], # this must be the same as the name above
  version = '0.2',
  description = 'A random test lib',
  author = 'Johnny Gazelle',
  author_email = 'johnny@example.com',
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)
