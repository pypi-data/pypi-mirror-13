import os
import re

from setuptools import setup, find_packages

# Do not try to import the package to get its version.
_version_file = open(os.path.join(os.path.dirname(__file__), 'dokang_pdf', 'version.py'))
VERSION = re.compile(r"^VERSION = '(.*?)'", re.S).match(_version_file.read()).group(1)


def read(filename):
    with open(filename) as fp:
        return fp.read()

setup(
    name='dokang_pdf',
    version=VERSION,
    description="PDF harvester for Dokang",
    long_description='%s\n\n%s' % (read('README.rst'), read('CHANGES.txt')),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    author="Polyconseil",
    author_email="opensource+dokang@polyconseil.fr",
    url='',
    keywords='full-text search engine',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'dokang>=0.7.0',
    ],
    extras_require={
        ":python_version == '2.7'": [
            'pdfminer==20140328',
        ],
        ":python_version != '2.7'": [
            'pdfminer3k==1.3.0',
        ],
    },
    tests_require=[l for l in read('requirements_dev.txt').splitlines() if not l.startswith(('-', '#'))],
    test_suite='tests',
)
