from setuptools import setup, find_packages
import os
from distutils.core import setup

version = '1.0'

setup(name='plonetheme.office',
      version=version,
      description="Plone Theme Office",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      #keywords='',
      #author='Inigo Consulting',
      #author_email='team@inigo-tech.com',
      #url='http://github.com/inigoconsulting/',

      #milktea
      author = 'Afterfive Technologies',
      author_email = 'afterfive2015@gmail.com',
      url = 'https://github.com/afterfivetech/plonetheme.office', # URL to the github repo
      download_url = 'https://github.com/milktea/plonetheme.office/tarball/1.0', # Version tag
      keywords = ['testing', 'logging', 'example'], # arbitrary keywords

      license='gpl',
      packages=find_packages(),
      namespace_packages=['plonetheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity [grok, relations]',
          'plone.namedfile [blobs]',
          'collective.grok',
          'plone.app.referenceablebehavior',
          'collective.dexteritytextindexer',
          # 'plone.app.multilingual',
          # 'plone.multilingualbehavior',
          'z3c.jbot'
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'plone.app.testing',
           ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # The next two lines may be deleted after you no longer need
      # addcontent support from paster and before you distribute
      # your package.
      setup_requires=["PasteScript"],
      paster_plugins=["templer.localcommands"],

      )
