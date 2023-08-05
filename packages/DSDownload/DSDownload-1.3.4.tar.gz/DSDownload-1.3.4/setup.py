from distutils.core import setup
setup(
  name = 'DSDownload',
  packages = ['DSDownload'], 
  version = '1.3.4',
  description = 'DSDownload is a fully featured download library with focus on performance',
  author = 'Diego Siqueira',
  author_email = 'dieg0@live.com',
  url = 'https://github.com/DiSiqueira/DSDownload', 
  download_url = 'https://github.com/DiSiqueira/DSDownload/tarball/1.3', 
  keywords = ['download', 'thread', 'speed', 'resume', 'multi', 'simple'],
  classifiers = [],
  license='MIT',
  entry_points = {
          'console_scripts': [
              'dsdownload = DSDownload.DSDownload:main',                  
          ],              
      },
)