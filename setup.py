import codecs
import os
import sys
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    README = f.read()

with codecs.open(os.path.join(HERE, 'CHANGELOG.rst'), encoding='utf-8') as f:
    CHANGELOG = f.read()


REQUIREMENTS = [
    'jsonschema',
    'kinto-client',
    'requests',
    'lxml',
    'six',
    'xmltodict',
]


if sys.version_info < (2, 7, 9):
    # Add OpenSSL dependencies to handle requests SSL warning.
    REQUIREMENTS.append([
        "pyopenssl",
        "ndg-httpsclient",
        "pyasn1"
    ])


ENTRY_POINTS = {
    'console_scripts': [
        'kinto2xml = amo2kinto.exporter:main',
        'json2kinto = amo2kinto.importer:main',
        'xml-verifier = amo2kinto.verifier:main',
    ]
}


setup(name='amo2kinto',
      version='1.1.0',
      description='Generate a blocklists.xml file from the Kinto collections.',
      long_description=README + "\n\n" + CHANGELOG,
      license='Apache License (2.0)',
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "License :: OSI Approved :: Apache Software License"
      ],
      keywords="web services",
      author='Mozilla Services',
      author_email='services-dev@mozilla.com',
      url='https://github.com/mozilla-services/amo2kinto',
      packages=find_packages(),
      zip_safe=False,
      install_requires=REQUIREMENTS,
      entry_points=ENTRY_POINTS)
