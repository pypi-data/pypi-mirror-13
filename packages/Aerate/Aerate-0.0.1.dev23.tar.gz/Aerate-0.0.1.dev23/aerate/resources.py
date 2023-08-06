# -*- coding: utf-8 -*-
"""
    aerate.resources
    ~~~~~~~~~~~~~~~~
    Implements ResourceCollection and ResourceItem for use in
    defining Falcon routes.

    The ResourceItem must be subclassed in a user's application

    :copyright: (c) 2016 by Kelly Caylor.
    :license: BSD, see LICENSE for more details.
"""
from aerate.config import config
import aerate.validate as v
from aerate.utils import log
METHODS = ['on_get', 'on_post', 'on_put', 'on_delete', 'on_patch', 'on_head']
VERBS = ['get', 'put', 'post', 'delete', 'patch', 'head']
METHOD_ARGS = set(['req', 'resp'])


class Resource(object):

    def __init__(
            self,
            definition=None,
            datasource=None,
            id_field=None,
            schema=None,
            **kwargs):

        """ Initializes a resource object for use in Aerate.

        Resource objects represent entities that exist in the data layer of the
        API. Generally, each resource in the API should be defined in the
        swagger spec in the `definitions` portion of the spec. This spec-level
        definition is then used to validate resource requests to ensure
        that the request objects conform to the API specification.

        Resources will usually map to discrete collections or tables in the
        database engine.

        Static resources should not be added to the API using Resource objects,
        since these resources do not contain either swagger definitions or
        representations on the database.

        param:definition: REQUIRED. This is the name of the resource as
            defined in the swagger spec. For example, in the Swagger
            API petstore example, the definition of a PetItem or
            PetCollection would be 'Pet'

        param:datasource: REQUIRED. This is the name of the collection or
            table that stores resource objects inside the datalayer.

        param:id_field: The record field corresponding to id-based lookups.
            This field is used in the find_one implementation of datalayers,
            allowing direct querying of a resource item using the unique id
            of the resource.

        param:schema: Schema definition of resource. Generally, this should
            be set when a resource is bound to the API, using the definition
            provided in the swagger spec.

        """
        self.id_field = id_field or config.ID_FIELD
        self.definition = definition
        for arg in kwargs.keys():
            setattr(self, arg, kwargs[arg])
        # Prevent user overloading of methods
        self.methods = []
        self.schema = schema
        # Initialize with passed hanlder functions.
        # These functions must be of the form:
        #  f(self, req, resp, **kwargs)
        self.datasource = datasource
        # Define default validators for PUT, POST, and PATCH.
        # These will be over-written by any resource-level definitions
        self.validate_on_post = self._default_POST_validator
        self.validate_on_put = self._default_POST_validator
        self.validate_on_patch = self._default_PATCH_validator
        # Initialize the validation and authorization dictionaries for
        # the resource.
        # TODO: Allow these to be updated with passed in validation and
        # authorization functions during resource instantiation.
        self.val_dict = {}
        self.auth_dict = {}
        for method in METHODS:
            val_fun = 'validate_' + method
            auth_fun = 'authorize_' + method
            verb = method.split('on_')[-1].upper()
            self.val_dict[verb] = getattr(self, val_fun)
            self.auth_dict[verb] = getattr(self, auth_fun)

    def authorize(self, method):
        log.info("called authorize in {0} with {1}".format(
            self.__class__, method.upper()))
        auth_fun = 'authorize_on_' + method.lower()
        return getattr(self, auth_fun)

    def validate(self, method):
        log.info("called validate in {0} with {1}".format(
            self.__class__, method.upper()))
        val_fun = 'validate_on_' + method.lower()
        return getattr(self, val_fun)

    def filter(self, req, resp, **kwargs):
        """ Filters response objects based on spec-level flags.
        Filter works in a similar fashion as validate; checking object
        fields to confirm that they are defined in the spec, and that
        they are not marked private (x-aerate-private) in the spec before
        returning response objects.
        """
        pass

    def authorize_on_get(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific rules
        that update req.context with method-specific authorization results
        """
        pass

    def authorize_on_post(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific rules
        that update req.context with method-specific authorization results
        """
        pass

    def authorize_on_patch(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific rules
        that update req.context with method-specific authorization results
        """
        pass

    def authorize_on_put(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific rules
        that update req.context with method-specific authorization results
        """
        pass

    def authorize_on_delete(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific rules
        that update req.context with method-specific authorization results
        """
        pass

    def authorize_on_head(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific rules
        that update req.context with method-specific authorization results
        """
        pass

    # Validation functions. Should be over-written as needed by
    # resource-specific implementations.
    def validate_on_get(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific validation rules.
        Returns True if the object is validated successfully, or raises a
        ValidationError if not.
        """
        return True

    def validate_on_delete(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific validation rules.
        Returns True if the object is validated successfully, or raises a
        ValidationError if not.
        """
        return True

    def validate_on_head(self, req, resp, **kwargs):
        """
        Should be defined in resource with app-specific validation rules.
        Returns True if the object is validated successfully, or raises a
        ValidationError if not.
        """
        return True

    # def on_get(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_post(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_put(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_delete(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def on_patch(self, req, resp, **kwargs):
    #     raise falcon.HTTPMethodNotAllowed

    # def _set_definition(self):
    #     return self.get_datasource().title()

    # def get_datasource(self):
    #     import re
    #     match = re.match('^.*(?=Item|Collection)', self.name())
    #     if match:
    #         return match.group(0).lower()
    #     else:
    #         return self.name().lower()

    def name(self):
        return self.__class__.__name__

    def valid_methods(self):
        return self._valid_methods(METHODS)

    def valid_operationIds(self):
        return list(
            [str(self.name() + '_' + method) for
                method in self.valid_methods()]
        )

    def _valid_methods(self, m):
        valid = []
        for method in m:
            if getattr(self, method, None):
                valid.append(method)
        return valid

    def _validate_function_args(self, op):
        if not op:
            raise ValueError(
                'No operation to validate {0}'.format(self.name()))
        else:
            return True

    def _default_POST_validator(self, req, resp, **kwargs):
        """
            Default Aerate validation for POST and PUT requests

        """
        return (
            v.validate_object(self.schema, *req.context['json'])
        )

    def _default_PATCH_validator(self, req, resp, **kwargs):

        return (
            v.validate_partial_object(self.schema, *req.context['json'])
        )


class ResourceCollection(Resource):

    def __init__(self, **kwargs):
        super(ResourceCollection, self).__init__(**kwargs)
        self.type = 'Collection'


class ResourceItem(Resource):

    def __init__(self, **kwargs):
        super(ResourceItem, self).__init__(**kwargs)
        self.type = 'Item'


class MediaResourceCollection(ResourceCollection):

    def __init__(self, **kwargs):
        super(MediaResourceCollection, self).__init__(**kwargs)


class MediaResourceItem(ResourceItem):

    def __init__(self, **kwargs):
        super(MediaResourceItem, self).__init__(**kwargs)
