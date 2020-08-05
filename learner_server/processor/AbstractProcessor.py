# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..configs import ApplicationConfiguration

from abc import *
from multiprocessing import Lock


class AbstractProcessor(SingletonInstance):

    @abstractmethod
    def run(self,  *args, **kwargs):
        pass
