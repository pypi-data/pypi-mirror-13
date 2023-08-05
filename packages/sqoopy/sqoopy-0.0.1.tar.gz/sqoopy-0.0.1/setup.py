from setuptools import setup, find_packages
import os

# hack for working with pandocs on windows
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    utf8 = codecs.lookup('utf-8')
    func = lambda name, enc=utf8: {True: enc}.get(name == 'mbcs')
    codecs.register(func)

# install readme
README = os.path.join(os.path.dirname(__file__), 'README.md')
README = open(README, 'r').read().strip()

REQUIREMENTS = os.path.join(os.path.dirname(__file__), 'requirements.txt')
REQUIREMENTS = open(REQUIREMENTS, 'r').read().splitlines()

VERSION = os.path.join(os.path.dirname(__file__), 'VERSION')
VERSION = open(VERSION, 'r').read().strip()

# setup
setup(
    name='sqoopy',
    version=VERSION,
    description='',
    long_description=README,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    author='Brian Abelson',
    author_email='brian.abelson@voxmedia.com',
    url='http://github.com/voxmedia/sqoopy',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    keywords=[ 'sqoop', 'mysql', 'import', 'hadoop'],
    tests_require=[],
    entry_points     = { 
        'console_scripts':[
            'sqoopy = sqoopy:run'
        ]
    },
)