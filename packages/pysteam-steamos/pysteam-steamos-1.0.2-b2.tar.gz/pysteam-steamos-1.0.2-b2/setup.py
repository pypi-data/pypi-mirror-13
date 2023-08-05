from setuptools import setup

setup(
  name='pysteam-steamos',
  version='1.0.2-b2',
  description='Python library to work with Steam. For SteamOS. Corrects naming convention.',
  url='http://github.com/scottrice/pysteam',
  author='Michael DeGuzis, Scott Rice',
  author_email='',
  license='MIT',
  packages=['pysteam'],
  install_requires=[
  ],
  data_files=[
  ],
  dependency_links=[
  ],
  zip_safe=False,
  test_suite='nose.collector',
  tests_require=[
    'nose',
    'nose-parameterized',
    'mock',
  ],
)
