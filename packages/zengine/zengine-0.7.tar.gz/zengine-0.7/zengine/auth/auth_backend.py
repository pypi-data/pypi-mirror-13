# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.exceptions import ObjectDoesNotExist
from zengine.models import *


class AuthBackend(object):
    """
    A minimal implementation of AuthBackend

    :param session: Session object
    """

    def __init__(self, current):
        self.session = current.session
        self.current = current

    def get_user(self):
        # FIXME: Should return a proper AnonymousUser object
        # (instead of unsaved User instance)
        if 'user_id' in self.session:
            self.current.user_id = self.session['user_id']
            return User.objects.get(self.current.user_id)
        else:
            return User()

    def get_role(self):
        # TODO: This should work
        return self.get_user().role_set[0].role

    def get_permissions(self):
        return self.get_user().get_permissions()

    def has_permission(self, perm):
        user = self.get_user()
        return user.superuser or perm in user.get_permissions()

    def authenticate(self, username, password):
        try:
            user = User.objects.filter(username=username).get()
            is_login_ok = user.check_password(password)
            if is_login_ok:
                self.session['user_id'] = user.key
            return is_login_ok
        except ObjectDoesNotExist:
            pass
