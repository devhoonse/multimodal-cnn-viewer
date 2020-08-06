# -*- coding: utf-8 -*-

from learner_server.configs import ApplicationConfiguration
from learner_server.utils import ArgParser, LogHandler
from learner_server.processor import Learner

import sys
import logging


def process_generator():

    config: ApplicationConfiguration = ApplicationConfiguration.instance()
    config.init('configs/config.properties')

    arg_parser = ArgParser.instance()
    arg_parser.init(config)

    learner = Learner()
    learner.init()

    learner.run(arg_parser.get_step_parser('DEFAULT').parse_args('step'))

    while True:
        1 == 1


if __name__ == '__main__':
    process_generator()
