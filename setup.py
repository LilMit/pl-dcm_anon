from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.rst')) as f:
    readme = f.read()

setup(
    name             = 'dcm_anon',
    version          = '0.1',
    description      = 'An app to anonymize dicom tags using the pfdicom_tagSub module',
    long_description = readme,
    author           = 'FNNDSC',
    author_email     = 'dev@babyMRI.org',
    url              = 'https://github.com/LilMit/pl-dcm_anon',
    packages         = ['dcm_anon'],
    install_requires = ['chrisapp'],
    test_suite       = 'nose.collector',
    tests_require    = ['nose'],
    license          = 'MIT',
    zip_safe         = False,
    python_requires  = '>=3.6',
    entry_points     = {
        'console_scripts': [
            'dcm_anon = dcm_anon.__main__:main'
            ]
        }
)
