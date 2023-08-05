import sys

from paver.easy import task, needs, path, sh, cmdopts, options
from paver.setuputils import setup, install_distutils_tasks
from distutils.extension import Extension
from distutils.dep_util import newer

sys.path.insert(0, path('.').abspath())
import version

setup(name='microdrop-device-converter',
      version=version.getVersion(),
      description='Convert microdrop devices from v0.3.0 to SVG format.',
      keywords='',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/wheeler-microfluidics/microdrop-device-converter',
      license='LGPLv2.1',
      packages=['microdrop_device_converter'],
      install_requires=['microdrop-utility>=0.4', 'numpy', 'pandas',
                        'path-helpers>=0.2', 'pyyaml',
                        'svg_model>=0.5.post14'],
      # Install data listed in `MANIFEST.in`
      include_package_data=True)


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
