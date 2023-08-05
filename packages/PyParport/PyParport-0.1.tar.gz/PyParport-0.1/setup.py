from setuptools import setup, Extension

pyparport = Extension("pyparport", sources=["pyparport/pyparport.c"])

setup(name="PyParport",
      version="0.1",
      description="This module provides the possibility to connect to the first parallel port from Python.",
      license='GPLv3',
      packages=['pyparport'],
      author='Christian Kokoska',
      author_email='christian@softcreate.de',
      ext_modules=[Extension("PyParport", ["pyparport/pyparport.c"])])
