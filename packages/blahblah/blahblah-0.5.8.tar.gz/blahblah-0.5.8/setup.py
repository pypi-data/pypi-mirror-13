from setuptools import setup, find_packages


setup(
  name='blahblah',
  version='0.5.8',
  description='Fake data generator for district42 schema',
  url='https://github.com/nikitanovosibirsk/blahblah',
  author='Nikita Tsvetkov',
  author_email='nikitanovosibirsk@yandex.com',
  license='MIT',
  packages=find_packages(),
  install_requires=[
    'district42==0.5.5',
    'exrex==0.9.4'
  ]
)
