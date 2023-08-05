
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def find_packages(toplevel):
    return [directory.replace(os.path.sep, '.') for directory, subdirs, files in os.walk(toplevel) if '__init__.py' in files]

def get_version():
    return re.search(r"""__version__\s+=\s+(?P<quote>['"])(?P<version>.+?)(?P=quote)""", open('pythonz/version.py').read()).group('version')

def python_version_gte(version, pkgs):
    # The proper way to do this would be {':python_version>="3.5"': ['resumable-urlretrieve']}
    # but this is only implemented in setuptools 17.1, while MacOSX currently ships
    # setuptools 1.1.6. Upgrading setuptools is unfeasible there due to its System Integrity Protection
    major, minor = version
    return dict((':python_version=="{}.{}"'.format(major, x), pkgs)
                for x in range(minor, 10))

setup(name='pythonz-bd',
      version              = get_version(),
      description          = "Manage python installations in your system, berdario's shallow fork",
      long_description     = open('README.rst').read(),
      author               = 'saghul',
      author_email         = 'saghul@gmail.com',
      url                  = 'https://github.com/berdario/pythonz/tree/bd',
      license              = 'MIT',
      packages             = find_packages('pythonz'),
      extras_require       = python_version_gte((3,5), ['resumable-urlretrieve']),
      include_package_data = True,
      entry_points         = dict(console_scripts=['pythonz=pythonz:main',
                                                   'pythonz_install=pythonz.installer:install_pythonz']),
      zip_safe             = False,
      classifiers          = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
      ])
