# -*- coding: utf-8 -*-

"""
BatchlyApi

This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""

class OperatingSystem(object):

    """Implementation of the 'OperatingSystem' enum.

    TODO: type enum description here.

    Attributes:
        NONE: TODO: type description here.
        WINDOWS: TODO: type description here.
        UBUNTU: TODO: type description here.
        CENTOS: TODO: type description here.
        RHEL: TODO: type description here.

    """

    NONE = "None"

    WINDOWS = "Windows"

    UBUNTU = "Ubuntu"

    CENTOS = "CentOS"

    RHEL = "RHEL"


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