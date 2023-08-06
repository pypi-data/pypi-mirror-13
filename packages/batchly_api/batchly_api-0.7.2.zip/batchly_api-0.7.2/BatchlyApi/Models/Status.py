# -*- coding: utf-8 -*-

"""
BatchlyApi

This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""

class Status(object):

    """Implementation of the 'Status' enum.

    TODO: type enum description here.

    Attributes:
        NONE: TODO: type description here.
        STARTING: TODO: type description here.
        BROKERING: TODO: type description here.
        PROCESSING: TODO: type description here.
        CLEANING: TODO: type description here.
        SUMMARY: TODO: type description here.
        COMPLETE: TODO: type description here.
        ERROR: TODO: type description here.
        TERMINATED: TODO: type description here.
        SCHEDULECONFLICT: TODO: type description here.
        PAUSED: TODO: type description here.

    """

    NONE = "None"

    STARTING = "Starting"

    BROKERING = "Brokering"

    PROCESSING = "Processing"

    CLEANING = "Cleaning"

    SUMMARY = "Summary"

    COMPLETE = "Complete"

    ERROR = "Error"

    TERMINATED = "Terminated"

    SCHEDULECONFLICT = "ScheduleConflict"

    PAUSED = "Paused"


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