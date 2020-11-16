# -*- coding: utf-8 -*-

from flask import Flask, request, send_file
import json

from .common import SingletonInstance
from .configs import ApplicationConfiguration
from .dao import AbstractSession, OracleDataSource
from .manager import ProcessManager


class WebApplication(SingletonInstance):
    """
    Web Application
    """

    def __init__(self):
        self.process_manager = None     # type: ProcessManager
        self.app = None                 # type: Flask
        self.static_url: str = ''
        self.host: str = ''
        self.port: int = 0
        self._url_list_queue: str = ''
        self._url_list_processes: str = ''
        self._url_is_available: str = ''
        self._url_proc_start: str = ''
        self._url_proc_kill: str = ''

    def init(self, config: ApplicationConfiguration):

        # ./configs/config.properties  로부터 [Server] 섹션 설정값들 불러오기
        server_info = dict(config.find_section('Server'))
        url_info = dict(config.find_section('Router'))

        # 인스턴스 변수 초기화
        self.static_url = server_info.get('app.static_url')
        self.host = server_info.get('app.host')
        self.port = server_info.get('app.port')
        self._url_list_queue = url_info.get('app.queue')
        self._url_list_processes = url_info.get('app.proc.list')
        self._url_proc_start = url_info.get('app.proc.start')
        self._url_proc_kill = url_info.get('app.proc.kill')

        # 요청을 처리하기 위한 ProcessManager 인스턴스 초기화
        self.process_manager = ProcessManager.instance()
        self.process_manager.init(config)

        # 요청을 받아오기 위한 웹 App 초기화
        self.app = Flask(__name__, static_url_path=self.static_url)

        # ================================== #
        #             웹 App 정의             #
        # ================================== #

        # 0. 작업 대기열 조회 요청 URL 에 대한 동작 정의
        @self.app.route(self._url_list_queue)
        def get_queue_list():
            data_source: OracleDataSource = OracleDataSource.instance()
            session: AbstractSession = data_source.get_session()
            queue_list = self.process_manager.get_queue_list(session)
            session.close()
            return json.dumps(queue_list)

        # 0. 작업 목록 조회 요청 URL 에 대한 동작 정의
        @self.app.route(self._url_list_processes)
        def get_process_list():
            data_source: OracleDataSource = OracleDataSource.instance()
            session: AbstractSession = data_source.get_session()
            process_list = self.process_manager.get_process_list(session)
            session.close()
            return json.dumps(process_list)

        # 1. start 요청 URL 에 대한 동작 정의
        @self.app.route(self._url_proc_start)
        def start(prj: str, work: str, step: str):
            return self.process_manager.run_process(prj, work, step)

        # 2. kill 요청 URL 에 대한 동작 정의
        @self.app.route(self._url_proc_kill)
        def kill(prj: str, work: str, step: str):
            return self.process_manager.kill_process(prj, work, step)

    def launch(self):
        self.app.run(host=self.host, port=self.port)
