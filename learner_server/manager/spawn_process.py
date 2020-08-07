# -*- coding: utf-8 -*-

from learner_server.configs import ApplicationConfiguration
from learner_server.utils import ArgParser, LogHandler
from learner_server.processor import Learner

import sys
import argparse
import logging

from typing import List


def process_generator(argv: List[str] = ()):
    """
    argv = ['--step', step_val] + [f'--{arg_name}', arg_val for arg in argv]
    """

    config: ApplicationConfiguration = ApplicationConfiguration.instance()
    config.init('configs/config.properties')

    arg_parser = ArgParser.instance()
    arg_parser.init(config)

    # print(argv)
    args_default: argparse.ArgumentParser = arg_parser.get_parser('DEFAULT')
    step: str = args_default.parse_args(argv).step
    # print(step)

    args_step: argparse.ArgumentParser = arg_parser.get_parser(step)
    # print(args_step)
    args_step_dict: dict = args_step.parse_args(argv[2:]).__dict__
    # print(args_step_dict)

    learner = Learner()
    learner.init()

    learner.run(step=step, **args_step_dict)


if __name__ == '__main__':
    process_generator(sys.argv[1:])
    exit(0)
