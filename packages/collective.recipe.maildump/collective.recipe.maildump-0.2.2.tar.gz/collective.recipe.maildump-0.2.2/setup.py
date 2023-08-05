"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/collective/collective.recipe.maildump
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

def readfile(filename):
    with open(path.join(here, filename), encoding='utf-8') as f:
        return f.read()

long_description = readfile('README.rst')
long_description += readfile('CHANGES.txt')

setup(
    name = "collective.recipe.maildump",
    version = "0.2.2",
    description = "Buildout recipe to install maildump",
    long_description=long_description,
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Communications :: Email',
        'Topic :: Software Development',
        'Topic :: System :: Networking',
        'Topic :: Utilities'
    ],
    keywords='buildout recipe maildump',
    author='Noe Nieto',
    author_email='nnieto@noenieto.com',
    url='https://github.com/collective/collective.recipe.maildump',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout',
        # -*- Extra requirements: -*-
        'zc.recipe.egg'
    ],
    entry_points = {'zc.buildout': ['default = collective.recipe.maildump:Recipe']},
)
