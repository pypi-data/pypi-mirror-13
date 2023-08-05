# -*- coding: utf-8 -*-
import os

import sys

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


class Configuration(dict):
    """
    Structure, not yaml, just similar looking. It is just a description.

    dir: ./                                               # -- directory, that is used further for creation of relative subdirectories
                                                          #    current working directory by default
    logger:                                               #
        name: GOSLogger                                   #
        level: info                                       #  -- by default only info messages are shown
                                                          #
        format: %(asctime)s - %(name)s - %(levelname)s - %(message)s  #
                                                          #
        destination: sys.stdout                           # -- by default all logging messages are shown to the standard output
                                                          #
    io_silent_fail: false                                 # -- by default if any IO exception happens, program will terminate
                                                          ########################################################################
                                                          ########################################################################
    input:                                                #
        source:                                           #
            - path: file1_path                            # -- relative (to input->dir) path to file with genome data
              format: grimm                               # -- determines which reader is going ot process the source file
                                                          #    if not specified, automatically retrieved from file extension
              io_silent_fail: input->io_silent_fail       # -- whether to fail or not if exception has occurred during data reading
                                                          #    file specific. defaults to input io_silent_fail setting.
                                                          ########################################################################
            - path: file2_path                            #
            - path: file3_path                            #
        dir: .->dir + /input                              # -- a directory to search for source files in. / by default
                                                          ########################################################################
        io_silent_fail: .->io_silent_fail                 # -- input section wide setting whether to fail or not, when an exception
                                                          #    has occurred during the source file processing. Can be overwritten
                                                          #    by source file specific variable
                                                          ########################################################################
        logger: .->logger                                 # -- a logger specification to be utilized for the input section of the
                                                          #
        genomes:                                          # -- if specified, a check performed to make sure data about all
                                                          #    genomes if present. If not -- retrieved form source files
            - name: genome1_name                          # -- primary genome name.
                                                          #    must be unique among all observed genomes (specified and retrieved)
              aliases: [alias1, alias2, alias3]           # -- other genome names, to be identified by. must be unique per genome
                                                          ########################################################################
            - name: genome2_name                          #
            - name: genome3_name                          #
                                                          ########################################################################
    algorithm:                                            ########################################################################
        io_silent_fail: .-> io_silent_fail                # -- if any part of an algorithm performs io operation, this flag determines what
                                                          #    to do if an IO exception is thrown
        logger: .->logger                                 # --
        tasks:                                            # -- single processing entity specification
            paths: []                                     # -- unchangeable value is "./tasks". everything else specified will be appended

                                                          #    to "./tasks" directory. All *.py files are observed and all classes,
                                                          #    being subclasses of GOSTask will be processed and available for further usage
                                                          #################################################################################
        executable_containers:
            - name: stage
              reference: stages
              entry_type_name: task

            - name: round
              reference: rounds
              entry_type_name: stage

        stages:                                           # -- section describing next level layer of processing entities "stages"
            - name: stage1                                # -- unique name of a stages, that it can be referenced by later.
              self_loop: false                            # -- flag determining if a stage must be executed again, after its first execution
                                                          #    is finished.
              tasks:                                      # -- ordered list of tasks that stage includes in itself and will execute
                - task1                                   # -- name based reference to previously specified task
                - task2                                   # --
            - name: stage2                                # --
              logger: algorithm->logger                   # -- logger can be specified uniquely for each stage.
              self_loop: true                             # --
              tasks:                                      # --
                - task2                                   # --
            - name: stage3                                # --
              path: path_to_*.py_file                     # -- if "path" value is specified, the stage is loaded from specified .py file and
                                                          #    its structure is retrieved from the class based attributes
                                                          #################################################################################
        rounds:                                           # -- section describing next level layer of processing entities "rounds"
            - name: round1                                # -- unique name of a round, that can be referenced later
              self_loop: false                            # -- flag determining if a round must be executed again, after its first execution
                                                          #    is finished.
              logger: algorithm->logger                   # -- logger can be specified uniquely for each stage.
              stages:                                     # -- ordered list of stages that round includes in itself and will execute
                - stage1                                  # --
                - stage2                                  # --
            - name: round2                                # --
              path: path_to_*.py_file                     # -- if "path" value is specified, the round is loaded from specified .py file and
                                                          #    its structure is retrieved from the class based attributes
                                                          #################################################################################
        pipeline:                                         # -- top level procession entity
            logger: algorithm->logger                     # --
            self_loop: false                              # --
            rounds:                                       # -- ordered list of rounds that pipeline includes in itself and will execute
                - round1                                  # --
                - round2                                  # --
                - round1                                  # --
                                                          ########################################################################
    output:                                               ########################################################################
        dir: .->dir + output/                             # -- directory for all output files to be put. Used for further paths construction
        logger: .->logger                                 # -- logger specification tp be utilized in the output section
        io_silent_fail: .->io_silent_fail                 # -- output section wide setting to fail or not when an exception
                                                          #    has occurred during the source file processing. Can be overwritten
                                                          #    by output section specific variable
                                                          #################################################################################
        stats:                                            # -- output section which handles all the statistics output for current
                                                          #    scaffolder execution
            dir: output->dir + stats/                     # -- directory where statistics files will be located
            file: stats.txt                               # -- default file name for the overall statistics file
            logger: output->logger                        #
            io_silent_fail: output->io_silent_fail        #
                                                          #################################################################################
        assembly_points:                                  # -- output section which handles all the information output about assembly
                                                          #    points during scaffolder run
            dir: output->dir + assembly_points/           # -- directory where assembly points file will be located
            file: assembly_points.txt                     # -- default name for the overall statistic
            logger: output->logger                        #
            io_silent_fail: output->io_silent_fail        #
            genome_specific: true                         # -- when specified, besides the overall file with all assembly points for current
                                                          #    scaffolder run, also "per-genome" files are created, that duplicate genome
                                                          #    specific results
                                                          #################################################################################
            genome_specific_file_name_pattern: assembly_points_{genome_name}.txt    # pattern for genome_specific file name creation
                                                          #################################################################################
        genomes:                                          # -- output section where information about genomes fragments will be stored
            dir: output->dir + genomes/                   # -- directory where all genomes will ba located
            output_non_glued_fragments: false             # -- if specified, all input information about genomes will be outputted,
                                                          #    if set to false, only those fragments, that we involved in at least one
                                                          #    gluing will be present in the output
            logger: output->logger                        #
            io_silent_fail: output->io_silent_fail        #
    """

    DIR = "dir"
    LOGGER = "logger"
    IOSF = "io_silent_fail"
    INPUT = "input"
    ALGORITHM = "algorithm"
    OUTPUT = "output"
    SOURCE = "source"
    NAME = "name"
    LEVEL = "level"
    FORMAT = "format"
    DESTINATION = "destination"
    ASSEMBLY_POINTS = "assembly_points"
    GENOMES = "genome"
    STATS = "stats"
    TASKS = "tasks"
    STAGES = "stages"
    ROUNDS = "rounds"
    PIPELINE = "pipeline"
    PATH = "path"
    PATHS = "paths"
    FILE = "file"
    GENOME_SPECIFIC = "genome_specific"
    GENOME_SPECIFIC_FNP = "genome_specific_file_name_pattern"
    OUTPUT_NG_FRAGMENTS = "output_non_glued_fragments"
    SELF_LOOP = "self_loop"
    EXECUTABLE_CONTAINERS = "executable_containers"
    ENTRIES = "entries"
    REFERENCE = "reference"

    # predefined constants
    DEFAULT_IOSF = False
    DEFAULT_LOGGER_NAME = "GOSLogger"
    DEFAULT_LOGGER_LEVEL = "info"
    DEFAULT_LOGGER_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_INPUT_DIR = "input"
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_OUTPUT_STATS_DIR = "stats"
    DEFAULT_OUTPUT_STATS_FILE = "stats.txt"
    DEFAULT_OUTPUT_AP_FILE = "assembly_points.txt"
    DEFAULT_OUTPUT_AP_DIR = "assembly_points"
    DEFAULT_OUTPUT_AP_GENOME_SPECIFIC = True
    DEFAULT_OUTPUT_AP_GSFNP = "assembly_points_{genome_name}.txt"
    DEFAULT_OUTPUT_GENOMES_ONGF = False
    DEFAULT_OUTPUT_GENOMES_DIR = "genomes"
    DEFAULT_ALGORITHM_TASKS_PATH = "./tasks"
    DEFAULT_ALGORITHM_PIPELINE_SELF_LOOP = True
    DEFAULT_ALGORITHM_EC_SELF_LOOP = True
    DEFAULT_LOGGER_DESTINATION = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_top_level_fields()
        self._init_logger_top_level_section()
        self._init_input_section()
        self._init_algorithm_section()
        self._init_output_section()

    def _init_output_section(self):
        if self.OUTPUT not in self:
            self[self.OUTPUT] = {}
        if self.DIR not in self[self.OUTPUT]:
            self[self.OUTPUT][self.DIR] = None
        if self.LOGGER not in self[self.OUTPUT]:
            self[self.OUTPUT][self.LOGGER] = {}
        if self.IOSF not in self[self.OUTPUT]:
            self[self.OUTPUT][self.IOSF] = None
        if self.ASSEMBLY_POINTS not in self[self.OUTPUT]:
            self[self.OUTPUT][self.ASSEMBLY_POINTS] = {}
        if self.GENOMES not in self[self.OUTPUT]:
            self[self.OUTPUT][self.GENOMES] = {}
        if self.STATS not in self[self.OUTPUT]:
            self[self.OUTPUT][self.STATS] = {}

    def _init_algorithm_section(self):
        if self.ALGORITHM not in self:
            self[self.ALGORITHM] = {}
        if self.LOGGER not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.LOGGER] = {}
        if self.IOSF not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.IOSF] = None
        if self.EXECUTABLE_CONTAINERS not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.EXECUTABLE_CONTAINERS] = []
        if self.TASKS not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.TASKS] = {}
        if self.PIPELINE not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.PIPELINE] = {}

    def _init_input_section(self):
        if self.INPUT not in self:
            self[self.INPUT] = {}
        if self.LOGGER not in self[self.INPUT]:
            self[self.INPUT][self.LOGGER] = {}
        if self.DIR not in self[self.INPUT]:
            self[self.INPUT][self.DIR] = None
        if self.IOSF not in self[self.INPUT]:
            self[self.INPUT][self.IOSF] = None
        if self.SOURCE not in self[self.INPUT]:
            self[self.INPUT][self.SOURCE] = []

    def _init_logger_top_level_section(self):
        if self.LOGGER not in self:
            self[self.LOGGER] = {}
        if self.NAME not in self[self.LOGGER]:
            self[self.LOGGER][self.NAME] = None
        if self.LEVEL not in self[self.LOGGER]:
            self[self.LOGGER][self.LEVEL] = None
        if self.FORMAT not in self[self.LOGGER]:
            self[self.LOGGER][self.FORMAT] = None
        if self.DESTINATION not in self[self.LOGGER]:
            self[self.LOGGER][self.DESTINATION] = None

    def _init_top_level_fields(self):
        if self.DIR not in self:
            self[self.DIR] = None
        if self.IOSF not in self:
            self[self.IOSF] = None

    def update_with_default_values(self):
        """ Goes through all the configuration fields and predefines empty ones with default values

        Top level:
            `dir` field is predefined with current working directory value, in case of empty string or `None`
            `io_silent_fail` field if predefined with :attr:`Configuration.DEFAULT_IOSF` in case of None or empty string

        Logger section:
            `name` field is predefined with :attr:`Configuration.DEFAULT_LOGGER_NAME`. Field is set to str() of itself
            `level` field is predefined with :attr:`Configuration.DEFAULT_LOGGER_LEVEL`. Field is set to str() of itself
            `format` field is predefined with :attr:`Configuration.DEFAULT_LOGGER_LEVEL`. Field is set to str() of itself
            `destination` field if predefined with

        Input section:
            `dir` field is predefined with a relative path constructed with top level `dir` field and :attr:`Configuration.DEFAULT_INPUT_DIR`
            `source` field is predefined with an empty list
            `io_silent_fail` if predefined with a top level `io_silent_fail`
            `logger` subsection if predefined by a top level `logger` section it substitutes all the missing values in `input` `logger` subsection

        Algorithm section:
            `io_silent_fail` is predefined with a top level `io_silent_fail` value
            `logger` is predefined with top level `logger` configuration
            `tasks` section:
                `paths` is predefined by [:attr:`Configuration.DEFAULT_ALGORITHM_TASKS_PATH`]. If value is supplied,
                        :attr:`Configuration.DEFAULT_ALGORITHM_TASKS_PATH` is prepended  to the supplied list
            `stages` section: (is predefined with [])
                if any values are predefined, such fields as `io_silent_fail`, `logger` are propagated to stages entries
                `self_loop` value is predefined by :attr:`Configuration.DEFAULT_ALGORITHM_STAGES_SELF_LOOP`
            `rounds` section: (is predefined with [])
                if any values are predefined, such fields as `io_silent_fail`, `logger` are propagated to stages entries
                `self_loop` value is predefined by :attr:`Configuration.DEFAULT_ALGORITHM_ROUNDS_SELF_LOOP`
            `pipeline` section:
                `self_loop` if predefined by :attr:`Configuration.DEFAULT_ALGORITHM_PIPELINE_SELF_LOOP`
                `logger` if predefined with an algorithm->logger configuration. All non specified value are propagated respectively
                `rounds` is predefined with []

        Output section:
            `dir` field is predefined with :attr:`Configuration.DEFAULT_OUTPUT_DIR`
            `io_silent_fail` field is predefined with top level `io_silent_fail`
            `logger` subsection is predefined with a top level logger section, which substitutes all of missing values from top level `logger` section
            `stats` section
                `io_silent_fail` field is predefined with `output->io_silent_fail` value
                `dir` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_STATS_DIR`
                `file` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_STATS_FILE`
                `logger` is defaulted (all, or just missing parts) bu `output->logger` section

            `assembly_points` section
                `io_silent_fail` field is predefined with `output->io_silent_fail` value
                `dir` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_AP_DIR`
                `file` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_AP_FILE`
                `logger` is defaulted (all, or just missing parts) bu `output->logger` section
                `genome_specific` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_AP_GENOME_SPECIFIC`
                `genome_specific_file_name_pattern` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_AP_GSFNP`

            `genomes` section
                `io_silent_fail` field is predefined with `output->io_silent_fail` value
                `dir` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_GENOMES_DIR`
                `logger` is defaulted (all, or just missing parts) bu `output->logger` section
                `output_non_glued_fragments` is predefined with :attr:`Configuration.DEFAULT_OUTPUT_GENOMES_ONGF`

        :return: Nothing, performs inplace changes
        :rtype: `None`
        """
        if self[self.DIR] in ("", None):
            self[self.DIR] = os.getcwd()
        if self[self.IOSF] in ("", None):
            self[self.IOSF] = self.DEFAULT_IOSF

        # logger section
        if self[self.LOGGER][self.NAME] in ("", None):
            self[self.LOGGER][self.NAME] = self.DEFAULT_LOGGER_NAME
        self[self.LOGGER][self.NAME] = str(self[self.LOGGER][self.NAME])
        if self[self.LOGGER][self.LEVEL] in ("", None):
            self[self.LOGGER][self.LEVEL] = self.DEFAULT_LOGGER_LEVEL
        self[self.LOGGER][self.LEVEL] = str(self[self.LOGGER][self.LEVEL])
        if self[self.LOGGER][self.FORMAT] in ("", None):
            self[self.LOGGER][self.FORMAT] = self.DEFAULT_LOGGER_FORMAT
        self[self.LOGGER][self.FORMAT] = str(self[self.LOGGER][self.FORMAT])
        if self[self.LOGGER][self.DESTINATION] in ([], "", None):
            self[self.LOGGER][self.DESTINATION] = self.DEFAULT_LOGGER_DESTINATION

        # input section
        if self[self.INPUT][self.SOURCE] in ("", None):
            self[self.INPUT][self.SOURCE] = []
        if self[self.INPUT][self.DIR] in ("", None):
            self[self.INPUT][self.DIR] = self.DEFAULT_INPUT_DIR
        if self[self.INPUT][self.IOSF] in ("", None):
            self[self.INPUT][self.IOSF] = self[self.IOSF]
        self._update_logger_config(logger_to_update=self[self.INPUT][self.LOGGER],
                                   source_logger=self[self.LOGGER])

        # algorithm section
        if self.LOGGER not in self[self.ALGORITHM] or self[self.ALGORITHM][self.LOGGER] in ("", None):
            self[self.ALGORITHM][self.LOGGER] = {}
        self._update_logger_config(logger_to_update=self[self.ALGORITHM][self.LOGGER],
                                   source_logger=self[self.LOGGER])
        if self.IOSF not in self[self.ALGORITHM] or self[self.ALGORITHM][self.IOSF] in ("", None):
            self[self.ALGORITHM][self.IOSF] = self[self.IOSF]
        if self.TASKS not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.TASKS] = {}
        if self.EXECUTABLE_CONTAINERS not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.EXECUTABLE_CONTAINERS] = []

        if self.PATHS not in self[self.ALGORITHM][self.TASKS] or self[self.ALGORITHM][self.TASKS][self.PATHS] in ("", None):
            self[self.ALGORITHM][self.TASKS][self.PATHS] = []
        self[self.ALGORITHM][self.TASKS][self.PATHS] = [self.DEFAULT_ALGORITHM_TASKS_PATH] + self[self.ALGORITHM][self.TASKS][self.PATHS]

        for ecs in self[self.ALGORITHM][self.EXECUTABLE_CONTAINERS]:
            if self.REFERENCE not in ecs:
                ecs[self.REFERENCE] = ecs[self.NAME] + "s"
            if ecs[self.REFERENCE] not in self[self.ALGORITHM]:
                self[self.ALGORITHM][ecs[self.REFERENCE]] = []
            for executable_container in self[self.ALGORITHM][ecs[self.REFERENCE]]:
                if self.SELF_LOOP not in executable_container:
                    executable_container[self.SELF_LOOP] = self.DEFAULT_ALGORITHM_EC_SELF_LOOP
                if self.ENTRIES not in executable_container:
                    executable_container[self.ENTRIES] = []

        if self.PIPELINE not in self[self.ALGORITHM]:
            self[self.ALGORITHM][self.PIPELINE] = {}
        if self.LOGGER not in self[self.ALGORITHM][self.PIPELINE] or self[self.ALGORITHM][self.PIPELINE][self.LOGGER] in ("", None):
            self[self.ALGORITHM][self.PIPELINE][self.LOGGER] = {}
        self._update_logger_config(logger_to_update=self[self.ALGORITHM][self.PIPELINE][self.LOGGER],
                                   source_logger=self[self.ALGORITHM][self.LOGGER])
        if self.IOSF not in self[self.ALGORITHM][self.PIPELINE] or self[self.ALGORITHM][self.PIPELINE][self.IOSF] in ("", None):
            self[self.ALGORITHM][self.PIPELINE][self.IOSF] = self[self.ALGORITHM][self.IOSF]
        if self.ENTRIES not in self[self.ALGORITHM][self.PIPELINE] or self[self.ALGORITHM][self.PIPELINE][self.ENTRIES] in ("", None):
            self[self.ALGORITHM][self.PIPELINE][self.ENTRIES] = []
        if self.SELF_LOOP not in self[self.ALGORITHM][self.PIPELINE] or self[self.ALGORITHM][self.PIPELINE][self.SELF_LOOP] in ("", None):
            self[self.ALGORITHM][self.PIPELINE][self.SELF_LOOP] = self.DEFAULT_ALGORITHM_PIPELINE_SELF_LOOP

        # output section
        if self[self.OUTPUT][self.DIR] in ("", None):
            self[self.OUTPUT][self.DIR] = os.path.join(self[self.DIR], self.DEFAULT_OUTPUT_DIR)
        if self[self.OUTPUT][self.IOSF] in ("", None):
            self[self.OUTPUT][self.IOSF] = self[self.IOSF]
        self._update_logger_config(logger_to_update=self[self.OUTPUT][self.LOGGER],
                                   source_logger=self[self.LOGGER])

        # output -> stats section
        if self.DIR not in self[self.OUTPUT][self.STATS] or self[self.OUTPUT][self.STATS][self.DIR] in ("", None):
            self[self.OUTPUT][self.STATS][self.DIR] = self.DEFAULT_OUTPUT_STATS_DIR
        if self.IOSF not in self[self.OUTPUT][self.STATS] or self[self.OUTPUT][self.STATS][self.IOSF] in ("", None):
            self[self.OUTPUT][self.STATS][self.IOSF] = self[self.OUTPUT][self.IOSF]
        if self.FILE not in self[self.OUTPUT][self.STATS] or self[self.OUTPUT][self.STATS][self.FILE] in ("", None):
            self[self.OUTPUT][self.STATS][self.FILE] = self.DEFAULT_OUTPUT_STATS_FILE
        if self.LOGGER not in self[self.OUTPUT][self.STATS]:
            self[self.OUTPUT][self.STATS][self.LOGGER] = {}
        self._update_logger_config(logger_to_update=self[self.OUTPUT][self.STATS][self.LOGGER],
                                   source_logger=self[self.OUTPUT][self.LOGGER])

        # output -> assembly_points section
        if self.DIR not in self[self.OUTPUT][self.ASSEMBLY_POINTS] or self[self.OUTPUT][self.ASSEMBLY_POINTS][self.DIR] in ("", None):
            self[self.OUTPUT][self.ASSEMBLY_POINTS][self.DIR] = self.DEFAULT_OUTPUT_AP_DIR
        if self.IOSF not in self[self.OUTPUT][self.ASSEMBLY_POINTS] or self[self.OUTPUT][self.ASSEMBLY_POINTS][self.IOSF] in ("", None):
            self[self.OUTPUT][self.ASSEMBLY_POINTS][self.IOSF] = self[self.OUTPUT][self.IOSF]
        if self.FILE not in self[self.OUTPUT][self.ASSEMBLY_POINTS] or self[self.OUTPUT][self.ASSEMBLY_POINTS][self.FILE] in ("", None):
            self[self.OUTPUT][self.ASSEMBLY_POINTS][self.FILE] = self.DEFAULT_OUTPUT_AP_FILE
        if self.GENOME_SPECIFIC not in self[self.OUTPUT][self.ASSEMBLY_POINTS] or self[self.OUTPUT][self.ASSEMBLY_POINTS][
            self.GENOME_SPECIFIC]:
            self[self.OUTPUT][self.ASSEMBLY_POINTS][self.GENOME_SPECIFIC] = self.DEFAULT_OUTPUT_AP_GENOME_SPECIFIC
        if self.GENOME_SPECIFIC_FNP not in self[self.OUTPUT][self.ASSEMBLY_POINTS] or self[self.OUTPUT][self.ASSEMBLY_POINTS][
            self.GENOME_SPECIFIC_FNP]:
            self[self.OUTPUT][self.ASSEMBLY_POINTS][self.GENOME_SPECIFIC_FNP] = self.DEFAULT_OUTPUT_AP_GSFNP
        if self.LOGGER not in self[self.OUTPUT][self.ASSEMBLY_POINTS]:
            self[self.OUTPUT][self.ASSEMBLY_POINTS][self.LOGGER] = {}
        self._update_logger_config(logger_to_update=self[self.OUTPUT][self.ASSEMBLY_POINTS][self.LOGGER],
                                   source_logger=self[self.OUTPUT][self.LOGGER])

        # output -> genomes section
        if self.DIR not in self[self.OUTPUT][self.GENOMES] or self[self.OUTPUT][self.GENOMES][self.DIR] in ("", None):
            self[self.OUTPUT][self.GENOMES][self.DIR] = self.DEFAULT_OUTPUT_GENOMES_DIR
        if self.IOSF not in self[self.OUTPUT][self.GENOMES] or self[self.OUTPUT][self.GENOMES][self.IOSF] in ("", None):
            self[self.OUTPUT][self.GENOMES][self.IOSF] = self[self.OUTPUT][self.IOSF]
        if self.OUTPUT_NG_FRAGMENTS not in self[self.OUTPUT][self.GENOMES] or self[self.OUTPUT][self.GENOMES][self.OUTPUT_NG_FRAGMENTS] in (
        "", None):
            self[self.OUTPUT][self.GENOMES][self.OUTPUT_NG_FRAGMENTS] = self.DEFAULT_OUTPUT_GENOMES_ONGF
        if self.LOGGER not in self[self.OUTPUT][self.GENOMES]:
            self[self.OUTPUT][self.GENOMES][self.LOGGER] = {}
        self._update_logger_config(logger_to_update=self[self.OUTPUT][self.GENOMES][self.LOGGER],
                                   source_logger=self[self.OUTPUT][self.LOGGER])

    @staticmethod
    def _update_logger_config(logger_to_update, source_logger):
        if logger_to_update in ("", None):
            logger_to_update = {}
        for key, value in source_logger.items():
            if key not in logger_to_update or logger_to_update[key] in ("", None):
                logger_to_update[key] = source_logger[key]
