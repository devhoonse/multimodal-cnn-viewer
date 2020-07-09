from flask import Flask, send_file

from .common import SingletonInstance
from .manager import ProcessManager


class WebApplication(SingletonInstance):
    """
    Web Application
    """

    def __init__(self):
        self.process_manager = None
        self.app = None
        self.static_url: str = ''
        self.host: str = ''
        self.port: int = 0

    def init(self, static_url: str, host: str, port: int):

        # 인스턴스 변수 초기화
        self.static_url = static_url
        self.host = host
        self.port = port

        # 요청을 처리하기 위한 ProcessManager 인스턴스 초기화
        self.process_manager = ProcessManager.instance()
        self.process_manager.init()

        # 요청을 받아오기 위한 웹 App 초기화
        self.app = Flask(__name__, static_url_path=self.static_url)

        # 웹 App 정의
        # 0. 작업 대기열 조회 요청 URL 구조
        @self.app.route('/query/queue')
        def start():
            return self.process_manager.get_queue_list()

        # 1. 신규 작업 할당 가능 여부 조회 요청 URL 구조
        @self.app.route('/query/availability')
        def is_available():
            return self.process_manager.is_available()

        # 2. start 요청 URL 구조
        @self.app.route('/start/step=<string:step>/params=<string:params>')
        def start(step, params):
            return self.process_manager.start_process(step, params)

        # 3. kill 요청 URL 구조
        @self.app.route('/kill/prj_id=<string:prj_id>/work_id=<string:work_id>/step=<string:step>')
        def kill(prj_id, work_id, step):
            return self.process_manager.kill_process(prj_id, work_id, step)

    def launch(self):
        self.app.run(host=self.host, port=self.port)
