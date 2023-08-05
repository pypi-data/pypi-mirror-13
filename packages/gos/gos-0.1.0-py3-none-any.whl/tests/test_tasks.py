# -*- coding: utf-8 -*-
import unittest

import importlib
import os
import tempfile
from gos.exceptions import GOSTaskException, GOSIOException
from gos.tasks import BaseTask, TaskLoader


class BaseTaskTestCase(unittest.TestCase):
    def setUp(self):
        self.task_class = BaseTask

    def test_name_property(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "name"))

    def test_self_loop_property(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "self_loop"))

    def test_do_self_loop_property(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "do_self_loop"))

    def test_run_method_existence(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "run"))
        self.assertTrue(callable(getattr(task, "run")))


class TaskLoaderTestCase(unittest.TestCase):
    def test_load_from_file_file_does_not_exists(self):
        file_path = "non_existing_file_pass"
        with self.assertRaises(GOSIOException):
            TaskLoader().load_tasks_from_file(file_path)

    def test_load_from_file_dir_supplied(self):
        dir_path = os.path.dirname(__file__)
        with self.assertRaises(GOSIOException):
            TaskLoader().load_tasks_from_file(dir_path)

    def test_load_from_file_no_name_attribute_on_loaded_class(self):
        bad_class_code = """class MyTaskOne(BaseTask):\n\tdef run(self, assembler_manager):\n\t\tpass\n"""
        source_file = self.create_tmp_py_file()
        source_file.write(self.get_base_task_import_code_string())
        source_file.write(bad_class_code)
        source_file.flush()
        importlib.invalidate_caches()  # importlib invalidate_caches call is required due to this python issue: http://bugs.python.org/issue23412
        source_file_name = source_file.name
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_file(source_file_name)
        source_file.close()

    def test_load_from_file_non_python_file(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py")
        importlib.invalidate_caches()
        with self.assertRaises(GOSIOException):
            TaskLoader().load_tasks_from_file(tmp_file.name)

    def get_base_task_import_code_string(self):
        return "from gos.tasks import BaseTask\n"

    @staticmethod
    def get_tasks_names():
        return ["my_task_one",
                "my_task_two",
                "my_task_three",
                "my_task_four",
                "my_task_five",
                "my_task_six",
                "my_task_seven"]

    def get_custom_task_files_values(self):
        return [
            """class MyTaskOne(BaseTask):\n\tname = "my_task_one"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskTwo(BaseTask):\n\tname = "my_task_two"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskThree(BaseTask):\n\tname = "my_task_three"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskFour(BaseTask):\n\tname = "my_task_four"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskFive(BaseTask):\n\tname = "my_task_five"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskSix(BaseTask):\n\tname = "my_task_six"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskSeven(BaseTask):\n\tname = "my_task_seven"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
        ]

    def get_custom_non_task_classes_code_strings(self):
        return [
            """class MyNoneTaskClass(object):\n\tname = "my_none_base_task"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
        ]

    def test_load_from_file_single_custom_task_class(self):
        with tempfile.NamedTemporaryFile(mode="wt", suffix=".py") as source_file:
            custom_task_file_data = self.get_custom_task_files_values()[0]
            source_file.write(self.get_base_task_import_code_string())
            source_file.write(custom_task_file_data)
            source_file.flush()
            importlib.invalidate_caches()
            source_file_name = source_file.name
            result = TaskLoader().load_tasks_from_file(source_file_name)
            self.assertIn("my_task_one", result)
            self.assertTrue(issubclass(result["my_task_one"], BaseTask))

    def create_tmp_py_file(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        return tmp_file

    def test_load_from_file_multiple_custom_tasks_classes(self):
        source_file = self.create_tmp_py_file()
        source_file.write(self.get_base_task_import_code_string())
        for custom_task_code_string in self.get_custom_task_files_values():
            source_file.write(custom_task_code_string)
        source_file.write(self.get_custom_non_task_classes_code_strings()[0])
        source_file.flush()
        importlib.invalidate_caches()
        source_file_name = source_file.name
        result = TaskLoader().load_tasks_from_file(source_file_name)
        for task_name in ["my_task_one", "my_task_two", "my_task_three"]:
            self.assertIn(task_name, result)
            self.assertTrue(issubclass(result[task_name], BaseTask))
        self.assertNotIn("my_non_base_task", result)
        source_file.close()

    def test_load_from_dir_dir_does_not_exists(self):
        non_existing_dir = "/my_non/existing_dir"
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_dir(non_existing_dir)

    def test_load_from_dir_file_supplied(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt")
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_dir(tmp_file.name)

    def test_load_from_dir_single_file_with_multiple_classes(self):
        tmp_dir = tempfile.TemporaryDirectory()
        tmp_file1 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir.name, delete=False)
        tmp_file1.write(self.get_base_task_import_code_string())
        for task_class_string in self.get_custom_task_files_values():
            tmp_file1.write(task_class_string)
        tmp_file1.flush()
        importlib.invalidate_caches()
        result = TaskLoader().load_tasks_from_dir(tmp_dir.name)
        for task_name in ["my_task_one", "my_task_two", "my_task_three"]:
            self.assertIn(task_name, result)
            self.assertTrue(issubclass(result[task_name], BaseTask))
        tmp_dir.cleanup()

    def test_load_from_dir_non_python_file(self):
        tmp_dir = tempfile.TemporaryDirectory()
        tmp_file1 = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py", dir=tmp_dir.name, delete=False)
        tmp_file1.write(self.get_base_task_import_code_string())
        for task_class_string in self.get_custom_task_files_values():
            tmp_file1.write(task_class_string)
        tmp_file1.flush()
        importlib.invalidate_caches()
        result = TaskLoader().load_tasks_from_dir(tmp_dir.name)
        self.assertDictEqual(result, {})
        tmp_dir.cleanup()

    def test_load_from_dir_multiple_python_files(self):
        tmp_dir = tempfile.TemporaryDirectory()
        tmp_file1 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir.name, delete=False)
        tmp_file2 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir.name, delete=False)
        tmp_file1.write(self.get_base_task_import_code_string())
        tmp_file2.write(self.get_base_task_import_code_string())
        for tasks_class_strings in self.get_custom_task_files_values()[:1]:
            tmp_file1.write(tasks_class_strings)
        tmp_file1.flush()
        for tasks_class_strings in self.get_custom_task_files_values()[1:]:
            tmp_file2.write(tasks_class_strings)
        tmp_file2.flush()
        importlib.invalidate_caches()
        result = TaskLoader().load_tasks_from_dir(tmp_dir.name)
        for task_name in ["my_task_one", "my_task_two", "my_task_three"]:
            self.assertIn(task_name, result)
            self.assertTrue(issubclass(result[task_name], BaseTask))
        tmp_dir.cleanup()

    def test_load_tasks_non_iterable_argument(self):
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks(5)

    def test_load_tasks_only_python_files(self):
        tmp_file1 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file2 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file1.write(self.get_base_task_import_code_string())
        tmp_file2.write(self.get_base_task_import_code_string())
        for tasks_class_strings in self.get_custom_task_files_values()[:1]:
            tmp_file1.write(tasks_class_strings)
        tmp_file1.flush()
        for tasks_class_strings in self.get_custom_task_files_values()[1:]:
            tmp_file2.write(tasks_class_strings)
        tmp_file2.flush()
        importlib.invalidate_caches()
        paths = [tmp_file1.name, tmp_file2.name]
        result = TaskLoader().load_tasks(paths=paths)
        for task_name in ["my_task_one", "my_task_two", "my_task_three"]:
            self.assertIn(task_name, result)
            self.assertTrue(issubclass(result[task_name], BaseTask))

    def test_load_tasks_non_string_value_in_paths(self):
        paths = ["path1", "path2", BaseTask(), "path3"]
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks(paths=paths)

    def test_load_tasks_only_files_some_files_are_non_python(self):
        tmp_file1 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file2 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file3 = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py")
        tmp_file1.write(self.get_base_task_import_code_string())
        tmp_file2.write(self.get_base_task_import_code_string())
        tmp_file3.write(self.get_base_task_import_code_string())
        for tasks_class_strings in self.get_custom_task_files_values()[:1]:
            tmp_file1.write(tasks_class_strings)
        tmp_file1.flush()
        for tasks_class_strings in self.get_custom_task_files_values()[1:2]:
            tmp_file2.write(tasks_class_strings)
        tmp_file2.flush()
        for tasks_class_strings in self.get_custom_task_files_values()[2:]:
            tmp_file3.write(tasks_class_strings)
        tmp_file3.flush()
        importlib.invalidate_caches()
        paths = [tmp_file1.name, tmp_file2.name, tmp_file3.name]
        result = TaskLoader().load_tasks(paths=paths)
        for task_name in ["my_task_one", "my_task_two"]:
            self.assertIn(task_name, result)
            self.assertTrue(issubclass(result[task_name], BaseTask))
        self.assertNotIn("my_task_three", result)

    def test_load_tasks_files_and_dirs(self):
        tmp_dir1 = tempfile.TemporaryDirectory()
        tmp_dir2 = tempfile.TemporaryDirectory()

        tmp_file1 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir1.name, delete=False)
        tmp_file2 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir1.name, delete=False)
        tmp_file3 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir1.name, delete=False)

        tmp_file4 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir2.name, delete=False)
        tmp_file5 = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py", dir=tmp_dir2.name, delete=False)

        tmp_file6 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file7 = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py")

        tmp_files = [tmp_file1, tmp_file2, tmp_file3, tmp_file4, tmp_file5, tmp_file6, tmp_file7]

        for cnt, tmp_file in enumerate(tmp_files):
            tmp_file.write(self.get_base_task_import_code_string())
            tmp_file.write(self.get_custom_task_files_values()[cnt])
            tmp_file.flush()
        importlib.invalidate_caches()
        paths = [tmp_dir1.name, tmp_dir2.name, tmp_file6.name, tmp_file7.name]
        result = TaskLoader().load_tasks(paths=paths)
        for task_name in ["my_task_one", "my_task_two", "my_task_three", "my_task_four", "my_task_six"]:
            self.assertIn(task_name, result)
            self.assertTrue(issubclass(result[task_name], BaseTask))
        self.assertNotIn("my_task_five", result)
        self.assertNotIn("my_task_seven", result)
        tmp_dir1.cleanup()
        tmp_dir2.cleanup()

    def test_load_tasks_from_dir_TaskException_propagation(self):
        tmp_dir = self._prepare_for_TaskException_propagation_test()
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_dir(dir_path=tmp_dir.name, propagate_exceptions=True)
        tmp_dir.cleanup()

    def _prepare_for_TaskException_propagation_test(self):
        tmp_dir = tempfile.TemporaryDirectory()
        tmp_file1 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir.name, delete=False)
        tmp_file2 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", dir=tmp_dir.name, delete=False)
        tmp_file1.write(self.get_base_task_import_code_string())
        tmp_file1.write(self.get_custom_task_files_values()[0])
        tmp_file1.flush()
        tmp_file2.write(self.get_base_task_import_code_string())
        tmp_file2.write("""class Task(BaseTask):\n\tdef run(self, assembler_manager):\n\t\tpass\n""")
        tmp_file2.flush()
        importlib.invalidate_caches()
        return tmp_dir

    def test_load_tasks_from_dir_no_TaskException_propagation(self):
        tmp_dir = self._prepare_for_TaskException_propagation_test()
        result = TaskLoader().load_tasks_from_dir(dir_path=tmp_dir.name, propagate_exceptions=False)
        self.assertIn("my_task_one", result)
        tmp_dir.cleanup()

    def test_load_tasks_TaskException_propagation(self):
        tmp_dir = self._prepare_for_TaskException_propagation_test()
        tmp_file3 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", delete=True)
        tmp_file3.write(self.get_base_task_import_code_string())
        tmp_file3.write(self.get_custom_task_files_values()[1])
        tmp_file3.flush()
        importlib.invalidate_caches()
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks(paths=[tmp_dir.name, tmp_file3.name], propagate_exception=True)
        tmp_dir.cleanup()

    def test_load_tasks_no_TaskException_propagation(self):
        tmp_dir = self._prepare_for_TaskException_propagation_test()
        tmp_file3 = tempfile.NamedTemporaryFile(mode="wt", suffix=".py", delete=True)
        tmp_file3.write(self.get_base_task_import_code_string())
        tmp_file3.write(self.get_custom_task_files_values()[1])
        tmp_file3.flush()
        importlib.invalidate_caches()
        result = TaskLoader().load_tasks(paths=[tmp_dir.name, tmp_file3.name], propagate_exception=False)
        self.assertEqual(len(result), 3)  # base + two valid tasks
        self.assertIn("my_task_one", result)
        self.assertIn("my_task_two", result)
        tmp_dir.cleanup()


if __name__ == '__main__':
    unittest.main()
