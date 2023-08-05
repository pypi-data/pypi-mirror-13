from distutils.core import setup

setup(
  name = 'ttw',
  packages = ['ttw'], # this must be the same as the name above
  version = '0.0.2',
  description = 'ttw - talking to whom? the python console util to track all your outcome connections In other words easily extendable network sniffer with some functionality to analyse requests',
  author = 'Misha Shelemetyev',
  author_email = 'mshelemetev@gmail.com',
  url = 'https://github.com/MShel/ttw', # use the URL to the github repo
  download_url = 'https://github.com/MShel/ttw/tarball/0.0.2',
  keywords = ['sniffer', 'tcp', 'udp','icmp','traffic-analyser'], # arbitrary keywords
  classifiers = [],
)
