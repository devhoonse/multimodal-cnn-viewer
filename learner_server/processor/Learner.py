# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..configs import ApplicationConfiguration
from ..manager import ProcessManager
from ..utils import LogHandler
from ..processor import *

import logging
from typing import Dict


class Learner(SingletonInstance):
    """
    Maybe.. it would be deprecated...
    """

    def __init__(self):
        self._parent = None         # type: ProcessManager
        self.loader = None          # type: Loader
        self.preprocessor = None    # type: Preprocessor
        self.evaluator = None       # type: Evaluator
        self.predictor = None       # type: Predictor

        self._STEP_MAP: Dict[str, AbstractProcessor] = dict()

    def init(self, parent: ProcessManager = None):
        self._parent = parent
        self.loader = Loader.instance()
        self.preprocessor = Preprocessor.instance()
        self.evaluator = Evaluator.instance()
        self.predictor = Predictor.instance()

        self._STEP_MAP = {
            'S01': self.loader,
            'S02': self.preprocessor,
            'S03': self.evaluator,
            'S04': self.predictor
        }

    def get_target_job(self, step: str) -> callable:
        return self._STEP_MAP[step].run

    def run(self, step: str, *args, **kwargs):
        target_job: callable = self.get_target_job(step)
        target_job(*args, **kwargs)
