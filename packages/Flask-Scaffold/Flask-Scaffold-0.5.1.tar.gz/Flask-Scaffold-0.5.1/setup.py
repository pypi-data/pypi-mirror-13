"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Flask-Scaffold',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.5.1',

    description="Scaffold Database Applications in MySQL or PostgreSQL with Flask",
    long_description=long_description,

    # The project's main homepage.
    url="https://github.com/Leo-G/Flask-Scaffold",

    # Author details
    author="Leo G",
    author_email="leo@techarena51.com",

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],

    # What does your project relate to?
    keywords='Flask Database Web',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages('app', 'scaffold'),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
    "alembic==0.8.3",
    "autopep8==1.1.1",
    "Flask==0.10.1",
    "Flask-Migrate==1.4.0",
    "Flask-RESTful==0.3.4",
    "Flask-Script==2.0.5",
    "Flask-SQLAlchemy==2.0",
    "inflect==0.2.5",
    "lazy-object-proxy==1.2.1",
    "Mako==1.0.3",
    "MarkupSafe==0.23",
    "marshmallow==2.3.0",
    "marshmallow-jsonapi==0.3.0",
    "pep8==1.6.2",
    "psycopg2==2.6",
    "PyMySQL==0.6.6",
    "python-dateutil==2.4.2",
    "PyYAML==3.11",
    "six==1.10.0",
    "SQLAlchemy==1.0.9",
    "uWSGI==2.0.11.2",
    "wrapt"
    ]

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]

)
