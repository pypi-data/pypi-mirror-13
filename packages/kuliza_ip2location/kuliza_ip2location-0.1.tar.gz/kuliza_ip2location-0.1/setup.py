from setuptools import setup
setup(
  name = 'kuliza_ip2location',
  packages = ['kuliza_ip2location'], # this must be the same as the name above
  version = '0.1',
  description = 'Wrapper for https://ipinfo.io',
  author = 'Sachin Prabhu',
  author_email = 'sachin.prabhu@kuliza.com',
  url='https://www.example.com/',
  classifiers = [],
  install_requires=["requests","py2-ipaddress"],
)

