from ..common import SingletonInstance
from . import AbstractDAO, AbstractSession


class ProcessDAO(AbstractDAO, SingletonInstance):
    """
    Demand Data Access Object
    """

    def select(self, session: AbstractSession, **params):
        """
        Query the Entire Situation
        """
        return session.select("SELECT * "
                              "FROM DLP_PRJT_PIPELN "
                              "ORDER BY RGST_DT_TM", params)

    def select_one(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 1개 데이터를 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        pass

    @classmethod
    def select_queue_list(cls, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 list 데이터 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        return session.select("SELECT * "
                              "FROM DLP_PRJT_PIPELN "
                              "WHERE OP_CD = 'QUEUE' "
                              "ORDER BY RGST_DT_TM", params)

    @classmethod
    def select_process_list(cls, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 list 데이터 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        return session.select("SELECT * "
                              "FROM DLP_PRJT_PIPELN "
                              "WHERE OP_CD = 'RUNNING' "
                              "ORDER BY RGST_DT_TM", params)

    @classmethod
    def select_current_process_list(cls, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 list 데이터 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        return session.select("SELECT MDL_ID, PRJT_ID, PIPELN_ID "
                              "FROM DLP_PRJT_PIPELN "
                              "WHERE BAT_OP_ID IS NOT NULL "
                              "ORDER BY RGST_DT_TM", params)

    @classmethod
    def select_canceled_process_list(cls, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 list 데이터 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        return session.select("SELECT * "
                              "FROM DLP_PRJT_PIPELN "
                              "WHERE OP_CD = 'CANCELED' "
                              "ORDER BY RGST_DT_TM", params)

    @classmethod
    def select_pipeline_definition(cls, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source 로부터 현재 모델에 대한 파이프라인 정의를 조회
        :param session:
        :param params:
        :return:
        """
        return session.select("SELECT * "
                              "FROM DLP_PIPELN "
                              "WHERE MDL_ID = :MDL_ID "
                              "ORDER BY PIPELN_ID", params)

    @classmethod
    def assign_jobs_from_queue(cls, session: AbstractSession, **params):
        return session.execute("UPDATE DLP_PRJT_PIPELN "
                               "SET OP_CD = 'RUNNING' "
                               "WHERE MDL_ID = :MDL_ID "
                               "AND PRJT_ID = :PRJT_ID "
                               "AND PIPELN_ID = :PIPELN_ID", **params)

    @classmethod
    def create_subprocess(cls, session: AbstractSession, **params):
        return session.execute("UPDATE DLP_PRJT_PIPELN "
                               "SET (BAT_OP_ID, START_DT_TM) = "
                               "( SELECT :PID AS PID"
                               "       , :DATE_START AS START_DT_TM"
                               "  FROM DUAL)"
                               "WHERE MDL_ID = :MDL_ID "
                               "AND PRJT_ID = :PRJT_ID "
                               "AND PIPELN_ID = :PIPELN_ID ", **params)

    @classmethod
    def finish_subprocess(cls, session: AbstractSession, **params):
        return session.execute("UPDATE DLP_PRJT_PIPELN "
                               "SET (CMPLT_YN, OP_CD, BAT_OP_ID, END_DT_TM) = "
                               "( SELECT 'Y' AS CMPLT_YN"
                               "       , 'FINISHED' AS OP_CD"
                               "       , NULL AS PID"
                               "       , :END_DT_TM AS END_DT"
                               "  FROM DUAL)"
                               "WHERE MDL_ID = :MDL_ID "
                               "AND PRJT_ID = :PRJT_ID "
                               "AND PIPELN_ID = :PIPELN_ID", **params)

    @classmethod
    def cancel_subprocess(cls, session: AbstractSession, **params):
        return session.execute("UPDATE DLP_PRJT_PIPELN "
                               "SET (BAT_OP_ID, END_DT_TM) = "
                               "( SELECT NULL AS PID"
                               "       , :END_DT_TM AS END_DT"
                               "  FROM DUAL)"
                               "WHERE MDL_ID = :MDL_ID "
                               "AND PRJT_ID = :PRJT_ID "
                               "AND PIPELN_ID = :PIPELN_ID", **params)

    def execute(self, session: AbstractSession, sql_template: str, data_list: list):
        """
        세션 인스턴스를 통해 Data Source에 대한 CUD를 실행
        :param session: AbstractSession 인스턴스
        :param sql_template: sql template string
        :param data_list: CUD 대상 데이터
        :return: True/False
        """
        session.execute(sql_template, data_list)
