from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name='type-goes-first',
      version='0.0.1',
      description=u"Ensures that a FeatureCollection is declared early",
      long_description=long_description,
      classifiers=[],
      keywords='geojson, supermercado',
      author=u"Jacques Tardie",
      author_email='jacques@mapbox.com',
      url='https://github.com/jacquestardie/tgf',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click'
      ],
      entry_points="""
      [console_scripts]
      tgf=tgf.scripts.cli:cli
      """
      )
