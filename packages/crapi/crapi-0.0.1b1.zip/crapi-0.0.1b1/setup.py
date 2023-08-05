"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


from __future__ import print_function
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path, sep
from sys import platform

cwd = path.abspath(path.dirname(__file__))
md = path.join(cwd, 'crapi' + sep + 'README.md')
rst = 'crapi' + sep + 'README.rst'
req = 'crapi' + sep + 'requirements.txt'


# Get the long description from the README file
def md2rst():
    try:
        from pypandoc import convert
        print('Converting ' + md + ' to rst...')
        description = convert(md, 'rst')
        with open(rst, mode='w', encoding='utf-8') as f:
            print(description, file=f)
        return description
    except ImportError:
        print(
            "WARNING: Failed to convert Markdown to RST: " +
            "pandoc module is required!"
        )
        print("WARNING: Reading MD file...")
        with open(md, encoding='utf-8') as f:
            return f.read()


# Extract any Windows dependencies.
def win_pkg(line):
    if line in 'sys.platform':
        return line.split(';')[0]


with open(req) as f:
    requirements = filter(
        lambda s: not(
            '-e .' in s or '--extra-index-url' in s or platform in s
        ),
        f.read().splitlines()
    )

with open(req) as f:
    for line in f:
        if 'sys.platform' in line:
            requirements.append(line.split(';')[0])

setup(

    name='crapi',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1b01',

    description='CRAPI: Common Range API',
    long_description=md2rst(),

    # The project's main homepage.
    url='https://github.com/kounavi/crapi',

    # Author details
    author='Iraklis D., Kritonas P.',
    author_email='hdiakos@outlook.com, kriton_pilavidis@outlook.com',

    platforms=['windows', 'linux', 'server', 'workstation'],

    # Choose your license
    license='ASF 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Application Frameworks',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Microsoft',
        'Operating System :: POSIX :: Linux'
    ],

    # What does your project relate to?
    keywords='backend systems development wrapper pipes services daemons',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(
        exclude=[
            'docs', 'experimental', 'tests', 'crapi.messaging',
            'crapi.service.rt',
        ]
    ),
    include_package_data=True,

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=requirements

)
