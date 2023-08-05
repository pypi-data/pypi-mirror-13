from setuptools import setup

def readme():
  with open('README.rst') as f:
    return f.read()

setup(
  name='mdx',
  version='0.1',
  description='A simple package for generating mdx scripts',
  long_description=readme(),
  keywords='MDX builder bi business intelligence',
  url='http://github.com/tiagotaveiragomes/mdx',
  author='Tiago Taveira-Gomes',
  author_email='tiago.taveira@me.com',
  license='MIT',
  packages=['mdx'],
  zip_safe=False,
  include_package_data=True,
  install_requires=['moretools'],
  test_suite='nose.collector',
  tests_require=['nose'],
)