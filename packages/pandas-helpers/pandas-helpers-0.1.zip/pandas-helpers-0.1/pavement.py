from paver.easy import task, needs
from paver.setuputils import setup

import version


setup(name='pandas-helpers',
      version=version.getVersion(),
      description='Helper functions for working with pandas',
      author='Ryan Fobel',
      author_email='ryan@fobel.net',
      url='http://github.com/wheeler-microfluidics/pandas-helpers.git',
      license='GPLv2',
      install_requires=['pandas'],
      packages=['pandas_helpers'])


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
