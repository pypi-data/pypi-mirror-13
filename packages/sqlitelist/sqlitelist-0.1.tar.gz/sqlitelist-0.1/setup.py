from setuptools import setup

from sqlitelist import VERSION

with open('README.rst') as f:
    readme = f.read()

setup(
    name='sqlitelist',
    version=VERSION,
    description='SQLite3 wrapper with a list-like interface',
    author='deliro',
    author_email='t4k.kitaetz@gmail.com',
    long_description=readme,
    license='Apache 2.0',
    packages=['sqlitelist'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ),
)