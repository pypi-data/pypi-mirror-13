from setuptools import setup, find_packages

PACKAGE = "inipgdump"
NAME = "inipgdump"
DESCRIPTION = "Creates a dump of the PostgreSQL database. Stores the specified number of dumps, deletes the old dumps."
AUTHOR = "Timur Isanov"
AUTHOR_EMAIL = "tisanov@yahoo.com"
URL = "https://github.com/xtimon/inipgdump"
VERSION = __import__(PACKAGE).__version__

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open("README.rst").read(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="MIT",
    url=URL,
    packages=find_packages(),
    entry_points={
        'console_scripts':
            ['inipgdump = inipgdump.core:main']
        }
)
