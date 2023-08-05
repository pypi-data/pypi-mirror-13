# -*- coding: utf-8 -*-
import importlib
import inspect
from .types import SettingsLoadStrategy


def _is_python_module(file_name):
    try:
        importlib.import_module(file_name)
        return True
    except ImportError:
        return False


def _load_python_module(settings_file):
    result = {}
    module = importlib.import_module(settings_file)
    for setting in (s for s in dir(module) if not s.startswith('_')):
        setting_value = getattr(module, setting)
        if not inspect.ismodule(setting_value):
            result[setting] = setting_value
    return result


strategy = SettingsLoadStrategy(
    name='python',
    is_valid_file=_is_python_module,
    load_settings_file=_load_python_module
)
