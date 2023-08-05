"""A framework making it easy to use the SAFT-gamma Mie theory for molecular
dynamics with the HOOMD-blue GPU-accelerated MD code.

See:
https://bitbucket.org/asmunder/raasaft/
http://molecularsystemsengineering.org/saft.html
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file, render from md to rst
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
    print("Long description converted successfully")
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='raaSAFT',

    version='0.6.3',

    description='Easy coarse-grained simulations with the SAFT-gamma Mie force field',
    long_description=long_description,

    # The project's main homepage.
    url='https://bitbucket.org/asmunder/raasaft/',

    # Author details
    author='Åsmund Ervik',
    author_email='aaervik@gmail.com',

    license='MIT',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',

        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='molecular dynamics GPU SAFT Mie HOOMD',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'test*', 'replication', 'tutorials']),
    
    install_requires=['requests','future'],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={'console_scripts': ['raasaft_init = raasaft.dirinit:main']},
)
