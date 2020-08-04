# -*- coding: utf-8 -*-

from ..common import SingletonInstance


class JsonParser(SingletonInstance):

    @classmethod
    def parse_blob(cls, blob):
        """
        # Todo: Make BLOB Object Parser
        Parse Oracle BLOB Object
        and RETURNS Dictionary
        """
        return blob
