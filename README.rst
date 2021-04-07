pl-dcm_anon
================================

.. image:: https://img.shields.io/docker/v/fnndsc/pl-dcm_anon?sort=semver
    :target: https://hub.docker.com/r/fnndsc/pl-dcm_anon

.. image:: https://img.shields.io/github/license/fnndsc/pl-dcm_anon
    :target: https://github.com/FNNDSC/pl-dcm_anon/blob/master/LICENSE

.. image:: https://github.com/FNNDSC/pl-dcm_anon/workflows/ci/badge.svg
    :target: https://github.com/FNNDSC/pl-dcm_anon/actions


.. contents:: Table of Contents


Abstract
--------

An app to anonymize dicom tags using the pfdicom_tagSub module


Description
-----------

``dcm_anon`` is a ChRIS-based application that...


Usage
-----

.. code::

    python dcm_anon.py
        [-h|--help]
        [--json] [--man] [--meta]
        [--savejson <DIR>]
        [-v|--verbosity <level>]
        [--version]
        <inputDir> <outputDir>


Arguments
~~~~~~~~~

.. code::

    [-h] [--help]
    If specified, show help message and exit.
    
    [--json]
    If specified, show json representation of app and exit.
    
    [--man]
    If specified, print (this) man page and exit.

    [--meta]
    If specified, print plugin meta data and exit.
    
    [--savejson <DIR>] 
    If specified, save json representation file to DIR and exit. 
    
    [-v <level>] [--verbosity <level>]
    Verbosity level for app. Not used currently.
    
    [--version]
    If specified, print version number and exit. 


Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-dcm_anon dcm_anon --man

Run
~~~

You need to specify input and output directories using the `-v` flag to `docker run`.


.. code:: bash

    docker run --rm -u $(id -u)                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
        fnndsc/pl-dcm_anon dcm_anon                        \
        /incoming /outgoing


Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-dcm_anon .

Run unit tests:

.. code:: bash

    docker run --rm local/pl-dcm_anon nosetests

Examples
--------

Put some examples here!


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
