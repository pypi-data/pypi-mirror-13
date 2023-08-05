"""
blowdrycss setup module.

Repository: https://github.com/nueverest/blowdrycss
Docs: http://blowdrycss.readthedocs.org/en/latest/index.html

setup.py references:
https://python-packaging-user-guide.readthedocs.org/en/latest/distributing/
http://peterdowns.com/posts/first-time-with-pypi.html
https://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
"""

# builtins
from setuptools import setup, find_packages     # Always prefer setuptools over distutils

__author__ = 'chad nelson'
__project__ = 'blow dry css'

# Get readme.rst from sphinx docs.
try:
    with open('docs/readme.rst', encoding='utf-8') as f:
        long_description = f.read()
except (IOError, ImportError):
    # default description
    long_description = u'Rapid styling tool used to auto-generate DRY CSS files from encoded class selectors.'

# Get current version number.
version = {}
with open('version.py') as file:
    exec(file.read(), version)

setup(
    name='blowdrycss',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version['__version__'],

    description=u'A rapid styling tool that compiles DRY CSS from encoded class selectors in your web project files',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/nueverest/blowdrycss',
    download_url='https://github.com/nueverest/blowdrycss/archive/master.zip',

    # Author details
    author=version['__author__'],
    author_email='nu.everest@gmail.com',

    # License
    license='MIT',

    # Classifier Reference: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',                  # 3 - Alpha, 4 - Beta, 5 - Production/Stable
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Operating System :: OS Independent',

        # Topics
        'Topic :: Artistic Software',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Utilities',

        # License
        'License :: OSI Approved :: MIT License',

        # Python version support.
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',  # Not compatible with cssutils, pypandoc, or sphinx
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords=('blowdry blowdrycss css compiler pre-compiler pre-processor generator dry cascading style sheets html ' +
             'encoded class selector parser'),

    # Packages
    packages=find_packages(),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['cssutils>=1.0.1', 'pypandoc>=1.1.2', 'future>=0.15.2'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install blowdrycss -e .[auto_save, docs, testing]
    extras_require={
        'auto_save': ['watchdog>=0.8.3', ],
        'docs': ['sphinx>=1.3.3', ],
        'testing': ['unittest', 'coverage>=4.0.2', ],
        'development': ['wheel>=0.26.0', ],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    # package_data={
    #     'blowdrycss': ['package_data.dat'],
    # },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'blowdry=blowdry:main',
    #     ],
    # },
)
