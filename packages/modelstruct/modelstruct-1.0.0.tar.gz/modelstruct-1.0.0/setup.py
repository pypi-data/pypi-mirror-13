from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='modelstruct',
    version='1.0.0',
    description='A module to expose the structure of SQLAlchemy models as a RESTful API',
    long_description=long_description,
    url='https://github.com/mathur/modelstruct',
    author='Rohan Mathur',
    author_email='rohan@rmathur.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='sqlalchemy models structure expose api',
    py_modules=["expose"],
    install_requires=['flask'],
)