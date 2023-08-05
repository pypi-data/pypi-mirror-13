from setuptools import setup
from pip.req import parse_requirements
import io
import os

__author__ = 'Cedric Zhuang'

__version__ = '0.1.7'


def here(filename=None):
    ret = os.path.abspath(os.path.dirname(__file__))
    if filename is not None:
        ret = os.path.join(ret, filename)
    return ret


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n\n')
    buf = []
    for filename in filenames:
        with io.open(here(filename), encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


def get_requires(filename):
    requirements = parse_requirements(filename, session=False)
    return [str(ir.req) for ir in requirements]


def get_long_description():
    filename = 'README.md'
    try:
        import pypandoc
        ret = pypandoc.convert(filename, 'rst')
    except ImportError:
        ret = read(filename)
    return ret


setup(
    name="int_date",
    version=__version__,
    author="Cedric Zhuang",
    author_email="cedric.zhuang@gmail.com",
    description="Utility for int date like 20150312.",
    license="BSD",
    keywords="date integer",
    url="http://github.com/jealous/int_date",
    packages=['int_date'],
    platforms=['any'],
    long_description=get_long_description(),
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=get_requires('requirements.txt'),
    tests_require=get_requires('test-requirements.txt')
)
