from ..common import SingletonInstance
from ..dao import AbstractSession, QueueDAO
from ..processor import Launcher
from .. import ApplicationConfiguration


class ProcessManager(SingletonInstance):
    """

    """

    def __init__(self):
        self.max_processes: int = 1
        self.launcher: Launcher = None

    def init(self, config: ApplicationConfiguration):
        self.launcher = Launcher()
        self.launcher.init(config)

    def is_available(self) -> bool:
        pass

    def get_queue_list(self, session: AbstractSession):
        queue_dao: QueueDAO = QueueDAO.instance()
        queue_list = QueueDAO.map(queue_dao.select_queue_list(session=session))
        print(queue_list)
        return queue_list

    def get_process_list(self):
        pass

    def get_process_info(self):
        pass

    def start_process(self, step, params):
        log_msg: str = f"REQUEST - start {step} / {params}"
        print(log_msg)
        return log_msg

    def kill_process(self, prj_id, work_id, step):
        log_msg: str = f"REQUEST - kill {prj_id} / {work_id} / {step}"
        print(log_msg)
        return log_msg

    def _send_progression(self):
        """

        :return:
        """
        pass

    def receive_progression(self, msg):
        """
        processor 클래스들이 단계별 Callback 함수 내부에서 호출함으로써
        manager 에 현재 진행 상황을 보내기 위한 용도
        manager 의 입장에서는 msg 를 받는 것 (receive)
        :return:
        """
        pass

    def _get_pid(self):
        pass

    def _get_ppid(self):
        pass
