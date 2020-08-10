# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..configs import ApplicationConfiguration
from ..dao import AbstractSession, ProcessDAO, ParametersDAO
from ..utils import JsonParser, DateTimeUtility
from ..processor import Learner

import os
import sys
import datetime
import signal
import psutil   # Fixme: 3rd-Party Dependency
import re
import subprocess
from multiprocessing import Process, Lock
from collections import OrderedDict


class ProcessManager(SingletonInstance):
    """
    Available for Both of WebApp and Cron-Monitor
    """

    REGEX_PNAME: str = r'^LEARNER[:][<](.*)[>][_][<](.*)[>]_[<](.*)[>]'
    FORM_PNAME: str = 'LEARNER:<{}>_<{}>_<{}>'

    def __init__(self):
        self.max_processes: int = 1
        self.path_std_out: str = ''
        self.path_std_err: str = ''
        self._learner: Learner = None

    def init(self, config: ApplicationConfiguration):
        self.max_processes = int(config.find('Server', 'process.max'))
        self.path_std_out = config.find('Logging', 'std.out')
        self.path_std_err = config.find('Logging', 'std.err')
        self._learner = Learner.instance()
        self._learner.init(self)

    def is_available(self, session: AbstractSession) -> bool:
        availability: bool = len(self.get_process_list(session)) < self.max_processes

        return availability

    def assign_jobs_from_queue(self, session: AbstractSession):
        """
        Simply Register the Processes
        Not Actual Execution
        Limitation of Maximum Number of Processes are Regarded Here
        """
        while self.is_available(session) and len(self.get_queue_list(session)):
            first_queue: dict = self.__class__.get_queue_list(session)[0]
            process_key: dict = {
                'PRJ_ID': first_queue['PRJ_ID'],
                'WORK_ID': first_queue['WORK_ID'],
                'STEP': first_queue['STEP']
            }
            ProcessDAO.assign_jobs_from_queue(session, **process_key)

    @classmethod
    def get_queue_list(cls, session: AbstractSession) -> list:
        processes_dao: ProcessDAO = ProcessDAO.instance()
        queue_list: list = ProcessDAO.map(processes_dao.select_queue_list(session=session))
        return queue_list

    @classmethod
    def get_process_list(cls, session: AbstractSession) -> list:
        processes_dao: ProcessDAO = ProcessDAO.instance()
        process_list: list = ProcessDAO.map(processes_dao.select_process_list(session=session))
        return process_list

    @classmethod
    def get_status_list(cls, session: AbstractSession) -> list:
        process_dao: ProcessDAO = ProcessDAO.instance()
        status_list: list = process_dao.map(process_dao.select(session=session))
        return status_list

    @classmethod
    def get_not_executed_processes(cls, session: AbstractSession) -> list:
        """
        Fixme: No Need to Compare Two Lists Anymore
        """
        processes_list: list = cls.get_process_list(session)
        processes_current: list = cls.search_current_processes(session)
        processes_todo: list = list(filter(
            lambda info_dict: {'PRJ_ID': info_dict['PRJ_ID'],
                               'WORK_ID': info_dict['WORK_ID'],
                               'STEP': info_dict['STEP']} not in processes_current,
            processes_list
        ))

        return processes_todo

    @classmethod
    def get_canceled_processes(cls, session: AbstractSession) -> list:
        canceled_processes: list = ProcessDAO.map(
            ProcessDAO.select_canceled_process_list(session)
        )
        return canceled_processes

    @classmethod
    def get_parameter_object(cls, session: AbstractSession, prj_id: str, work_id, step: str):
        parameters_dao = ParametersDAO.instance()
        params = parameters_dao.map(
            parameters_dao.select_params_binary(session, PRJ_ID=prj_id, WORK_ID=work_id, STEP=step)
        )
        if not params:
            return None
        return params[0]['PARAM_OBJECT']

    def run_newly_assigned_processes(self, session: AbstractSession):
        """
        Todo: Fill this Function
        """
        processes_started: list = []
        processes_todo: list = self.get_not_executed_processes(session)
        for new_process_info in processes_todo:
            prj_id: str = new_process_info['PRJ_ID']
            work_id: str = new_process_info['WORK_ID']
            step: str = new_process_info['STEP']
            param_object = self.get_parameter_object(session, prj_id, work_id, step)

            params: dict = dict()
            if param_object:
                params = JsonParser.parse_blob(param_object)

            processes_started.append(
                self.run_process(session, prj_id=prj_id, work_id=work_id, step=step, **params)
            )
        return processes_started

    def cancel_processes(self, session: AbstractSession):
        """
        Todo: Fill this Function
        """
        processes_canceled: list = []
        processes_to_cancel: list = self.get_canceled_processes(session)
        for cancel_process_info in processes_to_cancel:
            prj_id: str = cancel_process_info['PRJ_ID']
            work_id: str = cancel_process_info['WORK_ID']
            step: str = cancel_process_info['STEP']
            end_time: str = cancel_process_info['DATE_END']
            pid: str = cancel_process_info['HID_PNAME']

            if end_time:
                continue

            os_signal: int = self.kill_process(int(pid))
            self.send_cancel_process(session, prj_id=prj_id, work_id=work_id, step=step)
            if os_signal == 0:
                # print(f"PID={pid} Has been Canceled")
                processes_canceled.append(
                    (self.FORM_PNAME.format(prj_id, work_id, step), pid)
                )
        return processes_canceled

    @classmethod
    def search_current_processes(cls, session: AbstractSession):
        """
        https://c0mb.tistory.com/115
        """

        current_processes: list = ProcessDAO.map(
            ProcessDAO.select_current_process_list(session)
        )

        # Searching for Zombie Process
        # current_processes: list = []
        # for proc in psutil.process_iter():
        #     try:
        #         pinfo: dict = proc.as_dict(attrs=['pid', 'name', 'create_time'])
        #         process_name = pinfo['name']
        #         process_id = pinfo['pid']
        #         process_info = self._parse_pname(process_name)
        #         if not process_info:
        #             continue
        #         current_processes.append(process_info)
        #     except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        #         raise e

        return current_processes

    def get_process_info(self):
        pass

    def run_process(self, session: AbstractSession, prj_id: str, work_id: str, step: str, **kwargs):
        """
        Should Have Already been Checked Availability Outside this Method
        """
        pname, pid = self._create_subprocess(session, prj_id, work_id, step, **kwargs)
        return pname, pid

    @classmethod
    def send_cancel_process(cls, session: AbstractSession, prj_id: str, work_id: str, step: str):

        # Remove PID from PROCESS Table in DataSource
        ProcessDAO.cancel_subprocess(session,
                                     DATE_END=DateTimeUtility.get_current_time_str(),
                                     PRJ_ID=prj_id,
                                     WORK_ID=work_id,
                                     STEP=step)

    @classmethod
    def kill_process(cls, pid: int):
        try:
            os.kill(pid, signal.SIGKILL)
            return 0
        except ProcessLookupError as e:
            print(e)    # Todo: log this
            return 1

    def receive_progression(self, msg):
        """
        processor 클래스들이 단계별 Callback 함수 내부에서 호출함으로써
        manager 에 현재 진행 상황을 보내기 위한 용도
        manager 의 입장에서는 msg 를 받는 것 (receive)
        :return:
        """
        pass

    def _create_multiprocess(self, prj_id: str, work_id: str, step: str, **kwargs):
        """
        Process Creator with Actual Callable Object
        """
        target_function: callable = self._learner.get_target_job(step)
        pname: str = self.FORM_PNAME.format(prj_id, work_id, step)
        # kwargs.update({'lock': Lock()})
        proc = Process(target=target_function, name=pname, kwargs=kwargs)
        proc.start()
        return pname, proc.pid

    def _create_subprocess(self, session: AbstractSession, prj_id: str, work_id: str, step: str, **kwargs):
        """
        Process Creator with Command-Line (calling spawn_process.py)
        """
        pname: str = self.FORM_PNAME.format(prj_id, work_id, step)
        cmd: list = ['nohup', sys.executable, os.path.join(os.path.dirname(__file__), 'spawn_process.py')]
        cmd_args: OrderedDict = OrderedDict()
        cmd_args.update({'step': step})
        for key, value in kwargs.items():
            cmd_args.update({key: value})
        for argname, val in cmd_args.items():
            cmd.extend(
                [f"--{argname.lower()}", val]
            )
        with open(self.path_std_out, 'a') as stdout, \
             open(self.path_std_err, 'a') as stderr:
            proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr,
                                    start_new_session=True)
        # proc = subprocess.Popen(cmd,
        #                         # preexec_fn=os.setpgrp,
        #                         # preexec_fn=cls._ignore_parents_signal,
        #                         start_new_session=True)
        ProcessDAO.create_subprocess(session,
                                     DATE_START=DateTimeUtility.get_current_time_str(),
                                     PID=proc.pid,
                                     PRJ_ID=prj_id,
                                     WORK_ID=work_id,
                                     STEP=step)
        return pname, proc.pid

    @classmethod
    def _ignore_parents_signal(cls):
        """
        Callable to Make Subprocess Not End with Parent Processes Signal
        """
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    def _search_process(self, prj, work, step):
        pass

    def _get_requested_pid(self, prj, work, step) -> int:
        pass

    def _get_ppid(self):
        pass

    def _parse_pname(self, pname: str):
        regex_search = re.search(self.REGEX_PNAME, pname)
        if regex_search:
            prj_id, work_id, step = regex_search.groups()
            return {'PRJ_ID': prj_id, 'WORK_ID': work_id, 'STEP': step}
        return dict()
