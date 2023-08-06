# -*-  coding: utf-8 -*-
import os
from time import sleep
import falcon
from falcon import errors
from werkzeug.test import Client

from pyoko.lib.utils import pprnt
from zengine.server import app
from pprint import pprint
import json
from zengine.models import User, Permission, Role
from zengine.log import log
from pyoko.model import super_context

CODE_EXCEPTION = {
    falcon.HTTP_400: errors.HTTPBadRequest,
    falcon.HTTP_401: errors.HTTPUnauthorized,
    falcon.HTTP_403: errors.HTTPForbidden,
    falcon.HTTP_404: errors.HTTPNotFound,
    falcon.HTTP_406: errors.HTTPNotAcceptable,
    falcon.HTTP_500: errors.HTTPInternalServerError,
    falcon.HTTP_503: errors.HTTPServiceUnavailable,
}


class RWrapper(object):
    """
    Wrapper object for werkzeug test client's response
    """
    def __init__(self, *args):
        self.content = list(args[0])
        self.code = args[1]
        self.headers = list(args[2])
        try:
            self.json = json.loads(self.content[0].decode('utf-8'))
        except:
            log.exception('ERROR at RWrapper JSON load')
            self.json = {}

        self.token = self.json.get('token')

        if int(self.code[:3]) >= 400:
            self.raw()
            if self.code in CODE_EXCEPTION:
                raise CODE_EXCEPTION[self.code](title=self.json.get('title'),
                                                description=self.json.get('description'))
            else:
                raise falcon.HTTPError(title=self.json.get('title'),
                                       description=self.json.get('description'))

    def raw(self):
        """
        Pretty prints the response
        """
        pprint(self.code)
        pprnt(self.json)
        pprint(self.headers)
        if not self.json:
            pprint(self.content)



class TestClient(object):
    """
    TestClient to simplify writing API tests for Zengine based apps.
    """
    def __init__(self, path):
        """
        this is a wsgi test client based on werkzeug.test.Client

        :param str path: Request uri
        """
        self.set_path(path, None)
        self._client = Client(app, response_wrapper=RWrapper)
        self.user = None
        self.path = ''

    def set_path(self, path, token=''):
        """
        Change the path (workflow)

        Args:
            path: New path (or wf name)
            token: WF token.
        """
        self.path = path
        self.token = token

    def post(self, conf=None, **data):
        """
        by default data dict encoded as json and
        content type set as application/json

        :param dict conf: additional configs for test client's post method.
                          pass "no_json" in conf dict to prevent json encoding
        :param data: post data,
        :return: RWrapper response object
        :rtype: RWrapper
        """
        conf = conf or {}
        make_json = not conf.pop('no_json', False)
        if make_json:
            conf['content_type'] = 'application/json'
            if 'token' not in data and self.token:
                data['token'] = self.token
            data = json.dumps(data)
        response_wrapper = self._client.post(self.path, data=data, **conf)
        # update client token from response
        self.token = response_wrapper.token
        return response_wrapper


# encrypted form of test password (123)
user_pass = '$pbkdf2-sha512$10000$nTMGwBjDWCslpA$iRDbnITHME58h1/eVolNmPsHVq' \
            'xkji/.BH0Q0GQFXEwtFvVwdwgxX4KcN/G9lUGTmv7xlklDeUp4DD4ClhxP/Q'

username = 'test_user'
import sys

sys.TEST_MODELS_RESET = False


class BaseTestCase:
    """
    Base test case.
    """
    client = None

    @staticmethod
    def cleanup():
        """
        Deletes User and Permission objects.
        """
        if not sys.TEST_MODELS_RESET:
            for mdl in [User, Permission]:
                mdl(super_context).objects._clear_bucket()
            sys.TEST_MODELS_RESET = True

    @classmethod
    def create_user(cls):
        """
        Creates a new user and Role with all Permissions.
        """
        cls.cleanup()
        cls.client.user, new = User(super_context).objects.get_or_create({"password": user_pass,
                                                                          "superuser": True},
                                                                         username=username)
        if new:
            Role(super_context, user=cls.client.user).save()
            for perm in Permission(super_context).objects.raw("*:*"):
                cls.client.user.Permissions(permission=perm)
            cls.client.user.save()
            sleep(2)

    @classmethod
    def prepare_client(cls, path, reset=False, user=None, login=None, token=''):
        """
        Setups the path, logs in if necessary

        Args:
            path: change or set path
            reset: Create a new client
            login: Login to system
            token: Set token
        """

        if not cls.client or reset or user:
            cls.client = TestClient(path)
            login = True if login is None else login

        if not (cls.client.user or user):
            cls.create_user()
            login = True if login is None else login
        elif user:
            cls.client.user = user
            login = True if login is None else login

        if login:
            cls._do_login()

        cls.client.set_path(path, token)

    @classmethod
    def _do_login(self):
        """
        logs in the "test_user"
        """
        self.client.set_path("/login/")
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'LoginForm'
        req_fields = resp.json['forms']['schema']['required']
        assert all([(field in req_fields) for field in ('username', 'password')])
        assert not resp.json['is_login']
        resp = self.client.post(username=self.client.user.username,
                                password="123", cmd="do")
        assert resp.json['is_login']
        # assert resp.json['msg'] == 'Success'
