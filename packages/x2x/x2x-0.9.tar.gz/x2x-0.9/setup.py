from distutils.core import setup

setup(
        url                 = 'https://github.com/uxcn/x2x',
        name                = 'x2x',
        version             = '0.9',
        fullname            = 'x2x',
        description         = 'commands to convert radixes',
        long_description    = '''
x2x

Commands to convert radixes.

* x2b - convert to binary
* x2o - convert to octal
* x2d - convert to decimal
* x2h - convert to heaxadecimal
* x2x - convert any radix to any radix


Installing
----------

PyPI
::

    pip install x2x

From source
::

    python setup.py install

Versions
--------

0.9 (Jan, 2016)

* first release
''',
        classifiers         = ['Development Status :: 4 - Beta',
                               'Environment :: Console',
                               'Intended Audience :: Science/Research',
                               'Intended Audience :: Information Technology',
                               'Intended Audience :: System Administrators',
                               'Topic :: Scientific/Engineering',
                               'Topic :: Scientific/Engineering :: Mathematics',
                               'Topic :: Software Development',
                               'Topic :: System :: Shells',
                               'Natural Language :: English',
                               'Operating System :: OS Independent',
                               'Programming Language :: Python',
                               'Programming Language :: Python :: 2',
                               'Programming Language :: Python :: 2.7',
                               'Programming Language :: Python :: 3',
                               'Programming Language :: Python :: 3.3',
                               'Programming Language :: Python :: 3.4',
                               'License :: OSI Approved :: MIT License'],
        author              = 'Jason Schulz',
        maintainer          = 'Jason Schulz',
        author_email        = 'jason@schulz.name',
        maintainer_email    = 'jason@schulz.name',
        keywords            = 'radix base convert binary octal decimal hexadecimal',
        license             = 'MIT',
        scripts             = ['x2x', 'x2b', 'x2o', 'x2d', 'x2h'],
)

