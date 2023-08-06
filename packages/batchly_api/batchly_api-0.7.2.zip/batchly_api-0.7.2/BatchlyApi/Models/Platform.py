# -*- coding: utf-8 -*-

"""
BatchlyApi

This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""

class Platform(object):

    """Implementation of the 'Platform' enum.

    TODO: type enum description here.

    Attributes:
        AMAZONS3: TODO: type description here.
        AMAZONWEBSERVICES: TODO: type description here.
        BOX: TODO: type description here.
        GOOGLECOMPUTEENGINE: TODO: type description here.
        MICROSOFTAZURE: TODO: type description here.
        NONE: TODO: type description here.
        PORTICOR: TODO: type description here.

    """

    AMAZONS3 = "AmazonS3"

    AMAZONWEBSERVICES = "AmazonWebServices"

    BOX = "Box"

    GOOGLECOMPUTEENGINE = "GoogleComputeEngine"

    MICROSOFTAZURE = "MicrosoftAzure"

    NONE = "None"

    PORTICOR = "Porticor"


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