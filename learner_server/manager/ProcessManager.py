# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..dao import AbstractSession, ProcessDAO
from ..processor import Learner
from ..configs import ApplicationConfiguration

import os
import signal
from multiprocessing import Process


class ProcessManager(SingletonInstance):
    """
    Available for Both of WebApp and Cron-Monitor
    """

    def __init__(self):
        self.max_processes: int = 1
        self._learner: Learner = None

    def init(self, config: ApplicationConfiguration):
        self._learner = Learner.instance()
        self._learner.init(self, config)

    def is_available(self) -> bool:
        pass

    @classmethod
    def get_queue_list(cls, session: AbstractSession):
        processes_dao: ProcessDAO = ProcessDAO.instance()
        queue_list = ProcessDAO.map(processes_dao.select_queue_list(session=session))
        return queue_list

    @classmethod
    def get_process_list(cls, session: AbstractSession):
        processes_dao: ProcessDAO = ProcessDAO.instance()
        process_list = ProcessDAO.map(processes_dao.select_process_list(session=session))
        return process_list

    @classmethod
    def get_status_list(cls, session: AbstractSession):
        process_dao: ProcessDAO = ProcessDAO.instance()
        status_list = process_dao.map(process_dao.select(session=session))
        return status_list

    def get_process_info(self):
        pass

    def start_process(self, prj, work, step, **kwargs):
        result: str

        if self.is_available():
            pid = self._create_process(step, **kwargs)
            result = f"PID = {pid}"
        else:
            result = f"QUEUE"

        log_msg: str = f"REQUEST - start {prj} / {work} / {step} -> {result}"
        return log_msg

    def kill_process(self, prj, work, step):
        log_msg: str = f"REQUEST - kill {prj} / {work} / {step}"

        pid: int = self._get_requested_pid(prj, work, step)
        os.kill(pid, signal.SIGSTOP)
        return log_msg

    def receive_progression(self, msg):
        """
        processor 클래스들이 단계별 Callback 함수 내부에서 호출함으로써
        manager 에 현재 진행 상황을 보내기 위한 용도
        manager 의 입장에서는 msg 를 받는 것 (receive)
        :return:
        """
        pass

    def _create_process(self, step, **kwargs):
        target_function: callable = self._learner.get_target_job(step)
        proc = Process(target=target_function, kwargs=kwargs)
        return proc.pid

    def _search_process(self, prj, work, step):
        pass

    def _get_requested_pid(self, prj, work, step) -> int:
        pass

    def _get_ppid(self):
        pass
