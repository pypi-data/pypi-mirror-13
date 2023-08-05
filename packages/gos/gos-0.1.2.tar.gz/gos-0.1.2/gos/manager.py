# -*- coding: utf-8 -*-
from gos.configuration import Configuration
from gos.exceptions import GOSTaskException, GOSExecutableContainerException
from gos.executable_containers import ExecutableContainer
from gos.tasks import TaskLoader


class Manager(object):
    def __init__(self, config):
        self.configuration = config
        self.tasks_classes = {}
        self.tasks_instances = {}
        self.executable_containers_classes = {}
        self.executable_containers_instances = {}

    def initiate_tasks(self):
        """ Loads all tasks using `TaskLoader` from respective configuration option """
        self.tasks_classes = TaskLoader().load_tasks(
            paths=self.configuration[Configuration.ALGORITHM][Configuration.TASKS][Configuration.PATHS])

    def instantiate_tasks(self):
        """ All loaded tasks are initialized. Depending on configuration fails in such instantiations may be silent """
        self.tasks_instances = {}
        for task_name, task_class in self.tasks_classes.items():
            try:
                self.tasks_instances[task_name] = task_class()
            except Exception as ex:
                if not self.configuration[Configuration.ALGORITHM][Configuration.IOSF]:
                    raise GOSTaskException("An exception happened during the task instantiation."
                                           "{exception}".format(exception=ex))

    def initiate_executable_containers(self):
        for entry in self.configuration[Configuration.ALGORITHM]["executable_containers"]:
            if "reference" in entry:
                reference = entry["reference"]
                for ec_config in self.configuration[Configuration.ALGORITHM][reference]:
                    ec_config["group_reference_name"] = reference
                    result = ExecutableContainer.setup_from_config(manager=self, config=ec_config)
                    self.executable_containers_instances[result.name] = result
            elif "paths" in entry:
                paths = entry["paths"]
                for path in paths:
                    try:
                        for ec_instance in ExecutableContainer.setup_from_file(file_path=path):
                            self.executable_containers_instances[ec_instance.name] = ec_instance
                    except GOSExecutableContainerException:
                        continue
        if "pipeline" not in self.configuration[Configuration.ALGORITHM]["executable_containers"]:
            pipeline_config = self.configuration[Configuration.ALGORITHM]["pipeline"]
            if "name" not in pipeline_config:
                pipeline_config["name"] = "pipeline"
            self.executable_containers_instances["pipeline"] = ExecutableContainer.setup_from_config(manager=self,
                                                                                                     config=pipeline_config)

    def instantiate_executable_containers(self):
        for executable_container in self.executable_containers_instances.values():
            for entry_name in executable_container.entries_names:
                try:
                    entry = self.tasks_instances[entry_name]
                except KeyError:
                    entry = self.executable_containers_instances[entry_name]
                executable_container.entries.append(entry)

    def run(self):
        self.executable_containers_instances["pipeline"].run(manager=self)

    def get_task_instance(self, task_name):
        return self.tasks_instances[task_name]

    def get_executable_container_instance(self, ec_name):
        return self.executable_containers_instances[ec_name]
