# -*- coding: utf-8 -*-
import unittest

import importlib
import tempfile
from gos.configuration import Configuration
from gos.exceptions import GOSTaskException
from gos.manager import Manager
from gos.tasks import BaseTask, TaskLoader
from tests.test_tasks import TaskLoaderTestCase


class ManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.am = Manager(config=Configuration())

    def test_manager_init(self):
        config = Configuration()
        am = Manager(config=config)
        self.assertDictEqual(config, am.configuration)

    def create_correct_temporary_tasks_files(self):
        result = []
        tltc = TaskLoaderTestCase()
        for task_string_data in tltc.get_custom_task_files_values():
            tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
            tmp_file.write(tltc.get_base_task_import_code_string())
            tmp_file.write(task_string_data)
            tmp_file.flush()
            result.append(tmp_file)
        return result

    def test_manager_initiate_tasks(self):
        tmp_files = self.create_correct_temporary_tasks_files()  # have to keep reference to tmp_file objects,
        # otherwise object are deleted by garbage collector and
        # corresponding files are deleted
        self.am.configuration[Configuration.ALGORITHM][Configuration.TASKS] = {
            Configuration.PATHS: [f.name for f in tmp_files]
        }
        importlib.invalidate_caches()
        self.am.initiate_tasks()
        self.assertTrue(hasattr(self.am, "tasks_classes"))
        self.assertTrue(isinstance(self.am.tasks_classes, dict))
        for task_name in TaskLoaderTestCase.get_tasks_names():
            self.assertIn(task_name, self.am.tasks_classes)
            self.assertTrue(issubclass(self.am.tasks_classes[task_name], BaseTask))

    def test_manager_instantiate_tasks(self):
        self.am.tasks_classes = self.get_tasks_classes()
        self.am.instantiate_tasks()
        self.check_task_instantiation_results()

    def get_tasks_classes(self):
        tmp_files = self.create_correct_temporary_tasks_files()
        paths = [f.name for f in tmp_files]
        importlib.invalidate_caches()
        return TaskLoader().load_tasks(paths=paths)

    def test_manager_instantiate_tasks_error_task_instantiation_no_silent_fail(self):
        self._prepare_error_task_instantiation_test_case()
        with self.assertRaises(GOSTaskException):
            self.am.instantiate_tasks()

    def test_manager_instantiate_tasks_error_task_instantiation_silent_fail(self):
        self._prepare_error_task_instantiation_test_case()
        self.am.configuration[Configuration.ALGORITHM][Configuration.IOSF] = True
        self.am.instantiate_tasks()
        del self.am.tasks_classes[self._get_task_class_with_error().name]
        self.check_task_instantiation_results()

    def _prepare_error_task_instantiation_test_case(self):
        self.am.tasks_classes = self.get_tasks_classes()
        self.am.configuration[Configuration.ALGORITHM][Configuration.IOSF] = False
        error_task = self._get_task_class_with_error()
        self.am.tasks_classes.update({error_task.name: error_task})

    def check_task_instantiation_results(self):
        for task_name in self.am.tasks_classes:
            self.assertIn(task_name, self.am.tasks_instances)
            self.assertIsInstance(self.am.tasks_instances[task_name], BaseTask)
            self.assertIsInstance(self.am.tasks_instances[task_name], self.am.tasks_classes[task_name])

    def _get_task_class_with_error(self):
        class ErrorTask(BaseTask):
            name = "error_task"

            def __init__(self):
                self.a = [1, 2, 3][3]

            def run(self, manager):
                pass
        return ErrorTask

    def test_manager_get_task(self):
        task = self._get_my_task_instance()
        self.am.tasks_instances[task.name] = task
        self.assertEqual(self.am.get_task_instance(task.name), task)

    def test_manager_get_task_name_does_not_exist(self):
        with self.assertRaises(KeyError):
            self.am.get_task_instance("non_existing_name")

    def _get_my_task_class(self):
        class MyTask(BaseTask):
            name = "my_task"

            def run(self, manager):
                pass

        return MyTask

    def _get_my_task_instance(self):
        return self._get_my_task_class()()


if __name__ == '__main__':
    unittest.main()
