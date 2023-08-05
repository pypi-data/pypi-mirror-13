# -*- coding: utf-8 -*-
import logging
import unittest

import importlib
import tempfile
from gos.algo.executable_containers.base_round import Round
from gos.algo.executable_containers.base_stage import Stage
from gos.algo.executable_containers.pipeline import Pipeline
from gos.exceptions import GOSExecutableContainerException, GOSIOException
from gos.executable_containers import ExecutableContainer
from gos.manager import Manager


class ExecutableContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.executable_container = ExecutableContainer()
        self.ec = self.executable_container
        self.dm = Manager({})
        self.dm.logger = logging.getLogger()

    ################################################################################
    #
    # testing attributes, that are utilized in referencing the EC object itself
    #
    ################################################################################

    def test_name_attribute(self):
        self.assertTrue(hasattr(self.ec, "name"))

    def test_type_name_attribute(self):
        self.assertTrue(hasattr(self.ec, "type_name"))

    def test_group_reference_name_attribute(self):
        self.assertTrue(hasattr(self.ec, "group_reference_name"))

    ################################################################################
    #
    # testing attributes, that are utilized in referencing other EC / tasks that
    #      this EC object is working with
    #
    ################################################################################

    def test_entries_type_name_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries_type_names"))

    def test_entries_info_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries_names"))

    def test_entries_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries"))

    ################################################################################
    #
    # testing internal attributes and methods for the EC object
    #
    ################################################################################
    def test_self_loop_attribute(self):
        self.assertTrue(hasattr(self.ec, "self_loop"))

    def test_do_self_loop_attribute(self):
        self.assertTrue(hasattr(self.ec, "do_self_loop"))

    def test_run_method_existence(self):
        self.assertTrue(hasattr(self.ec, "run"))
        self.assertTrue(callable(getattr(self.ec, "run")))

    def test_logger_attribute(self):
        self.assertTrue(hasattr(self.ec, "logger"))

    ################################################################################
    #
    # testing logic of EC object
    #
    ################################################################################
    def test_default_group_reference_name_attribute(self):
        ec = ExecutableContainer(name="test")
        self.assertEqual(ec.group_reference_name, "tests")

    def test_initialization_with_class_defined_entries_names_value(self):
        entry_ = ["entry1", "entry2", "entry3"]

        class MyEC(ExecutableContainer):
            entries_names = entry_

        value = MyEC()
        self.assertListEqual(value.entries_names, entry_)

    def test_initialization_with_no_defined_entries_names_values(self):
        class MyEC(ExecutableContainer):
            pass

        self.assertListEqual(MyEC().entries_names, [])

    def test_initialization_with_specified_entries_names_value(self):
        class MyEC(ExecutableContainer):
            pass

        value_ = ["task1", "round1", "value1"]
        self.assertListEqual(MyEC(entries_names=value_).entries_names, value_)

    def test_initialization_with_class_defined_entries_type_names(self):
        entry_ = ["task", "round"]

        class MyEC(ExecutableContainer):
            entries_type_names = entry_

        value = MyEC()
        self.assertListEqual(value.entries_type_names, entry_)

    def test_initialization_with_no_defined_entries_type_names_value(self):
        class MyEC(ExecutableContainer):
            pass

        self.assertEqual(MyEC().entries_type_names, [])

    def test_initialization_with_specified_entries_type_names_value(self):
        class MyEC(ExecutableContainer):
            pass

        value_ = ["task", "round", "value"]
        self.assertListEqual(MyEC(entries_type_names=value_).entries_type_names, value_)

    def test_initialization_entries_by_default_are_empty_list(self):
        self.assertListEqual(ExecutableContainer().entries, [])

    def test_setup_from_config_no_name(self):
        with self.assertRaises(GOSExecutableContainerException):
            ExecutableContainer.setup_from_config(manager=self.dm, config={})

    def test_setup_from_config_self_loop_value(self):
        ec = ExecutableContainer.setup_from_config(config={"name": "my_name",
                                                           "self_loop": False},
                                                   manager=self.dm)
        self.assertFalse(ec.self_loop)

    def test_setup_from_config_entries_names(self):
        stage_name_list = ["stage1", "stage2", "stage3"]
        ec = ExecutableContainer.setup_from_config(config={"name": "my_name",
                                                           "entries_names": stage_name_list},
                                                   manager=self.dm)
        self.assertListEqual(ec.entries_names, stage_name_list)

    def test_setup_from_file_file_does_not_exists(self):
        non_existing_path = "non_existing_path.py"
        with self.assertRaises(GOSIOException):
            next(ExecutableContainer.setup_from_file(non_existing_path))

    def test_setup_from_file_non_python_file(self):
        non_py_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py")
        with self.assertRaises(GOSIOException):
            next(ExecutableContainer.setup_from_file(non_py_file.name))

    def test_setup_from_file_no_unique_name(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write("""class MyContainer(ExecutableContainer):\n\tdef setup(self):\n\t\tpass""")
        tmp_file.flush()
        importlib.invalidate_caches()
        with self.assertRaises(GOSExecutableContainerException):
            next(ExecutableContainer.setup_from_file(tmp_file.name))

    def get_executable_container_import_string(self):
        return """from gos.executable_containers import ExecutableContainer\n"""

    def test_setup_from_file_no_setup_method(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write("""class MyContainer(ExecutableContainer):\n\tname="new_executable_container_name" """)
        tmp_file.flush()
        importlib.invalidate_caches()
        with self.assertRaises(GOSExecutableContainerException):
            next(ExecutableContainer.setup_from_file(tmp_file.name))

    def test_setup_from_file(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write(
                """class MyContainer(ExecutableContainer):\n\tname="my_ec"\n\tdef setup(self):\n\t\tself.entries_names = ["entry1"]\n\t\tself.entries_type_names=["task"] """)
        tmp_file.flush()
        importlib.invalidate_caches()
        result = next(ExecutableContainer.setup_from_file(tmp_file.name))
        self.assertIsInstance(result, ExecutableContainer)
        self.assertListEqual(result.entries_names, ["entry1"])
        self.assertListEqual(result.entries_type_names, ["task"])

    def test_setup_from_file_multiple_ex_containers(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write(
                """class MyContainerOne(ExecutableContainer):\n\tname="my_ec_1"\n\tdef setup(self):\n\t\tself.entries_names = ["entry1"]\n\t\tself.entries_type_names=["task"]\ndef run(self, manager):\n\t\tpass""")
        tmp_file.write(
                """\n\n\nclass MyContainerTwo(ExecutableContainer):\n\tname="my_ec_2"\n\tdef setup(self):\n\t\tself.entries_names = ["entry1"]\n\t\tself.entries_type_names=["task"]\ndef run(self, manager):\n\t\tpass """)
        tmp_file.flush()
        importlib.invalidate_caches()
        result = list(ExecutableContainer.setup_from_file(tmp_file.name))
        self.assertEqual(len(result), 2)
        names = {ex.name for ex in result}
        self.assertSetEqual({"my_ec_1", "my_ec_2"}, names)


class BaseStageTestCase(unittest.TestCase):
    def test_base_stage_executable_container_entries_type_name_attribute(self):
        self.assertListEqual(Stage.entries_type_names, ["task"])

    def test_base_stage_executable_container_type_name(self):
        self.assertEqual(Stage.type_name, "stage")


class BaseRoundTestCase(unittest.TestCase):
    def test_base_round_executable_container_entries_type_name_attribute(self):
        self.assertListEqual(Round.entries_type_names, ["stage"])

    def test_base_round_executable_container_type_name(self):
        self.assertEqual(Round.type_name, "round")


class PipelineTestCase(unittest.TestCase):
    def test_pipeline_executable_container_entries_type_name_attribute(self):
        self.assertIsNone(Pipeline.entries_type_names)

    def test_pipeline_executable_container_type_name(self):
        self.assertEqual(Pipeline.type_name, "pipeline")


if __name__ == '__main__':
    unittest.main()
