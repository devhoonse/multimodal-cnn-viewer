# -*- coding: utf-8 -*-

from ..common import SingletonInstance

from typing import Dict


class BuiltinHandler(SingletonInstance):
    _BUILTIN_TYPES: Dict[str, type] = {
        class_name: __builtins__[class_name]
        for class_name in __builtins__.keys()
        if isinstance(__builtins__[class_name], type)
    }

    def __init__(self):
        pass

    @classmethod
    def get_builtin_type_by_name(cls, class_name: str) -> type:
        return cls._BUILTIN_TYPES.get(class_name)
