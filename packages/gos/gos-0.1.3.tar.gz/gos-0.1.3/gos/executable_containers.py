# -*- coding: utf-8 -*-

from gos.exceptions import GOSExecutableContainerException
from gos.utils.load import Loader

DEFAULT_SELF_LOOP = False


class ExecutableContainer(object):
    name = "executable_container"
    type_name = "executable_container"

    def __init__(self, name=None, type_name=None, group_reference_name=None, self_loop=DEFAULT_SELF_LOOP, do_self_loop=False,
                 entries_names=None, entries=None,
                 entries_type_names=None, logger=None):

        self.name = self.__class__.name if name is None else name
        self.type_name = self.__class__.type_name if type_name is None else type_name

        if group_reference_name is None:
            group_reference_name = self.group_reference_name if \
                hasattr(self, "group_reference_name") and self.group_reference_name is not None else \
                self._get_default_group_reference_name()
        self.group_reference_name = group_reference_name

        if entries_names is None:
            entries_names = self.entries_names if hasattr(self, "entries_names") else []
        self.entries_names = entries_names

        if entries_type_names is None:
            entries_type_names = self.entries_type_names if hasattr(self, "entries_type_names") else []
        self.entries_type_names = entries_type_names

        self.entries = [] if entries is None else entries

        self.self_loop = self_loop
        self.do_self_loop = do_self_loop
        self.logger = logger

    def _get_default_group_reference_name(self):
        return self.name + "s"

    def run(self, manager):
        for entry in self.entries:
            entry.do_self_loop = False
            entry.run(manager=manager)
            while entry.self_loop and entry.do_self_loop:
                entry.do_self_loop = False
                entry.run(manager=manager)

    @staticmethod
    def setup_from_config(manager, config):
        try:
            name = config["name"]
        except KeyError:
            raise GOSExecutableContainerException()
        reference = config.get("group_reference_name")
        entries_type_names = config.get("entries_type_names")
        entries_names = config.get("entries_names")
        self_loop = config.get("self_loop", DEFAULT_SELF_LOOP)
        result = ExecutableContainer(name=name, self_loop=self_loop, entries_names=entries_names, entries_type_names=entries_type_names,
                                     group_reference_name=reference)
        manager.logger.debug("Created {name} executable container from config".format(name=result.name))
        return result

    @staticmethod
    def setup_from_file(file_path):
        flag = False
        file_name, module_path, objects = Loader.import_custom_python_file(file_path)
        for entry in objects:
            try:
                if issubclass(entry, ExecutableContainer) and entry.__name__ != ExecutableContainer.__name__:
                    if entry.name == ExecutableContainer.name:
                        continue
                    elif not hasattr(entry, "setup"):
                        continue
                    flag = True
                    result = entry()
                    result.setup()
                    yield result
            except TypeError:
                continue
        if not flag:
            raise GOSExecutableContainerException()
