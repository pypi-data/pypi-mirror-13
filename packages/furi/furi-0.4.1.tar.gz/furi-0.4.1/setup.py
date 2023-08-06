import os
from setuptools import setup

NAME    = "furi"
VERSION = "0.4.1"
AUTHOR  = "amancevice"
EMAIL   = "smallweirdnum@gmail.com"
DESC    = "fURI File access through URIs."

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities" ]
TEST_REQUIRES  = ["nose", "mock", "moto"]
S3_REQUIRES    = ["boto3>=1.2.3"]
SFTP_REQUIRES  = ["pysftp>=0.2.8"]
EXTRAS_REQUIRE = {
    'test' : TEST_REQUIRES,
    's3'   : S3_REQUIRES,
    'sftp' : SFTP_REQUIRES,
    'all'  : S3_REQUIRES + SFTP_REQUIRES
}

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name                 = NAME,
    version              = VERSION,
    author               = AUTHOR,
    author_email         = EMAIL,
    packages             = [ NAME ],
    package_data         = { "%s" % NAME : ['README.md'] },
    include_package_data = True,
    url                  = 'http://www.smallweirdnumber.com',
    description          = DESC,
    long_description     = read('README.md'),
    classifiers          = CLASSIFIERS,
    install_requires     = EXTRAS_REQUIRE['all'],
    test_requires        = TEST_REQUIRES,
    extras_require       = EXTRAS_REQUIRE,
    test_suite           = "nose.collector" )
