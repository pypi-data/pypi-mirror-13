from distutils.core import setup
setup(
      name = 'easytrader',
      packages = ['easytrader'], # this must be the same as the name above
      version = '0.2.3',
      description = 'A utility for China Stock Trade',
      author = 'shidenggui',
      author_email = 'longlyshidenggui@gmail.com',
      url = 'https://github.com/shidenggui/easytrader', # use the URL to the github repo
      download_url = 'https://github.com/shidenggui/easytrader', # I'll explain this in a second
      keywords = ['China', 'stock', 'trade'], # arbitrary keywords
      classifiers = [],
      include_package_data=True,
      package_data={
          'config': ['ht.json', 'global.json', 'yjb.json'],
          'thirdlibrary': ['getcode_jdk1.5.jar', 'yjb_verify_code.jar']
      }
)
