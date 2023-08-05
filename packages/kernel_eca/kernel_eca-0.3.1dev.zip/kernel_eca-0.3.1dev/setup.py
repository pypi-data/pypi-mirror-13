import io
import os
import re

from distutils.core import setup


def read(path, encoding='utf-8'):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def version(path):
    """Obtain the packge version from a python file e.g. pkg/__init__.py
    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    version_file = read(path)
    version_match = re.search(r"""^__version__ = ['"]([^'"]*)['"]""",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


DESCRIPTION = "Python implementation of Kernel entropy component analysis"
LONG_DESCRIPTION = """
Kernel entropy component analysis
=================================
This is a scikit-learn compatible implementation of Kernel entropy component analysis.
For more information, see the github project page:
http://github.com/
"""
NAME = "kernel_eca"
AUTHOR = "Tobias Sterbak"
AUTHOR_EMAIL = "sterbak-it@outlook.com"
MAINTAINER = "Tobias Sterbak"
MAINTAINER_EMAIL = "sterbak-it@outlook.com"
URL = 'http://github.com/tsterbak/kernel_eca'
DOWNLOAD_URL = 'http://github.com/tsterbak/kernel_eca'
LICENSE = 'BSD'

VERSION = version('kernel_eca/__init__.py')

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      url=URL,
      download_url=DOWNLOAD_URL,
      license=LICENSE,
      packages=['kernel_eca',
            ],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'],
     )