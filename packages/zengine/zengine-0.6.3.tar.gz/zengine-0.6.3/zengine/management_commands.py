# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.manage import *
from zengine.views.crud import SelectBoxCache


class UpdatePermissions(Command):
    """
    Gets permissions from
    :attr:`~zengine.settings.PERMISSION_PROVIDER`
    then creates
    :attr:`~zengine.settings.PERMISSION_MODEL`
    objects if required.

    Args:
        dry: Dry run. Do nothing, just list.
    """
    CMD_NAME = 'update_permissions'
    HELP = 'Syncs permissions with DB'
    PARAMS = [
        {'name': 'dry', 'action':'store_true', 'help': 'Dry run, just list new found permissions'},
    ]
    def run(self):
        """
        Creates new permissions.
        """
        from pyoko.lib.utils import get_object_from_path
        from zengine.config import settings
        model = get_object_from_path(settings.PERMISSION_MODEL)
        perm_provider = get_object_from_path(settings.PERMISSION_PROVIDER)
        existing_perms = []
        new_perms = []
        for code, name, desc in perm_provider():
            if self.manager.args.dry:
                exists = model.objects.filter(code=code, name=name)
                if exists:
                    perm = exists[0]
                    new = False
                else:
                    new = True
                    perm = model(code=code, name=name)
            else:
                perm, new = model.objects.get_or_create({'description': desc}, code=code, name=name)
                if new:
                    new_perms.append(perm)
                else:
                    existing_perms.append(perm)

        report = "\n\n%s permission(s) were found in DB. " % len(existing_perms)
        if new_perms:
            report += "\n%s new permission record added. " % len(new_perms)
        else:
            report += 'No new perms added. '

        if new_perms:
            if not self.manager.args.dry:
                SelectBoxCache.flush(model.__name__)
            report += 'Total %s perms exists.' % (len(existing_perms) + len(new_perms))
            report = "\n + " + "\n + ".join([p.name for p in new_perms]) + report
        if self.manager.args.dry:
            print("\n~~~~~~~~~~~~~~ DRY RUN ~~~~~~~~~~~~~~\n")
        print(report + "\n")



class CreateUser(Command):
    """
    Creates a new user.

    Because this doesn't handle permission and role management,
    this is only useful when new user is a superuser.
    """
    CMD_NAME = 'create_user'
    HELP = 'Creates a new user'
    PARAMS = [
        {'name': 'username', 'required': True, 'help': 'Login username'},
        {'name': 'password', 'required': True, 'help': 'Login password'},
        {'name': 'super', 'action': 'store_true', 'help': 'This is a super user'},
    ]

    def run(self):
        """
        Creates user, encrypts password.
        """
        from zengine.models import User
        user = User(username=self.manager.args.username, superuser=self.manager.args.super)
        user.set_password(self.manager.args.password)
        user.save()
        print("New user created with ID: %s" % user.key)


class RunServer(Command):
    """
    Runs development server.

    Args:
        addr: Listen address. Defaults to 127.0.0.1
        port: Listen port. Defaults to 9001
    """
    CMD_NAME = 'runserver'
    HELP = 'Run the development server'
    PARAMS = [
        {'name': 'addr', 'default': '127.0.0.1', 'help': 'Listening address. Defaults to 127.0.0.1'},
        {'name': 'port', 'default': '9001', 'help': 'Listening port. Defaults to 9001'},
    ]

    def run(self):
        """
        Starts a simple_server for the zengine application
        """
        from wsgiref import simple_server
        from zengine.server import app
        httpd = simple_server.make_server(self.manager.args.addr, int(self.manager.args.port), app)
        print("Development server started on http://%s:%s. \n\nPress Ctrl+C to stop\n" % (
            self.manager.args.addr,
            self.manager.args.port)
              )
        httpd.serve_forever()
