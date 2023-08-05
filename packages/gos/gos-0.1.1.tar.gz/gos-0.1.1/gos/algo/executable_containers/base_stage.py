# -*- coding: utf-8 -*-
from gos.executable_containers import ExecutableContainer


class Stage(ExecutableContainer):
    entries_type_names = ["task"]
    type_name = "stage"
