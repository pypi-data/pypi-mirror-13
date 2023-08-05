from distutils.core import setup

setup(
  name = 'basketball_reference_web_scraper',
  packages = ['basketball_reference_web_scraper'], # this must be the same as the name above
  version = '2.0',
  description = 'An API for NBA data that is scraped from Basketball Reference',
  author = 'Jae Bradley',
  author_email = 'jae.b.bradley@gmail.com',
  url = 'https://github.com/jaebradley/basketball_reference_web_scraper', # use the URL to the github repo
  download_url = 'https://github.com/jaebradley/basketball_reference_web_scraper/tarball/0.7', # I'll explain this in a second
  keywords = ['basketball', 'data', 'nba'], # arbitrary keywords
  classifiers = [],
)