# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.DescribeJobModel
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper
from BatchlyApi.Models.Platform import Platform

class DescribeJobModel(object):

    """Implementation of the 'DescribeJobModel' model.

    TODO: type model description here.

    Attributes:
        platform (Platform): TODO: type description here.
        account_id (string): TODO: type description here.
        account_name (string): TODO: type description here.
        project_id (string): TODO: type description here.
        project_name (string): TODO: type description here.
        vpc_id (string): TODO: type description here.
        default_parameter_group_name (string): TODO: type description here.
        default_parameter_group_id (string): TODO: type description here.
        custom_ami (string): TODO: type description here.
        default_region (string): TODO: type description here.
        default_sla (double): TODO: type description here.
        id (string): TODO: type description here.
        name (string): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the DescribeJobModel class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    Platform -- Platform -- Sets the attribute platform
                    AccountId -- string -- Sets the attribute account_id
                    AccountName -- string -- Sets the attribute account_name
                    ProjectId -- string -- Sets the attribute project_id
                    ProjectName -- string -- Sets the attribute project_name
                    VPCId -- string -- Sets the attribute vpc_id
                    DefaultParameterGroupName -- string -- Sets the attribute default_parameter_group_name
                    DefaultParameterGroupId -- string -- Sets the attribute default_parameter_group_id
                    CustomAMI -- string -- Sets the attribute custom_ami
                    DefaultRegion -- string -- Sets the attribute default_region
                    DefaultSLA -- double -- Sets the attribute default_sla
                    Id -- string -- Sets the attribute id
                    Name -- string -- Sets the attribute name
        
        """
        # Set all of the parameters to their default values
        self.platform = None
        self.account_id = None
        self.account_name = None
        self.project_id = None
        self.project_name = None
        self.vpc_id = None
        self.default_parameter_group_name = None
        self.default_parameter_group_id = None
        self.custom_ami = None
        self.default_region = None
        self.default_sla = None
        self.id = None
        self.name = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "Platform": "platform",
            "AccountId": "account_id",
            "AccountName": "account_name",
            "ProjectId": "project_id",
            "ProjectName": "project_name",
            "VPCId": "vpc_id",
            "DefaultParameterGroupName": "default_parameter_group_name",
            "DefaultParameterGroupId": "default_parameter_group_id",
            "CustomAMI": "custom_ami",
            "DefaultRegion": "default_region",
            "DefaultSLA": "default_sla",
            "Id": "id",
            "Name": "name",
        }

        # Parse all of the Key-Value arguments
        if kwargs is not None:
            for key in kwargs:
                # Only add arguments that are actually part of this object
                if key in replace_names:
                    setattr(self, replace_names[key], kwargs[key])

            # Other objects also need to be initialised properly
            if "Platform" in kwargs:
                self.platform = Platform.from_string(kwargs["Platform"])

    def resolve_names(self):
        """Creates a dictionary representation of this object.
        
        This method converts an object to a dictionary that represents the
        format that the model should be in when passed into an API Request.
        Because of this, the generated dictionary may have different
        property names to that of the model itself.
        
        Returns:
            dict: The dictionary representing the object.
        
        """
        # Create a mapping from Model property names to API property names
        replace_names = {
            "platform": "Platform",
            "account_id": "AccountId",
            "account_name": "AccountName",
            "project_id": "ProjectId",
            "project_name": "ProjectName",
            "vpc_id": "VPCId",
            "default_parameter_group_name": "DefaultParameterGroupName",
            "default_parameter_group_id": "DefaultParameterGroupId",
            "custom_ami": "CustomAMI",
            "default_region": "DefaultRegion",
            "default_sla": "DefaultSLA",
            "id": "Id",
            "name": "Name",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)