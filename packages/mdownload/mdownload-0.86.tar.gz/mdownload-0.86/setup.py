from distutils.core import setup
setup(
  name = 'mdownload',
  packages = ['mdownload'], 
  version = '0.86',
  description = 'It is a small library to multi-threaded downloads.',
  author = 'Diego Siqueira',
  author_email = 'dieg0@live.com',
  url = 'https://github.com/DiSiqueira/mdownload', 
  download_url = 'https://github.com/DiSiqueira/mdownload/tarball/0.85', 
  keywords = ['download', 'thread', 'speed', 'resume', 'multi', 'simple'],
  classifiers = [],
  license='MIT',
  entry_points = {
          'console_scripts': [
              'mdownload = mdownload.mdownload:main',                  
          ],              
      },
)