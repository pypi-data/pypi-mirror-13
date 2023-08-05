#!/usr/bin/env python
info="""
Allow use of system gi.repository (Gtk3) from a virtualenv
Should work on all platforms.

report bugs to https://github.com/stuaxo/vext
"""

version="0.5.6.16"
vext_version="vext>=%s" % version


from glob import glob
from subprocess import call

from setuptools import setup
from setuptools.command.install import install
from setuptools.command.install_lib import install_lib

import sys

vext_files = glob("*.vext")

def _post_install(self):
    cmd = ["vext", "-e", "-i" + (" -i".join(vext_files))]
    call(cmd)

class Install(install):
    def run(self):
        # from pip
        call(["pip", "install", vext_version])
        self.do_egg_install()
        self.execute(_post_install, [self], msg="Install vext files:")

class InstallLib(install_lib):
    def run(self):
        # from setup.py install_requires
        import os
        if 'VEXT_DEBUG' in os.environ:
            import IPython; IPython.embed()	
        call(["pip", "install", vext_version])
        install_lib.run(self)
        self.execute(_post_install, [self], msg="Install vext files:")

setup(
    name='vext.gi',
    zip_safe=False,

    cmdclass={
          'install': Install,
          'install_lib': InstallLib,
    },

    version=version,

    description='Use system python packages in a virtualenv',
    long_description=info,

    # The project's main homepage.
    url='https://github.com/stuaxo/vext',

    # Author details
    author='Stuart Axon',
    author_email='stuaxo2@yahoo.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='virtualenv gi vext gtk',

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    setup_requires=[vext_version, "setuptools>=0.18.8"],
    install_requires=[vext_version],
)
