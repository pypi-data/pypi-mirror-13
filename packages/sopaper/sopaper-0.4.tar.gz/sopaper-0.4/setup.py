#from distutils.core import setup
from setuptools import setup
kwargs = dict(
  name = 'sopaper',
  version = '0.4',
  description = 'Automatically search and download paper',
  author = 'Yuxin Wu',
  author_email = 'ppwwyyxxc@gmail.com',
  url = 'https://github.com/ppwwyyxx/sopaper',
  download_url = 'https://github.com/ppwwyyxx/sopaper/tarball/0.3',
  keywords = ['Utility'],
  packages = ['sopaper', 'sopaper.fetcher',
              'sopaper.lib', 'sopaper.searcher'],
  entry_points={
      'console_scripts': ['sopaper = sopaper.__main__:main']
  },
  include_package_data=True,
  install_requires=['termcolor', 'requests', 'beautifulsoup4']
)
setup(**kwargs)
