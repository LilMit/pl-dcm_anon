pl-dcm_anon
================================

.. image:: https://img.shields.io/docker/v/parrmi/pl-dcm_anon?sort=semver
    :target: https://hub.docker.com/r/parrmi/pl-dcm_anon

.. image:: https://img.shields.io/github/license/LilMit/pl-dcm_anon
    :target: https://github.com/LilMit/pl-dcm_anon/blob/master/LICENSE

.. image:: https://github.com/LilMit/pl-dcm_anon/workflows/ci/badge.svg
    :target: https://github.com/LilMit/pl-dcm_anon/actions


.. contents:: Table of Contents


Abstract
--------

An app to anonymize dicom tags using the pfdicom_tagSub module.


Description
-----------

``dcm_anon`` is a ChRIS-based application that serves as a wrapper around the pfdicom_tagSub module. This app performs a recursive walk down an input tree, and for each DICOM file (as filtered with a -e .dcm), will perform an edit or substitution on a pattern of user specified DICOM tags. Resultant edited files are saved in the corresponding location in the output tree. This page is not the canonical reference for pfdicom_tagSub on which this plugin is based. Please see https://github.com/FNNDSC/pfdicom_tagSub for detail about the actual tag substitution process and the pattern of command line flags.

Note that the only difference between this plugin and the reference pfdicom_tagSub is that the reference has explicit flags for inputDir and outputDir while this plugin uses positional arguments for the same.

This plugin is meant to replace an older plugin, pl-pfdicom_tagSub. Version 1.0.0 is essentially pl-pfdicom_tagSub ported to the new cookiecutter template, but additional features will be added in future versions.


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
        parrmi/pl-dcm_anon dcm_anon                        \
                --tagStruct '
        {
            "PatientName":       "anonymized",
            "PatientID":         "%_md5|7_PatientID",
            "AccessionNumber":   "%_md5|10_AccessionNumber",
            "PatientBirthDate":  "%_strmsk|******01_PatientBirthDate"
        }
        ' --threads 0 -v 2 -e .dcm                                  \
        /incoming /outgoing

Assuming that $(pwd)/in contains a tree of DICOM files, then the above will generate, for each leaf directory node in $(pwd)/in that contains files satisfying the search constraint of ending in .dcm, new DICOM files with the above tag subsitutions: The PatientName is set to anonymized, the PatientID is replaced with the first seven chars of an md5 hash of the original PatientID -- similarly for the AssessionNumber. Finally the PatientBirthDate is masked so that the birthday is set to the first of the month.

Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-dcm_anon .

Run unit tests:

.. code:: bash

    docker run --rm local/pl-dcm_anon nosetests

Debug
-----

Invariably, some debugging will be required. In order to debug efficiently, map the following into their respective locations in the container:

..code:: bash
    docker run -it --rm -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
            -v $(pwd)/dcm_anon/dcm_anon.py:/usr/src/dcm_anon/dcm_anon.py  \
            -v $(pwd)/dcm_anon/pfdicom_tagSub.py:/usr/local/lib/python3.5/dist-packages/pfdicom_tagSub/pfdicom_tagSub.py \
            parrmi/pl-dcm_anon dcm_anon                          \
            --tagStruct '
            {
                "PatientName":       "anonymized",
                "PatientID":         "%_md5|7_PatientID",
                "AccessionNumber":   "%_md5|10_AccessionNumber",
                "PatientBirthDate":  "%_strmsk|******01_PatientBirthDate"
            }
            ' --threads 0 -v 2 -e .dcm                                      \
            /incoming /outgoing

This assumes that the source code the underlying pfdicom_tagSub.py module is accessible as shown.

Make sure that the host $(pwd)/out directory is world writable!

Examples
--------

Put some examples here!


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
