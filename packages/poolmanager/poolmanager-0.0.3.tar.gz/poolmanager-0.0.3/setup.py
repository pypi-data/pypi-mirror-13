import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
requires = open(os.path.join(here, 'requirements.txt')).read().split('\n')

setup(name='poolmanager',
      version='0.0.3',
      description='Simple pool manager',
      classifiers=[],
      keywords='',
      author='Loic Gasser',
      author_email='loicgasser4@gmail.com',
      license='MIT',
      url='https://github.com/loicgasser/poolmanager',
      packages=find_packages(exclude=['tests']),
      package_dir={'poolmanager': 'poolmanager'},
      package_data={'': ['*.txt', '*.md']},
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=requires
      )
      

