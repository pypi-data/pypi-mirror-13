#! /usr/bin/env python
from __future__ import print_function

from setuptools import setup, find_packages

from cloudmesh_base.setup import *
from cloudmesh_base import __version__

check_pip()

requirements = ['wheel',
                'tox',
                'nose',
                'future',
                'docopt',
                'prettytable',
                'pyaml',
                'pytimeparse',
                'pyyaml',
                'simplejson',
                'gitchangelog']




banner("Installing cloudmesh_base {:}".format(__version__))

home = os.path.expanduser("~")


"""
    @classmethod
    def install_requirements(cls):
        for requirement in requirements:
            os.system("pip install {:}".format(requirement))
"""
#
# INSTALL
#


class InstallBase(install):
    """Install the package."""
    def run(self):
        banner("Requirements")
        #Make.install_requirements()
        banner("Install Cloudmesh Base")
        # os.system("pip install pip -U")
        install.run(self)
        pass

class InstallRequirements(install):
    """Install the requirements."""
    def run(self):
        #auto_create_requirements()
        #banner("Install Cloudmesh Base Requirements")
        #os.system("pip install -r requirements.txt")
        pass

class InstallAll(install):
    """Install requirements and the package."""
    def run(self):
        #banner("Install Cloudmesh Base Requirements")
        #os.system("pip install -r requirements.txt")
        #banner("Install Cloudmesh Base")
        #install.run(self)
        pass


setup(
    name='cloudmesh_base',
    version=__version__,
    description='A set of simple base functions and classes useful for cloudmesh and other programs',
    # description-file =
    #    README.rst
    author='The Cloudmesh Team',
    author_email='laszewski@gmail.com',
    url='http://github.org/cloudmesh/base',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Boot',
        'Topic :: System :: Systems Administration',
        'Framework :: Flask',
        'Environment :: OpenStack',
    ],
    entry_points={
        'console_scripts': [
            'cm-authors = cloudmesh_base.gitinfo:GitInfo.print_authors',
        ],
    },
    install_requires=requirements,
    packages=find_packages(),
    cmdclass={
        'install': InstallBase,
        'requirements': InstallRequirements,
        'all': InstallAll,
        'pypi': Make("pypi", repo='pypi'),
        'pypifinal': Make("pypi", repo='final'),
        'register': Make("pypi", repo='pypi'),
        'registerfinal': Make("pypi", repo='final'),
        'rmtag': Make('rmtag'),
        'tag': Make("tag"),
        'doc': Make("doc"),
        'view': Make("view"),
        'clean': Make("clean"),
        },
)
