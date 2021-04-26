#
# dcm_anon ds ChRIS plugin app
#
# (c) 2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

import os
import re
import json

from chrisapp.base import ChrisApp

import pfdicom_tagSub
import pudb
import sys



Gstr_title = r"""



     _                                         
    | |                                        
  __| | ___ _ __ ___    __ _ _ __   ___  _ __  
 / _` |/ __| '_ ` _ \  / _` | '_ \ / _ \| '_ \ 
| (_| | (__| | | | | || (_| | | | | (_) | | | |
 \__,_|\___|_| |_| |_| \__,_|_| |_|\___/|_| |_|
                   ______                      
                  |______|                     




"""

Gstr_synopsis = """

(Edit this in-line help for app specifics. At a minimum, the 
flags below are supported -- in the case of DS apps, both
positional arguments <inputDir> and <outputDir>; for FS and TS apps
only <outputDir> -- and similarly for <in> <out> directories
where necessary.)

    NAME

       dcm_anon.py 

    SYNOPSIS

        python dcm_anon.py                                         \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            [-I|--inputDir <inputDir>]                                  \\
            [-i|--inputFile <inputFile>]                                \\
            [-e|--extension <DICOMextension>]                           \\
            [-O|--outputDir <outputDir>]                                \\
            [-F|--tagFile <JSONtagFile>]                                \\
            [-T|--tagStruct <JSONtagStructure>]                         \\
            [-o|--outputFileStem <outputFileStem>]                      \\
            [--outputLeafDir <outputLeafDirFormat>]                     \\
            [--threads <numThreads>]                                    \\
            [-x|--man]                                                  \\
            [-y|--synopsis]                                             \\
            [--followLinks]                                             \\


    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                             \
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
                fnndsc/pl-dcm_anon dcm_anon                        \
                /incoming /outgoing

    DESCRIPTION

        `dcm_anon.py` ...

    ARGS

        [-I|--inputDir <inputDir>]
        Input DICOM directory to examine. By default, the first file in this
        directory is examined for its tag information. There is an implicit
        assumption that each <inputDir> contains a single DICOM series.

        [-i|--inputFile <inputFile>]
        An optional <inputFile> specified relative to the <inputDir>. If
        specified, then do not perform a directory walk, but convert only
        this file.

        [-e|--extension <DICOMextension>]
        An optional extension to filter the DICOM files of interest from the
        <inputDir>.

        [-O|--outputDir <outputDir>]
        The output root directory that will contain a tree structure identical
        to the input directory, and each "leaf" node will contain the analysis
        results.

        [-F|--tagFile <JSONtagFile>]
        Parse the tags and their "subs" from a JSON formatted <JSONtagFile>.

        [-T|--tagStruct <JSONtagStructure>]
        Parse the tags and their "subs" from a JSON formatted <JSONtagStucture>
        passed directly in the command line.

        [-o|--outputFileStem <outputFileStem>]
        The output file stem to store data. This should *not* have a file
        extension, or rather, any "." in the name are considered part of
        the stem and are *not* considered extensions.

        [--outputLeafDir <outputLeafDirFormat>]
        If specified, will apply the <outputLeafDirFormat> to the output
        directories containing data. This is useful to blanket describe
        final output directories with some descriptive text, such as
        'anon' or 'preview'.

        This is a formatting spec, so

            --outputLeafDir 'preview-%s'

        where %s is the original leaf directory node, will prefix each
        final directory containing output with the text 'preview-' which
        can be useful in describing some features of the output set.

        [--threads <numThreads>]
        If specified, break the innermost analysis loop into <numThreads>
        threads.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.

        [--json]
        If specified, output a JSON dump of final return.

        [--followLinks]
        If specified, follow symbolic links.

        [-v|--verbosity <level>]
        Set the app verbosity level.

            0: No internal output;
            1: Run start / stop output notification;
            2: As with level '1' but with simpleProgress bar in 'pftree';
            3: As with level '2' but with list of input dirs/files in 'pftree';
            5: As with level '3' but with explicit file logging for
                    - read
                    - analyze
                    - write

"""


