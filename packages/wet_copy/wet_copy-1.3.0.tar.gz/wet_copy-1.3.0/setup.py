#!/usr/bin/env python3

import distutils.core

# Uploading to PyPI
# =================
# The first time only:
# $ python setup.py register -r pypi
#
# Every version bump:
# $ git tag <version>; git push
# $ python setup.py sdist upload -r pypi

from wet_copy import __version__, __author__, __email__

with open('README.rst') as file:
    readme = file.read()

distutils.core.setup(
        name='wet_copy',
        version=__version__,
        author=__author__,
        author_email=__email__,
        url='https://github.com/kalekundert/wet_copy',
        download_url='https://github.com/kalekundert/wet_copy/tarball/v'+__version__,
        license='GPLv3',
        description="Format and print wetlab protocols stored as text files in git repositories.",
        long_description=readme,
        keywords=[
            'print',
            'scientific',
            'protocols',
        ],
        py_modules=[
            'wet_copy',
        ],
        install_requires=[
            'docopt==0.6.2',
        ],
        entry_points = {
            'console_scripts': ['wet_copy=wet_copy:main'],
        },

)
