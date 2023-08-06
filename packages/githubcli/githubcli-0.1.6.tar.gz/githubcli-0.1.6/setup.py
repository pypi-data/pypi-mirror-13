from githubcli.__init__ import __version__
import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

setup(
    description='',
    author='Donne Martin',
    url='',
    download_url='',
    author_email='donne.martin@gmail.com',
    version=__version__,
    license='',
    install_requires=[
        'click>=5.1',
        'docopt>=0.6.2',
        'tabulate>=0.7.5',
        'colorama>=0.3.3',
        'Pillow>=3.0.0',
        'requests >= 2.0',
        'uritemplate.py >= 0.2.0',
    ],
    extras_require={
        'testing': [
            'mock>=1.0.1',
            'tox>=1.9.2'
        ],
    },
    entry_points={
        'console_scripts': 'gh = githubcli.githubcli:GitHubCli.cli'
    },
    packages=find_packages(),
    scripts=[],
    name='githubcli',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
