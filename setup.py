import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'argparse',
    'pyramid',
    ]

setup(name='po.scaffolds',
      version='0.0',
      description='snippets for scaffolding',
      long_description=README + '\n\n' +  CHANGES,
      packages=find_packages(),
      namespace_packages=("po",),

      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [pyramid.scaffold]
      start_project = po.scaffolds:ProjectTemplate
      start_view = po.scaffolds:ViewTemplate
      start_model = po.scaffolds:ModelTemplate
      """,
      )

