# -*- coding: utf-8 -*-

"""
   BatchlyApi.Models.CreateJobRequest
 
   This file was automatically generated for batchly_api by APIMATIC BETA v2.0 on 02/18/2016
"""
from BatchlyApi.APIHelper import APIHelper

class CreateJobRequest(object):

    """Implementation of the 'CreateJobRequest' model.

    TODO: type model description here.

    Attributes:
        name (string): TODO: type description here.
        project_id (string): TODO: type description here.
        processor_id (string): TODO: type description here.
        data_source_id (string): TODO: type description here.
        parameter_group_id (string): TODO: type description here.
        destination_id (string): TODO: type description here.
        region (string): TODO: type description here.
        sla (double): TODO: type description here.

    """

    def __init__(self,
                 **kwargs):
        """Constructor for the CreateJobRequest class
        
        Args:
            **kwargs: Keyword Arguments in order to initialise the
                object. Any of the attributes in this object are able to
                be set through the **kwargs of the constructor. The values
                that can be supplied and their types are as follows::

                    Name -- string -- Sets the attribute name
                    ProjectId -- string -- Sets the attribute project_id
                    ProcessorId -- string -- Sets the attribute processor_id
                    DataSourceId -- string -- Sets the attribute data_source_id
                    ParameterGroupId -- string -- Sets the attribute parameter_group_id
                    DestinationId -- string -- Sets the attribute destination_id
                    Region -- string -- Sets the attribute region
                    SLA -- double -- Sets the attribute sla
        
        """
        # Set all of the parameters to their default values
        self.name = None
        self.project_id = None
        self.processor_id = None
        self.data_source_id = None
        self.parameter_group_id = None
        self.destination_id = None
        self.region = None
        self.sla = None

        # Create a mapping from API property names to Model property names
        replace_names = {
            "Name": "name",
            "ProjectId": "project_id",
            "ProcessorId": "processor_id",
            "DataSourceId": "data_source_id",
            "ParameterGroupId": "parameter_group_id",
            "DestinationId": "destination_id",
            "Region": "region",
            "SLA": "sla",
        }

        # Parse all of the Key-Value arguments
        if kwargs is not None:
            for key in kwargs:
                # Only add arguments that are actually part of this object
                if key in replace_names:
                    setattr(self, replace_names[key], kwargs[key])

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
            "name": "Name",
            "project_id": "ProjectId",
            "processor_id": "ProcessorId",
            "data_source_id": "DataSourceId",
            "parameter_group_id": "ParameterGroupId",
            "destination_id": "DestinationId",
            "region": "Region",
            "sla": "SLA",
        }

        retval = dict()

        return APIHelper.resolve_names(self, replace_names, retval)