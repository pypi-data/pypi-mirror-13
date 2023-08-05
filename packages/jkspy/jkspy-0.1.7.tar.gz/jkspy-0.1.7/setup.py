from distutils.core import setup
setup(
  name = 'jkspy',
  packages = ['jkspy'],
  package_data = {'modules':['*'],
                  'apps':['*'],
                  'scripts':['*'],
                  },
  version = '0.1.7',
  description = 'Python utilities for doing computer stuff',
  author = 'Kumseok Jung',
  author_email = 'jungkumseok@gmail.com',
  license = 'LICENSE.txt',
  url = 'https://github.com/jungkumseok/jkspy',
  download_url = 'https://github.com/jungkumseok/jkspy/archive/0.1.7.tar.gz',
  keywords = ['testing', 'utility'], 
  classifiers = [],
)