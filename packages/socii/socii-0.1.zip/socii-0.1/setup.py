
from setuptools import setup, find_packages
from codecs import open
from os import path


# here = path.abspath(path.dirname(__file__))

# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    # long_description = f.read()


setup(
    name='socii',
    version='0.1',
    description='A collection of snippets, types, functions, decorators',
    # long_description=long_description,
    url='https://github.com/socialery/socii',
    author='Socialery',
    license='Unlicense',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: Public Domain',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='dict attrdict',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
