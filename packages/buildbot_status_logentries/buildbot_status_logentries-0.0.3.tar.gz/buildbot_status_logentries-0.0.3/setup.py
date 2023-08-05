from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='buildbot_status_logentries',

    version='0.0.3',

    description='A Logentries status plugin for buildbot',
    long_description=long_description,

    url='http://www.logentries.com/',

    author='Jimmy Tang',
    author_email='jimmy_tang@rapid7.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='buildbot status logentries',

    #package_dir={'logentries': 'logentries'},
    #packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    packages=['logentries'],

    install_requires=['pyOpenSSL==0.15.1', 'Twisted==15.5.0', 'service_identity'],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    entry_points={
        'buildbot.status': [
            'LogentriesStatusPush = logentries:LogentriesStatusPush',
        ],
    },
)
