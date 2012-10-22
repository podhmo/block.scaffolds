import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'argparse',
    'pyramid',
    ]

setup(name='block.scaffolds',
      version='0.0',
      description='snippets for scaffolding',
      long_description=README + '\n\n' +  CHANGES,
      packages=find_packages(),
      namespace_packages=("block",),

      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [pyramid.scaffold]
      start_project = block.scaffolds:ProjectTemplate
      start_view = block.scaffolds:ViewTemplate
      start_model = block.scaffolds:ModelTemplate
      """,
      )

