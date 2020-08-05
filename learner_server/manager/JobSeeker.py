# -*- coding: utf-8 -*-


from ..common import SingletonInstance
from ..dao import AbstractSession, OracleDataSource
from . import ProcessManager


class JobSeeker(SingletonInstance):
    """
    JobSeeker Object which will be set into cron-job every minutes.
    Searching for New Job,
    Stopping Current Job,
    ..., etc, ...
    Maybe a Plain Wrapper for ProcessManager Class.
    """
    def __init__(self):
        self.proc_manager = ProcessManager.instance()

    @classmethod
    def get_current_status(cls, session: AbstractSession):
        status_list = ProcessManager.instance().get_status_list(session)
        return status_list

    @classmethod
    def get_current_processes(cls, session: AbstractSession):
        process_list = ProcessManager.instance().get_process_list(session)
        return process_list

    @classmethod
    def get_from_queue(cls, session: AbstractSession):
        queue_list = ProcessManager.instance().get_queue_list(session)
        return queue_list

    def start_process(self):
        process_manager = ProcessManager.instance()
        if self._exists_new_in_queue():
            process_manager.run_process()