class dcm_anon(ChrisApp):
    """
    An app to anonymize dicom tags using the pfdicom_tagSub module. Updated version of pl-pfdicom_tagSub.
    """
    PACKAGE                 = __package__
    TITLE                   = 'A ChRIS plugin app for anonymizing dicom tags. Updated version of pl-pfdicom_tagSub.'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 1000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 200  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        self.add_argument("-i", "--inputFile",
                            help        = "input file",
                            dest        = 'inputFile',
                            type        = str,
                            optional    = True,
                            default     = '')
        self.add_argument("-e", "--extension",
                            help        = "DICOM file extension",
                            dest        = 'extension',
                            type        = str,
                            optional    = True,
                            default     = '')
        self.add_argument("-F", "--tagFile",
                            help        = "JSON formatted file containing tags to sub",
                            dest        = 'tagFile',
                            type        = str,
                            optional    = True,
                            default     = '')
        self.add_argument("-T", "--tagStruct",
                            help        = "JSON formatted tag sub struct",
                            dest        = 'tagStruct',
                            type        = str,
                            optional    = True,
                            default     = '')
        self.add_argument("-I", "--tagInfo",
                            help        = "Semicolon-delimited tag sub struct",
                            dest        = 'tagInfo',
                            type        = str,
                            optional    = True,
                            default     = '')
        self.add_argument("-o", "--outputFileStem",
                            help        = "output file",
                            default     = "",
                            type        = str,
                            optional    = True,
                            dest        = 'outputFileStem')
        self.add_argument("--printElapsedTime",
                            help        = "print program run time",
                            dest        = 'printElapsedTime',
                            action      = 'store_true',
                            type        = bool,
                            optional    = True,
                            default     = False)
        self.add_argument("--threads",
                            help        = "number of threads for innermost loop processing",
                            dest        = 'threads',
                            type        = str,
                            optional    = True,
                            default     = "0")
        self.add_argument("--outputLeafDir",
                            help        = "formatting spec for output leaf directory",
                            dest        = 'outputLeafDir',
                            type        = str,
                            optional    = True,
                            default     = "")
        self.add_argument("-y", "--synopsis",
                            help        = "short synopsis",
                            dest        = 'synopsis',
                            action      = 'store_true',
                            type        = bool,
                            optional    = True,
                            default     = False)
        self.add_argument("--jsonReturn",
                            help        = "output final return in json",
                            dest        = 'jsonReturn',
                            action      = 'store_true',
                            type        = bool,
                            optional    = True,
                            default     = False)
        self.add_argument("--followLinks",
                            help        = "follow symbolic links",
                            dest        = 'followLinks',
                            action      = 'store_true',
                            type        = bool,
                            optional    = True,
                            default     = False)

    @staticmethod
    def tag_info_to_struct(tagInfo):
        fields = re.findall(r'(?:^|;\s*)"(.*?)"\s*:\s*"(.*?)"', tagInfo.strip())
        return json.dumps(dict(fields))

    def get_tag_struct(self):
        if self.options.tagStruct and self.options.tagInfo:
            msg = " Must give either tagStruct or tagInfo, not both."
            raise ValueError(msg)
        if self.options.tagInfo:
            return self.tag_info_to_struct(self.options.tagInfo)
        if !(self.options.tagInfo or self.options.tagstruct):
            tagInfo = '"PatientName":"anonymized";"PatientID":"%_md5|7_PatientID";"AccessionNumber":"%_md5|10_AccessionNumber";"PatientBirthDate":"%_strmsk|******01_PatientBirthDate"'
            return self.tag_info_to_struct(tagInfo)
        return self.options.tagStruct

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())

        pf_dicom_tagSub = pfdicom_tagSub.pfdicom_tagSub(
                        inputDir            = options.inputdir,
                        inputFile           = options.inputFile,
                        extension           = options.extension,
                        outputDir           = options.outputdir,
                        outputFileStem      = options.outputFileStem,
                        outputLeafDir       = options.outputLeafDir,
                        tagFile             = options.tagFile,
                        tagStruct           = self.get_tag_struct(),
                        threads             = options.threads,
                        verbosity           = options.verbosity,
                        followLinks         = options.followLinks,
                        json                = options.jsonReturn
                    )

        d_pfdicom_tagSub = pf_dicom_tagSub.run(timerStart = True)

        if options.printElapsedTime: 
            pf_dicom_tagSub.dp.qprint(
                                "Elapsed time = %f seconds" % 
                                d_pfdicom_tagSub['runTime']
                            )


    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)

