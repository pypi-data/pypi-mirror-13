from setuptools import setup

setup(name='tpt',
      version='0.12',
      description='The TPT load and export simple API',
      url='https://github.paypal.com/lihzhang/TPT-Load',
      author='Zhang Lihui',
      author_email='lihzhang@paypal.com',
      license='GNU',
      packages=['tpt'],
      package_data={'tpt': ['keywords.txt',]},
      include_package_data=True,
      install_requires=['pandas','jaydebeapi',],
      zip_safe=True)
