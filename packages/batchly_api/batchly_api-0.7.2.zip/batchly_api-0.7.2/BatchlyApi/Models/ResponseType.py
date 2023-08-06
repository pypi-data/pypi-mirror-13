# -*- coding: utf-8 -*-

"""
BatchlyApi

This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""

class ResponseType(object):

    """Implementation of the 'ResponseType' enum.

    TODO: type enum description here.

    Attributes:
        DB: TODO: type description here.
        DEFAULT: TODO: type description here.
        FILE: TODO: type description here.
        NONE: TODO: type description here.

    """

    DB = "Db"

    DEFAULT = "Default"

    FILE = "File"

    NONE = "None"


    @classmethod
    def to_string(cls, val):
        """Returns the string equivalent for the Enum.

        """
        for k,v in vars(cls).iteritems():
            if v==val:
                return k

    @classmethod
    def from_string(cls, str):
        """Creates an instance of the Enum from a given string.

        """
        return getattr(cls, str.upper(), None)