# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..configs import ApplicationConfiguration
from .BuiltinHandler import BuiltinHandler

from typing import Dict, Any
import json
import argparse


class ArgParser(SingletonInstance):
    """
    Argument Key Names Should be Defined in Lower Cases
    """

    def __init__(self):
        self.parsers: Dict[str, argparse.ArgumentParser] = dict()

    def init(self, config: ApplicationConfiguration):

        with open(config.find('Argument', 'args.json'), encoding="UTF-8") as json_file:
            definition = json.loads(json_file.read())

        for step in definition.keys():
            self.parsers[step] = argparse.ArgumentParser()
            self.parsers[step].formatter_class = argparse.ArgumentDefaultsHelpFormatter
            for key, value in definition[step].items():
                type_object: type = BuiltinHandler.get_builtin_type_by_name(value["type"])
                self.parsers[step].add_argument(f'--{key}',
                                                type=type_object,
                                                help=value["help"],
                                                default=value["default"])

    def get_parser(self, name: str):
        return self.parsers.get(name, None)
