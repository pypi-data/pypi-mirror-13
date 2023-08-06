from distutils.core import setup
setup(
  name = 'helloworldkent',
  packages = ['helloworldkent'], # this must be the same as the name above
  version = '0.1',
  description = 'My first pypi file',
  author = 'Kent Astudillo',
  author_email = 'kent@sym.com',
  url = 'https://github.com/killuabone/my-first-pypi', # use the URL to the github repo
  download_url = 'https://github.com/killuabone/my-first-pypi/tarball/0.1', # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)