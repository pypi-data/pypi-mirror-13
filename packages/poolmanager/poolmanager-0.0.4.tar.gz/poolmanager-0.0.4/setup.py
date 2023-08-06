from setuptools import setup, find_packages



setup(name='poolmanager',
      version='0.0.4',
      description='Simple pool manager',
      classifiers=[],
      keywords='',
      author='Loic Gasser',
      author_email='loicgasser4@gmail.com',
      license='MIT',
      url='https://github.com/loicgasser/poolmanager',
      packages=find_packages(exclude=['tests']),
      package_dir={'poolmanager': 'poolmanager'},
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      install_requires=[],
      )
      

