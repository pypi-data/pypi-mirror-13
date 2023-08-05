from distutils.core import setup

pack_name="DNApy"

setup(
  name = pack_name,
  packages = [pack_name], # this must be the same as the name above
  version = '0.0.2.3',
  description = 'A bioinformatics library containing common file parsers and\
		  others!',
  author = 'Naman Jain',
  author_email = 'namanjn07@hotmail.com',
  url = 'https://github.com/Namanjn/namuskj', # use the URL to the github repo
  download_url = 'https://github.com/Namanjn/PyNamu/tarball/0.1', # I'll explain this in a second
  keywords = ['testing', 'bioinformatics', 'example'], # arbitrary keywords
  classifiers = [],
)
