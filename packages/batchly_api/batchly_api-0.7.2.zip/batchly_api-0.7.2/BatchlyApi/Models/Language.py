# -*- coding: utf-8 -*-

"""
BatchlyApi

This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""

class Language(object):

    """Implementation of the 'Language' enum.

    TODO: type enum description here.

    Attributes:
        NONE: TODO: type description here.
        DOTNET: TODO: type description here.
        MONO: TODO: type description here.
        JAVA: TODO: type description here.
        PYTHON: TODO: type description here.
        PHP: TODO: type description here.
        RUBY: TODO: type description here.

    """

    NONE = "None"

    DOTNET = "DotNet"

    MONO = "Mono"

    JAVA = "Java"

    PYTHON = "Python"

    PHP = "PHP"

    RUBY = "Ruby"


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