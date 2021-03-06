# -*- coding: utf-8 -*-


from ..common import SingletonInstance
from . import AbstractDAO, AbstractSession


class ParametersDAO(AbstractDAO, SingletonInstance):
    """
    Demand Data Access Object
    """

    def select(self, session: AbstractSession, **params):
        """
        Query the Entire Situation
        """
        return session.select("SELECT * "
                              "FROM DLP_PRJT_PIPELN_PARAM ", params)

    def select_one(self, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 1개 데이터를 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        pass

    @classmethod
    def select_params_setting(cls, session: AbstractSession, **params):
        """
        세션 인스턴스를 통해 Data Source로 부터 list 데이터 조회
        :param session: AbstractSession Instance
        :param params: SQL Parameter Data
        :return: {"columns" : columns, "data" : list}
        """
        return session.select("SELECT * "
                              "FROM DLP_PRJT_PIPELN_PARAM "
                              "WHERE MDL_ID = :MDL_ID "
                              "AND PRJT_ID = :PRJT_ID "
                              "AND PIPELN_ID = :PIPELN_ID ", params)

    def execute(self, session: AbstractSession, sql_template: str, data_list: list):
        """
        세션 인스턴스를 통해 Data Source에 대한 CUD를 실행
        :param session: AbstractSession 인스턴스
        :param sql_template: sql template string
        :param data_list: CUD 대상 데이터
        :return: True/False
        """
        session.execute(sql_template, data_list)
