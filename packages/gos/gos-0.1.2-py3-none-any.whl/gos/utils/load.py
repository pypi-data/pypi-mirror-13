# -*- coding: utf-8 -*-
import importlib
import os

import sys

from gos.exceptions import GOSIOException


class Loader(object):
    @staticmethod
    def import_custom_python_file(file_path):
        if not os.path.exists(file_path):
            raise GOSIOException("Specified file does not exists")
        if os.path.isdir(file_path):
            raise GOSIOException("Specified path corresponds to a directory, not a file")
        module_path, file_name = os.path.split(file_path)
        if not file_name.endswith((".py", ".pyc")):
            raise GOSIOException("Specified path does not correspond to python file ")
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        module_name = file_name[:file_name.rfind(".")]
        module = importlib.import_module(module_name)
        objects = [getattr(module, attr_name) for attr_name in dir(module)]
        return file_name, module_path, objects