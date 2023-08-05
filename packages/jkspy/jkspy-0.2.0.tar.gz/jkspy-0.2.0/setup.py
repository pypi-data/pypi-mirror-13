from distutils.core import setup
setup(
  name = 'jkspy',
  install_requires = ['pytz', 'PIL'],
  packages = ['jkspy',
              'jkspy.modules',
              'jkspy.apps'],
  package_data = {'jkspy':['scripts/*']},
  version = '0.2.0',
  description = 'Python utilities for doing computer stuff',
  author = 'Kumseok Jung',
  author_email = 'jungkumseok@gmail.com',
  license = 'LICENSE.txt',
  url = 'https://github.com/jungkumseok/jkspy',
  download_url = 'https://github.com/jungkumseok/jkspy/archive/0.2.0.tar.gz',
  keywords = ['testing', 'utility'], 
  classifiers = [],
)