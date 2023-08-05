# -*- coding: utf-8 -*-
import os
from gos.exceptions import GOSTaskException, GOSIOException
from gos.utils.load import Loader


class BaseTask(object):
    name = "BaseTask"
    self_loop = False
    do_self_loop = False

    def run(self, manager):
        raise NotImplemented("run method shall be implemented for all the subclasses of BaseTask")


class TaskLoader(object):

    def load_tasks_from_file(self, file_path):
        """ Imports specified python module and returns subclasses of BaseTask from it

        :param file_path: a fully qualified file path for a python module to import CustomTasks from
        :type file_path: `str`
        :return: a dict of CustomTasks, where key is CustomTask.name, and value is a CustomClass task itself
        :rtype: `dict`
        """
        file_name, module_path, objects = Loader.import_custom_python_file(file_path)
        result = {}
        for entry in objects:
            try:
                if issubclass(entry, BaseTask):
                    if entry.__name__ != BaseTask.__name__ and entry.name == BaseTask.name:
                        raise GOSTaskException("Class {class_name} form file {file_name} does not have a unique `name` class field. "
                                               "All custom tasks must have a unique `name` class field for them, tat is used for future reference"
                                               "".format(class_name=entry.name, file_name=os.path.join(module_path, file_name)))
                    result[entry.name] = entry
            except TypeError:
                continue
        return result

    def load_tasks_from_dir(self, dir_path, propagate_exceptions=False):
        """ Imports all python modules in specified directories and returns subclasses of BaseTask from them

        :param propagate_exceptions: a flag that indicates if exceptions from single file import shall be raised during the
            whole directory lookup
        :param dir_path: fully qualified directory path, where all python modules will be search for subclasses of BaseTask
        :type dir_path: `str`
        :return: a dict of CustomTasks, where key is CustomTask.name, and value is a CustomClass task itself
        :rtype: `dict`
        """
        if not os.path.exists(dir_path):
            raise GOSTaskException()
        if os.path.isfile(dir_path):
            raise GOSTaskException()
        result = {}
        for file_basename in os.listdir(path=dir_path):
            full_file_path = os.path.join(dir_path, file_basename)
            try:
                result.update(self.load_tasks_from_file(full_file_path))
            except (GOSTaskException, GOSIOException):
                if propagate_exceptions:
                    raise
        return result

    def load_tasks(self, paths, propagate_exception=False):
        """ Loads all subclasses of BaseTask from modules that are contained in supplied directory paths or direct module paths

        :param propagate_exception: a flag that indicates if exceptions from single file import shall be raised during the
            whole directory lookup
        :param paths: an iterable of fully qualified paths to python modules / directories, from where we import subclasses of BaseClass
        :type paths: `iterable`(`str`)
        :return: a dict of CustomTasks, where key is CustomTask.name, and value is a CustomClass task itself
        :rtype: `dict`
        """
        try:
            result = {}
            for path in paths:
                try:
                    if os.path.isdir(path):
                        result.update(self.load_tasks_from_dir(dir_path=path, propagate_exceptions=propagate_exception))
                    elif os.path.isfile(path):
                        result.update(self.load_tasks_from_file(file_path=path))
                except (GOSTaskException, GOSIOException):
                    if propagate_exception:
                        raise
            return result
        except TypeError:
            raise GOSTaskException("Argument for `load_tasks` method must be iterable")
