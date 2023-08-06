import codecs
import os
import re

from setuptools import setup, find_packages

NAME = "flake8_dodgy"
PACKAGES = find_packages(where="src")
META_PATH = os.path.join("src", "flake8_dodgy", "__init__.py")
KEYWORDS = ["flake8", "dodgy"]
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Environment :: Console',
    'Topic :: Software Development :: Quality Assurance'
]
INSTALL_REQUIRES = [
    'flake8 >= 2.5.2, < 3.0.0',
    'dodgy >= 0.1.9, < 1.0.0',
    'setuptools'
]
TEST_REQUIRES = []

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()

META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("uri"),
        version=find_meta("version"),
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer=find_meta("author"),
        maintainer_email=find_meta("email"),
        keywords=KEYWORDS,
        long_description=(
            read("README.rst") + "\n\n" +
            read("AUTHORS.rst") + "\n\n" +
            read("CHANGELOG.rst")
        ),
        packages=PACKAGES,
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        tests_require=TEST_REQUIRES,
        entry_points={
            'flake8.extension': [
                'flake8_dodgy = '
                'flake8_dodgy.flake8_dodgy:'
                'dodgy_checker'
            ],
        },
        test_suite="nose.collector",

    )
