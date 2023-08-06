try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys
sys.path.insert(0, '.')
import version


setup(name='ipython-helpers',
      version=version.getVersion(),
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/cfobel/ipython-helpers',
      license='LGPL-3.0',
      install_requires=['IPython>=2.0', 'path_helpers>=0.2'],
      packages=['ipython_helpers'])
