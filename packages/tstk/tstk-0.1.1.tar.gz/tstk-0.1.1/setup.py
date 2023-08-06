from setuptools import setup

version = '0.1.1'

setup(
    name = 'tstk',
    version = version,
    packages = ['tstk'],
    description = 'A bunch of tools for sequencing data analysis',
    author = 'Tomás Di Domenico',
    author_email = 'tdido@tdido.com.ar',
    url = 'https://github.com/tdido/tstk',
    keywords = ['sequence','toolkit','bioinformatics'],
    install_requires=[
        'pandas',
        'pysam',
        'biopython',
        'matplotlib',
        'numpy'
    ],
    license = 'MIT',
    classifiers=[  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ]
)
