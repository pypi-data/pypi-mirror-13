from setuptools import setup

setup(name='tpt',
      version='0.11',
      description='The TPT load and export simple tool',
      url='https://github.paypal.com/lihzhang/TPT-Load',
      author='Zhang Lihui',
      author_email='lihzhang@paypal.com',
      license='GNU',
      packages=['tpt'],
      package_data={'tpt': ['keywords.txt',]},
      include_package_data=True,
      install_requires=['pandas','jaydebeapi',],
      zip_safe=True)
