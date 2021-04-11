# -*- coding: utf-8 -*-

from learner_server.configs import ApplicationConfiguration
from learner_server.utils import ArgParser, LogHandler
from learner_server.processor import Learner

import sys
import argparse
import logging

from typing import List


# Will be Deprecated


def process_generator(argv: List[str] = ()):
    """
    argv = ['--mdl_id', mdl_id] ['--pipeln_id', pipeln_id] + [f'--{arg_name}', arg_val for arg in argv]
    """

    # config: ApplicationConfiguration = ApplicationConfiguration.instance()
    # config.init('configs/config.properties')
    #
    # arg_parser = ArgParser.instance()
    # arg_parser.init(config)

    print(argv)
    # parser: argparse.ArgumentParser = arg_parser.get_parser('JOB')
    # mdl_id: str = parser.parse_args(argv).mdl_id
    # pipeln_id: str = parser.parse_args(argv).pipeln_id
    # print(f"start {mdl_id} - {pipeln_id}")
    #
    # args_step_dict: dict = parser.parse_args(argv[2:]).__dict__
    # print(args_step_dict)

    while True:
        pass

    # args_step: argparse.ArgumentParser = arg_parser.get_parser(step)
    # print(args_step)
    # args_step_dict: dict = args_step.parse_args(argv[2:]).__dict__
    # print(args_step_dict)

    # learner = Learner()
    # learner.init()
    #
    # learner.run(step=step, **args_step_dict)


if __name__ == '__main__':
    try:
        process_generator(sys.argv[1:])
    except Exception as e:
        print(e)
    exit(0)
