import os
import unittest
from copy import deepcopy
from gos.configuration import Configuration


class ConfigurationTestCase(unittest.TestCase):
    def setUp(self):
        self.init_config = Configuration()

    def test_initialization_top_level(self):
        """ in simple initialization the top level section must be properly configured """
        config = Configuration()
        self.assertIn(config.DIR, config)
        self.assertIn(config.LOGGER, config)
        self.assertIn(config.IOSF, config)
        self.assertIn(config.INPUT, config)
        self.assertIn(config.ALGORITHM, config)
        self.assertIn(config.OUTPUT, config)

        self.assertIsInstance(config[config.LOGGER], dict)
        self.assertIsInstance(config[config.INPUT], dict)
        self.assertIsInstance(config[config.ALGORITHM], dict)
        self.assertIsInstance(config[config.OUTPUT], dict)

    def test_initialization_input_section(self):
        """ input section of the overall configuration must have some default init values and is predefined with them """
        config = Configuration()
        input_section = config[config.INPUT]
        self.assertIn(config.DIR, input_section)
        self.assertIn(config.LOGGER, input_section)
        self.assertIn(config.IOSF, input_section)
        self.assertIn(config.SOURCE, input_section)

        self.assertIsInstance(input_section[config.SOURCE], list)
        self.assertIsInstance(input_section[config.LOGGER], dict)

    def test_initialization_logger_section(self):
        """ logger section is a top level configuration for GOS wide logger """
        config = Configuration()
        logger_section = config[config.LOGGER]
        self.assertIn(config.NAME, logger_section)
        self.assertIn(config.LEVEL, logger_section)
        self.assertIn(config.FORMAT, logger_section)
        self.assertIn(config.DESTINATION, logger_section)

    def test_initialization_output_section(self):
        """ output section configuration for GOS results to be put in"""
        config = Configuration()
        output_section = config[config.OUTPUT]
        self.assertIn(config.DIR, output_section)
        self.assertIn(config.LOGGER, output_section)
        self.assertIn(config.IOSF, output_section)
        self.assertIn(config.ASSEMBLY_POINTS, output_section)
        self.assertIn(config.GENOMES, output_section)
        self.assertIn(config.STATS, output_section)

        self.assertIsInstance(output_section[config.STATS], dict)
        self.assertIsInstance(output_section[config.ASSEMBLY_POINTS], dict)
        self.assertIsInstance(output_section[config.GENOMES], dict)

    def test_initialization_algorithm_section_executable_containers(self):
        config = Configuration()
        algorithm_section = config[config.ALGORITHM]
        self.assertIn(config.EXECUTABLE_CONTAINERS, algorithm_section)

    def test_initialization_algorithm_section(self):
        """ algorithm section configuration for GOS workflow """
        config = Configuration()
        algorithm_section = config[config.ALGORITHM]
        self.assertIn(config.IOSF, algorithm_section)
        self.assertIn(config.LOGGER, algorithm_section)
        self.assertIn(config.TASKS, algorithm_section)
        self.assertIn(config.PIPELINE, algorithm_section)

        self.assertIsInstance(algorithm_section[config.TASKS], dict)
        self.assertIsInstance(algorithm_section[config.PIPELINE], dict)

    def test_update_with_default_top_level_dir_empty(self):
        """ top level configuration field "dir" default fallback when it is not specified """
        self.init_config[self.init_config.DIR] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.DIR], os.getcwd())
        self.init_config[self.init_config.DIR] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.DIR], os.getcwd())

    def test_update_with_default_to_level_dir_predefined(self):
        """ top level configuration field "dir" default fallback when it is specified """
        self.init_config[self.init_config.DIR] = os.path.join("dir1", "dir2")
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.DIR], os.path.join("dir1", "dir2"))

    def test_update_with_default_top_level_io_silent_fail_empty(self):
        """ top level configuration field "io_silent_fail" default fallback when its not specified """
        self.init_config[self.init_config.IOSF] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], self.init_config.DEFAULT_IOSF)
        self.init_config[self.init_config.IOSF] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], self.init_config.DEFAULT_IOSF)

    def test_update_with_default_top_level_io_silent_fail_predefined(self):
        """ top level configuration field "io_silent_fail" default fallback when its specified """
        self.init_config[self.init_config.IOSF] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], True)
        self.init_config[self.init_config.IOSF] = False
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], False)
        self.init_config[self.init_config.IOSF] = "CustomValue"  # anything that works for if
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.IOSF], "CustomValue")

    def test_update_with_default_logger_name_empty(self):
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         self.init_config.DEFAULT_LOGGER_NAME)
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         self.init_config.DEFAULT_LOGGER_NAME)

    def test_update_with_default_logger_name_predefined(self):
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         str(True))
        self.init_config[self.init_config.LOGGER][self.init_config.NAME] = "MyName"
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.NAME],
                         "MyName")

    def test_update_with_default_logger_level_empty(self):
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         self.init_config.DEFAULT_LOGGER_LEVEL)
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         self.init_config.DEFAULT_LOGGER_LEVEL)

    def test_update_with_default_logger_level_predefined(self):
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = "MyLevel"
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         "MyLevel")
        self.init_config[self.init_config.LOGGER][self.init_config.LEVEL] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.LEVEL],
                         str(True))

    def test_update_with_default_logger_format_empty(self):
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = ""
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         self.init_config.DEFAULT_LOGGER_FORMAT)
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = None
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         self.init_config.DEFAULT_LOGGER_FORMAT)

    def test_update_with_default_logger_format_predefined(self):
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = "MyFormat"
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         "MyFormat")
        self.init_config[self.init_config.LOGGER][self.init_config.FORMAT] = True
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.LOGGER][self.init_config.FORMAT],
                         str(True))

    def test_update_with_default_input_source_empty(self):
        for empty_value in (None, ""):
            self.init_config[self.init_config.INPUT][self.init_config.SOURCE] = empty_value
            self.init_config.update_with_default_values()
            self.assertListEqual(self.init_config[self.init_config.INPUT][self.init_config.SOURCE],
                                 [])

    def test_update_with_default_input_source_predefined(self):
        for source_value in [["path1", "path2"], ["path3", "path4", "path5"]]:
            self.init_config[self.init_config.INPUT][self.init_config.SOURCE] = source_value
            self.init_config.update_with_default_values()
            self.assertListEqual(source_value,
                                 self.init_config[self.init_config.INPUT][self.init_config.SOURCE])

    def test_update_with_default_input_dir_empty(self):
        for empty_value in (None, ""):
            self.init_config[self.init_config.INPUT][self.init_config.DIR] = empty_value
            self.init_config.update_with_default_values()
            self.assertEqual(self.init_config[self.init_config.INPUT][self.init_config.DIR],
                             self.init_config.DEFAULT_INPUT_DIR)

    def test_update_with_default_input_io_silent_fail_empty(self):
        for empty_value in (None, ""):
            for top_level_iosf_value in (True, False):
                self.init_config[self.init_config.INPUT][self.init_config.IOSF] = empty_value
                self.init_config[self.init_config.IOSF] = top_level_iosf_value
                self.init_config.update_with_default_values()
                self.assertEqual(self.init_config[self.init_config.INPUT][self.init_config.IOSF],
                                 top_level_iosf_value)

    def get_list_of_logger_configurations(self):
        return [{
            self.init_config.NAME: "Logger Name 1",
            self.init_config.LEVEL: "info 1",
            self.init_config.FORMAT: "format 1",
            self.init_config.DESTINATION: "destination 1"
        }, {
            self.init_config.NAME: "Logger Name 2",
            self.init_config.LEVEL: "info 2",
            self.init_config.FORMAT: "format 2",
            self.init_config.DESTINATION: "destination 2"
        }]

    def test_update_with_default_input_logger_empty(self):
        top_level_loggers = self.get_list_of_logger_configurations()
        for logger_config in top_level_loggers:
            self.init_config = Configuration()
            self.init_config[self.init_config.INPUT][self.init_config.LOGGER] = {}
            self.init_config[self.init_config.LOGGER] = logger_config
            self.init_config.update_with_default_values()
            self.assertDictEqual(self.init_config[self.init_config.INPUT][self.init_config.LOGGER],
                                 logger_config)

    def test_update_with_default_input_logger_partially_predefined(self):
        partial_logger_configs = [
            {self.init_config.NAME: "My name",
             self.init_config.LEVEL: "My level"},
            {self.init_config.LEVEL: "My level 2"},
            {self.init_config.FORMAT: "My format",
             self.init_config.DESTINATION: "My destination"}
        ]
        for partial_logger_config in partial_logger_configs:
            for full_logger_config in self.get_list_of_logger_configurations():
                self.init_config[self.init_config.INPUT][self.init_config.LOGGER] = deepcopy(partial_logger_config)
                self.init_config[self.init_config.LOGGER] = full_logger_config
                self.init_config.update_with_default_values()
                for key, value in full_logger_config.items():
                    if key not in partial_logger_config:
                        self.assertEqual(full_logger_config[key],
                                         self.init_config[self.init_config.INPUT][self.init_config.LOGGER][key])
                    else:
                        self.assertEqual(partial_logger_config[key],
                                         self.init_config[self.init_config.INPUT][self.init_config.LOGGER][key])

    def test_update_with_default_input_logger_specified(self):
        for full_logger_spec in self.get_list_of_logger_configurations():
            self.init_config[self.init_config.INPUT][self.init_config.LOGGER] = deepcopy(full_logger_spec)
            self.init_config.update_with_default_values()
            self.assertDictEqual(full_logger_spec,
                                 self.init_config[self.init_config.INPUT][self.init_config.LOGGER])

    def test_update_with_default_output_dir_empty(self):
        for empty_value in (None, ""):
            self.init_config[self.init_config.OUTPUT][self.init_config.DIR] = empty_value
            self.init_config.update_with_default_values()
            self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.DIR],
                             os.path.join(self.init_config[self.init_config.DIR],
                                          self.init_config.DEFAULT_OUTPUT_DIR))

    def test_update_with_default_output_io_silent_fail_empty(self):
        for empty_value in (None, ""):
            for top_level_iosf_value in (True, False):
                self.init_config[self.init_config.OUTPUT][self.init_config.IOSF] = empty_value
                self.init_config[self.init_config.IOSF] = top_level_iosf_value
                self.init_config.update_with_default_values()
                self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.IOSF],
                                 top_level_iosf_value)

    def tet_update_with_default_output_logger_empty(self):
        for empty_value in (None, "", {}):
            top_level_loggers = self.get_list_of_logger_configurations()
            for logger_config in top_level_loggers:
                self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER] = empty_value
                self.init_config[self.init_config.LOGGER] = logger_config
                self.init_config.update_with_default_values()
                self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER],
                                     logger_config)

    def test_update_with_default_output_logger_partially_predefined(self):
        partial_logger_configs = [
            {self.init_config.NAME: "My name",
             self.init_config.LEVEL: "My level"},
            {self.init_config.LEVEL: "My level 2"},
            {self.init_config.FORMAT: "My format",
             self.init_config.DESTINATION: "My destination"}
        ]
        for partial_logger_config in partial_logger_configs:
            for full_logger_config in self.get_list_of_logger_configurations():
                self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER] = deepcopy(partial_logger_config)
                self.init_config[self.init_config.LOGGER] = full_logger_config
                self.init_config.update_with_default_values()
                for key, value in full_logger_config.items():
                    if key not in partial_logger_config:
                        self.assertEqual(full_logger_config[key],
                                         self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER][key])
                    else:
                        self.assertEqual(partial_logger_config[key],
                                         self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER][key])

    def test_update_with_default_output_logger_specified(self):
        for full_logger_spec in self.get_list_of_logger_configurations():
            self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER] = deepcopy(full_logger_spec)
            self.init_config.update_with_default_values()
            self.assertDictEqual(full_logger_spec,
                                 self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER])

    def test_update_with_default_output_stats_empty(self):
        for dir_name in ("output_dir1", "output_dir2", "output_dir3"):
            for iosf_value in (True, False):
                for logger_value in self.get_list_of_logger_configurations():
                    self.init_config[self.init_config.OUTPUT][self.init_config.STATS] = {}
                    self.init_config[self.init_config.OUTPUT][self.init_config.DIR] = dir_name
                    self.init_config[self.init_config.OUTPUT][self.init_config.IOSF] = iosf_value
                    self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER] = logger_value
                    self.init_config.update_with_default_values()
                    self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.STATS][self.init_config.FILE],
                                     self.init_config.DEFAULT_OUTPUT_STATS_FILE)
                    self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.STATS][self.init_config.DIR],
                                     self.init_config.DEFAULT_OUTPUT_STATS_DIR)
                    self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.STATS][self.init_config.IOSF],
                                     iosf_value)
                    self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.STATS][self.init_config.LOGGER],
                                         logger_value)
                    self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.STATS][self.init_config.FILE],
                                     self.init_config.DEFAULT_OUTPUT_STATS_FILE)

    def get_full_stats_configs(self):
        return [
            {self.init_config.DIR: "stat_dir_predefined_1",
             self.init_config.FILE: "file_predefined_1.txt",
             self.init_config.LOGGER: self.get_list_of_logger_configurations()[0],
             self.init_config.IOSF: True},
            {self.init_config.DIR: "stat_dir_predefined_2",
             self.init_config.FILE: "file_predefined_2.txt",
             self.init_config.LOGGER: self.get_list_of_logger_configurations()[0],
             self.init_config.IOSF: False},
        ]

    def test_update_with_default_output_stats_partially_predefined(self):
        partial_stats_configs = [
            {self.init_config.DIR: "stats_dir",
             self.init_config.FILE: "my_file_name.txt"},
            {self.init_config.IOSF: True},
            {self.init_config.DIR: "my_dir",
             self.init_config.FILE: "my_file_name2.txt",
             self.init_config.LOGGER: self.get_list_of_logger_configurations()[0]}
        ]
        for partial_stats_config in partial_stats_configs:
            for full_stats_config in self.get_full_stats_configs():
                self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER] = full_stats_config[self.init_config.LOGGER]
                self.init_config[self.init_config.OUTPUT][self.init_config.STATS] = deepcopy(partial_stats_config)
                self.init_config[self.init_config.OUTPUT][self.init_config.IOSF] = full_stats_config[self.init_config.IOSF]
                self.init_config.update_with_default_values()
                for key, value in partial_stats_config.items():
                    self.assertEqual(partial_stats_config[key],
                                     self.init_config[self.init_config.OUTPUT][self.init_config.STATS][key])

    def test_update_with_default_output_stats_predefined(self):
        for full_stats_config in self.get_full_stats_configs():
            self.init_config[self.init_config.OUTPUT][self.init_config.STATS] = deepcopy(full_stats_config)
            self.init_config.update_with_default_values()
            self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.STATS],
                                 full_stats_config)

    def test_update_with_default_output_assembly_points_empty(self):
        self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS] = {}
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.FILE],
                         self.init_config.DEFAULT_OUTPUT_AP_FILE)
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.DIR],
                         self.init_config.DEFAULT_OUTPUT_AP_DIR)
        self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.LOGGER],
                             self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER])
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.GENOME_SPECIFIC],
                         self.init_config.DEFAULT_OUTPUT_AP_GENOME_SPECIFIC)
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.GENOME_SPECIFIC_FNP],
                         self.init_config.DEFAULT_OUTPUT_AP_GSFNP)
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.IOSF],
                         self.init_config[self.init_config.OUTPUT][self.init_config.IOSF])

    def test_update_with_default_output_assembly_points_partially_predefined(self):
        partial_ap_config = {
            self.init_config.DIR: "my_ap_dir",
            self.init_config.GENOME_SPECIFIC: True,
            self.init_config.IOSF: False
        }
        self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS] = partial_ap_config
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.FILE],
                         self.init_config.DEFAULT_OUTPUT_AP_FILE)
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.DIR],
                         partial_ap_config[self.init_config.DIR])
        self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.LOGGER],
                             self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER])
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.GENOME_SPECIFIC],
                         partial_ap_config[self.init_config.GENOME_SPECIFIC])
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.GENOME_SPECIFIC_FNP],
                         self.init_config.DEFAULT_OUTPUT_AP_GSFNP)
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][self.init_config.IOSF],
                         partial_ap_config[self.init_config.IOSF])

    def test_update_with_default_output_assembly_points_predefined(self):
        full_ap_config = {
            self.init_config.FILE: "my_ap_file.txt",
            self.init_config.DIR: "my_ap_dir",
            self.init_config.IOSF: True,
            self.init_config.GENOME_SPECIFIC: True,
            self.init_config.GENOME_SPECIFIC_FNP: "my_patter_string_{genome_name}.txt",
            self.init_config.LOGGER: self.get_list_of_logger_configurations()[0]
        }
        self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS] = full_ap_config
        self.init_config.update_with_default_values()
        for key, value in full_ap_config.items():
            self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.ASSEMBLY_POINTS][key],
                             full_ap_config[key])

    def test_update_with_default_output_genomes_empty(self):
        self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES] = {}
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.DIR],
                         self.init_config.DEFAULT_OUTPUT_GENOMES_DIR)
        self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.LOGGER],
                             self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER])
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.IOSF],
                         self.init_config[self.init_config.OUTPUT][self.init_config.IOSF])
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.OUTPUT_NG_FRAGMENTS],
                         self.init_config.DEFAULT_OUTPUT_GENOMES_ONGF)

    def test_update_with_default_output_genomes_partially_predefined(self):
        partial_genomes_config = {
            self.init_config.OUTPUT_NG_FRAGMENTS: True,
            self.init_config.IOSF: False
        }
        self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES] = partial_genomes_config
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.DIR],
                         self.init_config.DEFAULT_OUTPUT_GENOMES_DIR)
        self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.LOGGER],
                             self.init_config[self.init_config.OUTPUT][self.init_config.LOGGER])
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.IOSF],
                         partial_genomes_config[self.init_config.IOSF])
        self.assertEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES][self.init_config.OUTPUT_NG_FRAGMENTS],
                         partial_genomes_config[self.init_config.OUTPUT_NG_FRAGMENTS])

    def test_update_with_default_output_genomes_predefined(self):
        predefined_genome_config = {
            self.init_config.OUTPUT_NG_FRAGMENTS: True,
            self.init_config.IOSF: False,
            self.init_config.LOGGER: self.get_list_of_logger_configurations()[0],
            self.init_config.DIR: "my_genome_dir"
        }
        self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES] = predefined_genome_config
        self.init_config.update_with_default_values()
        self.assertDictEqual(self.init_config[self.init_config.OUTPUT][self.init_config.GENOMES],
                             predefined_genome_config)

    def test_update_with_default_algorithm_empty(self):
        self.init_config[self.init_config.ALGORITHM] = {}
        self.init_config.update_with_default_values()
        self.assertDictEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.LOGGER],
                             self.init_config[self.init_config.LOGGER])
        self.assertDictEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.TASKS], {
            self.init_config.PATHS: [self.init_config.DEFAULT_ALGORITHM_TASKS_PATH]})
        self.assertEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.EXECUTABLE_CONTAINERS], [])
        expected_pipeline_config = {
            self.init_config.LOGGER: self.init_config[self.init_config.ALGORITHM][self.init_config.LOGGER],
            self.init_config.SELF_LOOP: self.init_config.DEFAULT_ALGORITHM_PIPELINE_SELF_LOOP,
            self.init_config.ENTRIES: [],
            self.init_config.IOSF: self.init_config[self.init_config.ALGORITHM][self.init_config.IOSF]
        }
        self.assertDictEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.PIPELINE],
                             expected_pipeline_config)

    def test_update_with_default_algorithm_predefined_tasks_paths(self):
        my_path_list = ["my_path1", "my_path2"]
        self.init_config[self.init_config.ALGORITHM] = {
            self.init_config.TASKS: {
                self.init_config.PATHS: deepcopy(my_path_list)
            }
        }
        self.init_config.update_with_default_values()
        self.assertIn(self.init_config.DEFAULT_ALGORITHM_TASKS_PATH,
                      self.init_config[self.init_config.ALGORITHM][self.init_config.TASKS][self.init_config.PATHS])
        for my_path in my_path_list:
            self.assertIn(my_path,
                          self.init_config[self.init_config.ALGORITHM][self.init_config.TASKS][self.init_config.PATHS])

    def test_update_with_default_algorithm_pipeline_logger(self):
        self.init_config[self.init_config.ALGORITHM] = {
            self.init_config.PIPELINE: {
                self.init_config.ENTRIES: []
            }
        }
        self.init_config.update_with_default_values()
        self.assertDictEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.PIPELINE][self.init_config.LOGGER],
                             self.init_config[self.init_config.ALGORITHM][self.init_config.LOGGER])

    def test_update_with_default_algorithm_predefined(self):
        predefined_algorithm_config = {
            self.init_config.IOSF: False,
            self.init_config.LOGGER: self.get_list_of_logger_configurations()[0],
            self.init_config.TASKS: {
                self.init_config.PATHS: ["my_path_1", "my_path_2"]
            },
            self.init_config.PIPELINE: {
                self.init_config.LOGGER: self.get_list_of_logger_configurations()[1],
                self.init_config.SELF_LOOP: False,
                self.init_config.ENTRIES: ["round1", "round2"]
            }
        }
        self.init_config[self.init_config.ALGORITHM] = deepcopy(predefined_algorithm_config)
        self.init_config.update_with_default_values()
        self.assertEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.IOSF],
                         predefined_algorithm_config[self.init_config.IOSF])
        self.assertDictEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.LOGGER],
                             predefined_algorithm_config[self.init_config.LOGGER])
        self.assertListEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.TASKS][self.init_config.PATHS],
                             [self.init_config.DEFAULT_ALGORITHM_TASKS_PATH] +
                             predefined_algorithm_config[self.init_config.TASKS][self.init_config.PATHS])
        predefined_algorithm_config[self.init_config.PIPELINE][self.init_config.IOSF] = self.init_config[self.init_config.ALGORITHM][self.init_config.IOSF]
        self.assertDictEqual(self.init_config[self.init_config.ALGORITHM][self.init_config.PIPELINE],
                             predefined_algorithm_config[self.init_config.PIPELINE])

    def test_update_with_default_algorithm_specified_executable_container_instantiation(self):
        self.set_up_executable_containers_for_algorithm_section()
        self.init_config.update_with_default_values()
        self.assertIsInstance(self.init_config[self.init_config.ALGORITHM]["stages"], list)

    def set_up_executable_containers_for_algorithm_section(self):
        ecs = [
            {
                "name": "stage",
                "reference": "stages",
                "entry_type_name": "task"
            }
        ]
        self.init_config[self.init_config.ALGORITHM][self.init_config.EXECUTABLE_CONTAINERS] = ecs

    def test_update_with_default_algorithm_automatically_generated_reference_for_executable_container(self):
        self.init_config[self.init_config.ALGORITHM][self.init_config.EXECUTABLE_CONTAINERS] = [{
            "name": "stage",
            "entry_type_name": "task"
        }]
        self.init_config.update_with_default_values()
        ecs = self.init_config[self.init_config.ALGORITHM][self.init_config.EXECUTABLE_CONTAINERS]
        self.assertEqual(ecs[0]["reference"], "stages")

    def test_update_with_default_algorithm_specified_executable_container_partially_specification(self):
        self.set_up_executable_containers_for_algorithm_section()
        self.init_config[self.init_config.ALGORITHM]["stages"] = [
            {
                self.init_config.NAME: "stage1",
            },
            {
                self.init_config.NAME: "stage2",
                self.init_config.ENTRIES: ["task1", "task2"]
            },
            {
                self.init_config.NAME: "stage3",
                self.init_config.SELF_LOOP: False,
                self.init_config.ENTRIES: ["task1", "task2", "task3"]
            }
        ]
        self.init_config.update_with_default_values()
        stages = self.init_config[self.init_config.ALGORITHM]["stages"]
        self.assertIsInstance(stages, list)
        self.assertEqual(len(stages), 3)
        stage1, stage2, stage3 = stages
        self.assertEqual(stage1[self.init_config.NAME], "stage1")
        self.assertEqual(stage1[self.init_config.SELF_LOOP], self.init_config.DEFAULT_ALGORITHM_EC_SELF_LOOP)
        self.assertListEqual(stage1[self.init_config.ENTRIES], [])

        self.assertEqual(stage2[self.init_config.NAME], "stage2")
        self.assertEqual(stage2[self.init_config.SELF_LOOP], self.init_config.DEFAULT_ALGORITHM_EC_SELF_LOOP)
        self.assertListEqual(stage2[self.init_config.ENTRIES], ["task1", "task2"])

        self.assertEqual(stage3[self.init_config.NAME], "stage3")
        self.assertEqual(stage3[self.init_config.SELF_LOOP], False)
        self.assertListEqual(stage3[self.init_config.ENTRIES], ["task1", "task2", "task3"])


if __name__ == '__main__':
    unittest.main()
