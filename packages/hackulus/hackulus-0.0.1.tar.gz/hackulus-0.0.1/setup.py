from distutils.core import setup
VERSION = '0.0.1'
setup(
  name = 'hackulus',
  install_requires = ['flask'],
  packages = ['hackulus',],
  package_data = {'hackulus':['templates/*', 'scripts/*']},
  scripts = ['hackulus/scripts/hackulus',],
  version = VERSION,
  description = 'Personal development server for developers',
  author = 'Kumseok Jung',
  author_email = 'jungkumseok@gmail.com',
  license = 'LICENSE.txt',
  url = 'https://github.com/jungkumseok/hackulus',
  download_url = 'https://github.com/jungkumseok/hackulus/archive/'+VERSION+'.tar.gz',
  keywords = ['remote', 'shell', 'development'], 
  classifiers = [],
)