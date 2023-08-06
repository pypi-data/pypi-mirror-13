from setuptools import setup, find_packages
import sys, os

version = '0.1.2'

setup(name='pyprogress',
      version=version,
      description="Various command line progress bars, spinners and counters including threaded versions",
      long_description="""\
""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='progress spinner counter cli timer completion',
      author='Graham Moucka',
      author_email='mouckatron@gmail.com',
      url='https://github.com/mouckatron/pyprogress',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite='tests',
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts': [
              'countoutput = pyprogress.countoutput:main',
          ]
      },
      )
