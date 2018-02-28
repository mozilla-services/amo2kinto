import codecs
import os
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    README = f.read()

with codecs.open(os.path.join(HERE, 'CHANGELOG.rst'), encoding='utf-8') as f:
    CHANGELOG = f.read()


REQUIREMENTS = [
    'jinja2',
    'kinto-http>=8',
    'lxml',
    'python-dateutil',
]


ENTRY_POINTS = {
    'console_scripts': [
        'kinto2xml = amo2kinto.exporter:main',
        'blockpages-generator = amo2kinto.generator:main',
    ]
}


setup(name='amo2kinto',
      version='3.2.1',
      description='Generate a blocklists.xml file from the Kinto collections.',
      long_description=README + "\n\n" + CHANGELOG,
      license='Apache License (2.0)',
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "License :: OSI Approved :: Apache Software License"
      ],
      keywords="web services",
      author='Mozilla Services',
      author_email='services-dev@mozilla.com',
      url='https://github.com/mozilla-services/amo2kinto',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIREMENTS,
      entry_points=ENTRY_POINTS)
