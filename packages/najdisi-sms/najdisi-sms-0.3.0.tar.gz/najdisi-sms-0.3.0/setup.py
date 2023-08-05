from setuptools import setup

version = '0.3.0'

setup(name='najdisi-sms',
      version=version,
      description="Najdi.si sms command line sender",
      long_description="""""",
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Domen Kozar, Andraz Bronik',
      author_email='brodul@brodul.org',
      url='',
      license='BSD',
      py_modules=['najdisi_sms'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'requests==2.2.1',
          'beautifulsoup4==4.3.2',
      ],
      entry_points="""
      [console_scripts]
      najdisi-sms = najdisi_sms:main
      """,
      )
