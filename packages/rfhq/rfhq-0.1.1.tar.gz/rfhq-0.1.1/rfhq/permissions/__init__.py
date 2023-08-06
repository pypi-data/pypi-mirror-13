# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

from restfw_composed_permissions.generic.components import BaseComposedPermision as BaseComposedPermission
from .components import (
    Deny, Allow, IsInternalClient, IsExternalClient, IsActingAsUser, IsActingAsClient, HasScopes, IsNested,
    IsReadOnly, IsAction, ObjectAttrEqualToObjectAttr, ObjectAttrInObjectAttr, ObjectAttrRelatedToObject,
    HasActiveAppSubscription, HasActiveAPISubscription
)


class InternalPermissions(BaseComposedPermission):
    """
    Default permissions for endpoints that are for internal use only

    """
    def global_permission_set(self):
        return IsInternalClient()

    def object_permission_set(self):
        return Allow()


class MixedPermissions(BaseComposedPermission):
    """
    Composed permissions that add default criteria based on whether a request is internal or external, from a user or a client

    Every access to a resource goes through this process:

        - check global_permission_set
            - if internal client: check internal_permission_set
            - if external client: check external_permission_set
            - if acting as user (App access): check active app plan and user_permissions_set
            - if acting as client (API access): check active api plan and client_permission_set
                - if internal client: check internal_client_permission_set
                - if external client: check external_client_permission_set

        - if object access: check object_permission_set
            - if internal client: check internal_object_permission_set
            - if external client: check external_object_permission_set
            - if acting as user (App access): check user_object_permissions_set
            - if acting as client (API access): check client_object_permission_set
                - if internal client: check internal_object_client_permission_set
                - if external client: check external_object_client_permission_set

    It's important to note that:

        * All internal permission sets return Allow by default
        * All external permission sets return Deny by default
        * Any of the methods can be overridden to provide specific behaviour (e.g. HasScopes, IsReadOnly, etc.)

    """
    def global_permission_set(self):
        """
        Corresponds to all types of access from any types of clients

        Default allows checking global and object permissions for internal or external clients, then checking global and object
        permissions for clients acting via an App on behalf of a user or acting as an API client
        """

        return (
            (
                (
                    IsInternalClient() & self.internal_permission_set()
                 ) | (
                    IsExternalClient() & self.external_permission_set()
                )
            ) & (
                (
                    IsActingAsUser() & self.user_permission_set()
                 ) | (
                    IsActingAsClient() & self.client_permission_set()
                )
            )
        )

    def object_permission_set(self):
        """
        Corresponds to all types of access to a specific object from any types of clients
        """
        return (
            (
                (
                    IsInternalClient() & self.internal_object_permission_set()
                 ) | (
                    IsExternalClient() & self.external_object_permission_set()
                )
            ) & (
                (
                    IsActingAsUser() & self.user_object_permission_set()
                 ) | (
                    IsActingAsClient() & self.client_object_permission_set()
                )
            )
        )

    def internal_permission_set(self):
        """
        Corresponds to all types of access from an internal client

        Access should be denied explicitly
        """
        return Allow()

    def external_permission_set(self):
        """
        Corresponds to all types of access from an external client

        Access should be granted explicitly
        """
        return Deny()



    def internal_object_permission_set(self):
        """
        Corresponds to all types of access to a specific object from an internal client

        Access should be denied explicitly
        """
        return Allow()

    def external_object_permission_set(self):
        """
        Corresponds to all types of access to a specific object from an external client

        Access should be granted explicitly
        """
        return Deny()

    def user_permission_set(self):
        """
        Corresponds to a WebApp (or third party app) access

        Access should be granted explicitly
        """
        return Deny()

    def user_object_permission_set(self):
        """
        Corresponds to a WebApp (or third party app) access to a specific object

        Access should be granted explicitly
        """
        return Deny()

    def client_permission_set(self):
        """
        Corresponds to an API access for both internal and external clients

        Default allows to fine grain access based on whether the client is internal or external

        """
        return (
               IsInternalClient() & self.internal_client_permission_set()
           ) | (
               IsExternalClient() & self.external_client_permission_set()
        )

    def internal_client_permission_set(self):
        """
        Corresponds to an API access from an internal client

        Access should be denied explicitly
        """
        return Allow()

    def external_client_permission_set(self):
        """
        Corresponds to an API access from an external client

        Access should be granted explicitly
        """
        return Deny()

    def client_object_permission_set(self):
        """
        Corresponds to an API access to a specific object for both internal and external clients

        Default allows to fine grain access based on whether the client is internal or external

        """
        return (
               IsInternalClient() & self.internal_client_object_permission_set()
           ) | (
                IsExternalClient() & self.external_client_object_permission_set()
        )

    def internal_client_object_permission_set(self):
        """
        Corresponds to an API access to a specific object from an internal client

        Access should be denied explicitly
        """
        return Allow()

    def external_client_object_permission_set(self):
        """
        Corresponds to an API access to a specific object from a third party client

        Access should be granted explicitly
        """
        return Deny()
