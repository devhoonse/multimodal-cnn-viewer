# -*- coding: utf-8 -*-

from ..common import SingletonInstance
from ..configs import ApplicationConfiguration
from ..dao import AbstractSession, ProcessDAO, ParametersDAO, DataPathDAO
from ..utils import JsonParser, DateTimeHandler, OSHandler, ArgParser
from ..processor import Learner

import os
import sys
import datetime
import signal
# import psutil   # Fixme: 3rd-Party Dependency
import re
import subprocess
import json
from multiprocessing import Process, Lock
from collections import OrderedDict


class ProcessManager(SingletonInstance):
    """
    Available for Both of WebApp and Cron-Process-Monitor
    """

    REGEX_PNAME: str = r'^LEARNER[:][<](.*)[>][_][<](.*)[>]_[<](.*)[>]'
    FORM_PNAME: str = 'LEARNER:<{}>_<{}>_<{}>'

    def __init__(self):
        self._process_info: dict = dict()
        self.max_processes: int = 1
        self.path_std_out: str = ''
        self.path_std_err: str = ''
        self._arg_parser: ArgParser = None
        self._learner: Learner = None

    def init(self, config: ApplicationConfiguration):

        with open(config.find('Process', 'procs.json'), encoding="UTF-8") as json_file:
            self._process_info = json.loads(json_file.read())

        self.max_processes = int(config.find('Server', 'process.max'))
        self.path_std_out = config.find('Logging', 'std.out')
        self.path_std_err = config.find('Logging', 'std.err')
        self._arg_parser = ArgParser.instance().init(config)

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
                'MDL_ID': first_queue['MDL_ID'],
                'PRJT_ID': first_queue['PRJT_ID'],
                'PIPELN_ID': first_queue['PIPELN_ID']
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
            lambda info_dict: {'MDL_ID': info_dict['MDL_ID'],
                               'PRJT_ID': info_dict['PRJT_ID'],
                               'PIPELN_ID': info_dict['PIPELN_ID']} not in processes_current,
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
    def get_parameter_setting(cls, session: AbstractSession, mdl_id: str, prjt_id: str, pipeln_id: str):
        parameters_dao = ParametersDAO.instance()
        params = parameters_dao.map(
            parameters_dao.select_params_setting(session, MDL_ID=mdl_id, PRJT_ID=prjt_id, PIPELN_ID=pipeln_id)
        )
        return params

    def run_newly_assigned_processes(self, session: AbstractSession):
        """
        Todo: Fill this Function
        """
        processes_started: list = []
        processes_todo: list = self.get_not_executed_processes(session)
        for new_process_info in processes_todo:
            mdl_id: str = new_process_info['MDL_ID']
            prjt_id: str = new_process_info['PRJT_ID']
            pipeln_id: str = new_process_info['PIPELN_ID']
            bat_op_yn: str = new_process_info['BAT_OP_YN']

            params = self.get_parameter_setting(session, mdl_id, prjt_id, pipeln_id)

            # params: dict = dict()
            # if param_object:
            #     params = JsonParser.parse_blob(param_object)

            processes_started.append(
                self.run_process(session, mdl_id, prjt_id, pipeln_id, bat_op_yn, params)
            )
        return processes_started

    def cancel_processes(self, session: AbstractSession):
        """
        Todo: Fill this Function
        """
        processes_canceled: list = []
        processes_to_cancel: list = self.get_canceled_processes(session)
        for cancel_process_info in processes_to_cancel:
            mdl_id: str = cancel_process_info['MDL_ID']
            prjt_id: str = cancel_process_info['PRJT_ID']
            pipeln_id: str = cancel_process_info['PIPELN_ID']
            end_time: str = cancel_process_info['END_DT_TM']
            pid: str = cancel_process_info['BAT_OP_ID']

            if end_time:    # end time 이 기록되어 있단 건, 이미 종료되었다는 것
                continue

            if not pid:     # end time 이 기록되었는데 pid 필드 값이 날아가고 없는 경우 - 정합성 위배 -> 로깅
                continue

            os_signal: int = self.kill_process(int(pid))
            self.send_cancel_process(session, mdl_id=mdl_id, prjt_id=prjt_id, pipeln_id=pipeln_id)
            if os_signal == 0:
                # print(f"PID={pid} Has been Canceled")
                processes_canceled.append(
                    (self.FORM_PNAME.format(mdl_id, prjt_id, pipeln_id), pid)
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

        # Searching for Zombies
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

    def run_process(self, session: AbstractSession, mdl_id: str, prjt_id: str, pipeln_id: str, bat_op_yn: str, params: list):
        """
        Should Have Already been Checked Availability Outside this Method
        """
        pname, pid = self._create_subprocess(session, mdl_id, prjt_id, pipeln_id, bat_op_yn, params)
        return pname, pid

    @classmethod
    def send_cancel_process(cls, session: AbstractSession, mdl_id: str, prjt_id: str, pipeln_id: str):

        # Remove PID from PROCESS Table in DataSource
        ProcessDAO.cancel_subprocess(session,
                                     END_DT_TM=DateTimeHandler.get_current_time_str(),
                                     MDL_ID=mdl_id,
                                     PRJT_ID=prjt_id,
                                     PIPELN_ID=pipeln_id)

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

    def _create_subprocess(self, session: AbstractSession,
                           mdl_id: str, prjt_id: str, pipeln_id: str, bat_op_yn: str, params: list):
        """
        Process Creator with Command-Line (calling process_generator.py)
        """
        pname: str = self.FORM_PNAME.format(mdl_id, prjt_id, pipeln_id)
        # job_info: dict = {'MDL_ID': mdl_id, 'PIPELN_ID': pipeln_id}

        src_path: str = self._process_info[mdl_id][pipeln_id]["src"]

        info_args: dict = {
            "mdl_id": mdl_id,
            "prjt_id": prjt_id,
            "pipeln_id": pipeln_id
        }

        dir_args: dict = self._process_info[mdl_id][pipeln_id]["dir_args"]
        dir_args = dict(
            zip(
                dir_args.keys(),
                map(lambda dir_path: os.path.join(dir_path, prjt_id), dir_args.values())
            )
        )

        log_stdout: str = os.path.join(self.path_std_out, mdl_id, pipeln_id, prjt_id, 'logs', 'stdout.txt')
        log_stderr: str = os.path.join(self.path_std_err, mdl_id, pipeln_id, prjt_id, 'logs', 'stderr.txt')

        cmd: list = ['nohup', sys.executable, '-u', src_path]

        cmd_args: OrderedDict = OrderedDict()
        cmd_args.update(info_args)
        cmd_args.update(dir_args)
        for param in params:
            cmd_args.update({param["PARAM_NM"]: param["PARAM_VAL"]})
        for argname, val in cmd_args.items():
            cmd.extend(
                [f"--{argname.lower()}", val]
            )
        # cmd.extend(['&'])

        OSHandler.create_directory(log_stdout, is_directory=False)
        OSHandler.create_directory(log_stderr, is_directory=False)
        with open(log_stdout, 'a') as stdout, \
             open(log_stderr, 'a') as stderr:
            pid = 'istream'
            if bat_op_yn == "Y":
                proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr,
                                        # )
                                        start_new_session=True)
                # ret = proc.communicate()    # for debugging
                pid = proc.pid
            ProcessDAO.create_subprocess(session,
                                         DATE_START=DateTimeHandler.get_current_time_str(),
                                         PID=pid,
                                         MDL_ID=mdl_id,
                                         PRJT_ID=prjt_id,
                                         PIPELN_ID=pipeln_id)
        return pname, pid

    def _get_prior_pipeln_id(self, mdl_id, pipeln_id, session):
        """
        이전 단계 파이프라인 명칭 파악을 위한 내부 메서드
        :param mdl_id:
        :param pipeln_id:
        :param session:
        :return:
        """

        process_dao = ProcessDAO.instance()
        pipeln_definition: list = ProcessDAO.map(process_dao.select_pipeline_definition(session, MDL_ID=mdl_id))
        current_model_pipelns = [row['PIPELN_ID'] for row in pipeln_definition]

        prior_pipeln_idx = current_model_pipelns.index(pipeln_id) - 1

        prior_pipeln_id = ''
        if prior_pipeln_idx > -1:
            prior_pipeln_id = current_model_pipelns[prior_pipeln_idx]

        return prior_pipeln_id

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
