# -*- coding: utf-8 -*-

"""
BatchlyApi

This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""

class RequestType(object):

    """Implementation of the 'RequestType' enum.

    TODO: type enum description here.

    Attributes:
        CSV: TODO: type description here.
        DB: TODO: type description here.
        FILE: TODO: type description here.
        NONE: TODO: type description here.
        QUEUE: TODO: type description here.

    """

    CSV = "CSV"

    DB = "Db"

    FILE = "File"

    NONE = "None"

    QUEUE = "Queue"


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