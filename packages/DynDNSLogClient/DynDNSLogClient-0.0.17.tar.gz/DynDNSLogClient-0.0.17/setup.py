from setuptools import setup, find_packages
setup(
  name = 'DynDNSLogClient',
  version = '0.0.17',
  packages = find_packages(),
  description = 'Dyn client for receiving DNS query log data from the cloud',
  author = 'Richard Bross',
  author_email = 'rbross1956@gmail.com',
  url = 'https://github.com/rabinnh/Dyn', 
  download_url = 'https://github.com/rabinnh/Dyn/tarball/0.0.17', 
  keywords = ['DNS', 'Dyn', 'Logs'], 
  install_requires=[
    'python-daemon>=1.6',
    'iron-mq>=0.8',
    'python-snappy>=0.5',
  ],
  classifiers = [],
)
