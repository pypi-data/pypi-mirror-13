from distutils.core import setup
setup(
  name = 'DSDownload',
  packages = ['DSDownload'], 
  version = '1.2',
  description = 'It is a small library to multi-threaded downloads.',
  author = 'Diego Siqueira',
  author_email = 'dieg0@live.com',
  url = 'https://github.com/DiSiqueira/DSDownload', 
  download_url = 'https://github.com/DiSiqueira/DSDownload/tarball/1.2', 
  keywords = ['download', 'thread', 'speed', 'resume', 'multi', 'simple'],
  classifiers = [],
  license='MIT',
  entry_points = {
          'console_scripts': [
              'dsdownload = DSDownload.DSDownload:main',                  
          ],              
      },
)