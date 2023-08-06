# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
import copy
from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import SAFE_METHODS

from restfw_composed_permissions.base import BasePermissionComponent, And, Or, Not
from restfw_composed_permissions.generic.components import ObjectAttrEqualToObjectAttr

# Provides the following on behalf of the restfw_composed_permissions package
assert BasePermissionComponent
assert ObjectAttrEqualToObjectAttr


class Allow(BasePermissionComponent):
    """
    Allow all

    """
    def has_permission(self, permission, request, view):
        return True

    def has_object_permission(self, permission, request, view, obj):
        return True


class Deny(BasePermissionComponent):
    """
    Deny all

    """
    def has_permission(self, permission, request, view):
        return False

    def has_object_permission(self, permission, request, view, obj):
        return False


class IsInternalClient(BasePermissionComponent):
    """
    Only allow authenticated internal clients
    """
    def is_internal_client(self, request):
        return hasattr(request, 'client') and request.client and request.client.is_internal

    def has_permission(self, permission, request, view):
        return self.is_internal_client(request)

    def has_object_permission(self, permission, request, view, obj):
        return self.is_internal_client(request)


class IsExternalClient(BasePermissionComponent):
    """
    Only allow authenticated external clients
    """
    def is_external_client(self, request):
        return hasattr(request, 'client') and request.client and not request.client.is_internal

    def has_permission(self, permission, request, view):
        return self.is_external_client(request)

    def has_object_permission(self, permission, request, view, obj):
        return self.is_external_client(request)


class IsActingAsClient(BasePermissionComponent):
    """
    Only allow acting as a client

    """
    def is_client(self, request):
        return hasattr(request, 'client') and request.client and request.user.is_anonymous()

    def has_permission(self, permission, request, view):
        return self.is_client(request)

    def has_object_permission(self, permission, request, view, obj):
        return self.is_client(request)


class IsActingAsUser(BasePermissionComponent):
    """
    Only allow acting as a user

    """
    def is_user(self, request):
        return hasattr(request, 'client') and request.client and request.user.is_authenticated()

    def has_permission(self, permission, request, view):
        return self.is_user(request)

    def has_object_permission(self, permission, request, view, obj):
        return self.is_user(request)


class HasActiveAPISubscription(BasePermissionComponent):

    def has_permission(self, permission, request, view):
        if not hasattr(request, 'account'):
            return True
        return request.account.api_subscription.is_active()


class HasActiveAppSubscription(BasePermissionComponent):

    def has_permission(self, permission, request, view):
        if not hasattr(request, 'account'):
            return True
        return request.account.app_subscription.is_active()


class HasScopes(BasePermissionComponent):
    """
    The request is authenticated as a user or client and the token used has been granted the right scope (global permissions only)

    """
    def __init__(self, *required_scopes):
        self.required_scopes = required_scopes

    def has_permission(self, permission, request, view):
        token = request.auth
        if not token:
            return False
        if hasattr(token, 'scope'):  # OAuth 2
            return token.is_valid(self.required_scopes)
        assert False, ('TokenHasScope requires the predicthq.apps.oauth2.authentication.BearerAuthentication` authentication class to be used.')


class IsReadOnly(BasePermissionComponent):
    """
    Only allow safe methods (global permissions only)

    """
    def has_permission(self, permission, request, view):
        return request.method in SAFE_METHODS


class IsAction(BasePermissionComponent):
    """
    Allow list of actions for a viewset and deny others

    """
    def __init__(self, *actions):
        self.actions = actions

    def is_valid_action(self, view):
        if not hasattr(view, 'action'):
            raise ImproperlyConfigured("Not a viewset")
        return view.action in self.actions

    def has_permission(self, permission, request, view):
        return self.is_valid_action(view)

    def has_object_permission(self, permission, request, view, obj):
        return self.is_valid_action(view)


class IsNested(BasePermissionComponent):
    """
    Only allow nested route access, check particular nesting key if provided

    """
    def __init__(self, parent_lookup_key=None):
        self.parent_lookup_key = parent_lookup_key

    def is_nested(self, view):
        if not hasattr(view, 'is_nested'):
            raise ImproperlyConfigured("View must implement is_nested()")
        return view.is_nested(self.parent_lookup_key)

    def has_permission(self, permission, request, view):
        return self.is_nested(view)

    def has_object_permission(self, permission, request, view, obj):
        return self.is_nested(view)


class ObjectAttrInObjectAttr(BasePermissionComponent):

    def __init__(self, obj_attr1, obj_attr2):
        self.obj_attr1 = obj_attr1
        self.obj_attr2 = obj_attr2

    def has_object_permission(self, permission, request, view, obj):
        safe_locals = {"obj": obj, "request": request}

        try:
            attr1_value = eval(self.obj_attr1, {}, safe_locals)
            attr2_value = eval(self.obj_attr2, {}, safe_locals)
        except AttributeError:
            return False
        else:
            return attr1_value in attr2_value


class ObjectAttrRelatedToObject(BasePermissionComponent):

    def __init__(self, obj_attr1, obj_attr2):
        self.obj_attr1 = obj_attr1
        self.obj_attr2 = obj_attr2

    def has_object_permission(self, permission, request, view, obj):
        safe_locals = {"obj": obj, "request": request}

        try:
            attr1_value = eval(self.obj_attr1, {}, safe_locals)
            attr2_value = eval(self.obj_attr2, {}, safe_locals)
        except AttributeError:
            return False
        else:
            return attr2_value.filter(**{self.obj_attr1.split('.')[-1]: attr1_value}).exists()
