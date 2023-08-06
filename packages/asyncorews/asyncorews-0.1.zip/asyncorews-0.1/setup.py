from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='asyncorews',
      version=version,
      description="Simple asyncore-based websocket server",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='websocket',
      maintainer='Petri Savolainen',
      maintainer_email='petri.savolainen@koodaamo.fi',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
