# -*- coding: utf-8 -*-


from learner_server.utils import ArgParser
from learner_server.processor import Learner


def process_generator():
    learner = Learner()
    learner.init()

    while True:
        1 == 1


if __name__ == '__main__':
    process_generator()
