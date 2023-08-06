from setuptools import setup, find_packages
import sys, os

version = '0.4'

setup(name='crackqcli',
      packages=['crackqcli'],
      version=version,
      description="Hashcrack Crackq command-line client",
      long_description="""\
Hashcrack Crackq command-line client for submitting hashes to the Crackq. Supported hash formats: NTLM, MD5, SHA1, WPA/WPA2, PDF, descrypt, md5crypt, PHPass, MYSQL""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='hashcrack crackq password bruteforce hash NTLM MD5 SHA1 WPA WPA2 DESCRYPT MD5CRYPT PDF Wordpress Joomla phpBB3 MYSQL',
      author='Hashcrack',
      author_email='support@hashcrack.org',
      scripts=['crackqcli/crackqcli.py'],
      url='http://hashcrack.org',
      license='GPLv3',
      #package_data={'thirdparty': ['thirdparty/*.py']},
      include_package_data=True,
      #py_modules=['thirdparty'],
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
