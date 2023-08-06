import os
from setuptools import setup, find_packages


def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read().\
           decode('utf-8')

version = '1.0'

setup(name='collective.complexrecordsproxy',
      version=version,
      description="Providing a proxy class for plone.registry allowing IObject fields to be stored as separate records using the plone.registry collection support.",
      long_description='\n'.join([
          read('README.rst'),
          read('CHANGES.rst'),
          ]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        ],
      keywords='configuration registry',
      author='Sune Broendum Woeller',
      author_email='sune@woeller.dk',
      url='http://pypi.python.org/pypi/collective.complexrecordsproxy',
      license='GPLv2+',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.registry>=1.0',
          ''
      ],
      entry_points="""
      """,
      )
