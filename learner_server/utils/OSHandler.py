# -*- coding: utf-8 -*-


import os

from ..configs import ApplicationConfiguration


class OSHandler:
    """
    OS Utility
    시간 관련 처리를 위한 유틸리티성 static 메서드들을 정의
    """

    @classmethod
    def create_directory(cls, file_path: str):
        """
        주어진 file_path 를 저장하기 위해
        저장될 폴더가 없다면 만들어 주는 처리
        """
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
