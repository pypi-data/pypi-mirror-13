from setuptools import setup, find_packages
setup(name='html_table_parser',
      packages=find_packages(),
      version='0.1.0',
      description='Transform html tables from soup objects to usable data structures (eg 2D arrays)',
      author='Oswald Jones',
      author_email='wakeupoj@gmail.com',
      url='https://github.com/ojones/html_table_parser',
      download_url='https://github.com/ojones/html_table_parser/tarball/0.1',
      include_package_data=True,
      license='MIT',
      zip_safe=False,
      test_suite='html_table_parser.tests',
      tests_require=['pytest'],
      install_requires=[
            'beautifulsoup4==4.4.1',
          ],
      extras_require={
          'testing': ['pytest'],
      }
      )