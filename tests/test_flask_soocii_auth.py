import os
import uuid

import pytest
from flask import Flask, Response, g

from flask_soocii_auth import SoociiAuthenticator, users, exceptions
from soocii_services_lib import auth


class TestFlaskSoociiAuth:
    app = None
    client = None

    def setup_method(self, _):
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

        @self.app.route('/')
        def hello_soocii():
            print('Hello Soocii')
            return Response()

        os.environ['ACCESS_TOKEN_SECRET'] = '6ca21c5ab8a6c181f5cfb91479588e37'
        os.environ['REFRESH_TOKEN_SECRET'] = 'ea57844efdcd163c4d84b8f7bf087baf'

    def test_valid_token(self):
        SoociiAuthenticator(self.app)
        token = auth.generate_access_token('MP01', uuid.uuid4().hex, 1, '', soocii_id='fake_soocii_id').decode('utf-8')
        resp = self.client.get('/', headers={'Authorization': 'Bearer {}'.format(token)})
        assert resp.status_code == 200

    def test_invalid_token(self):
        SoociiAuthenticator(self.app)
        resp = self.client.get('/', headers={'Authorization': 'Bearer {}'.format('invalid_token')})
        assert resp.status_code == 401

    def test_without_token(self):
        SoociiAuthenticator(self.app)
        resp = self.client.get('/', headers={'Authorization': 'Bearer {}'.format('invalid_token')})
        assert resp.status_code == 401

    def test_is_safe_req_is_true(self):

        def fake_func(_):
            return True

        SoociiAuthenticator(self.app, fake_func)
        resp = self.client.get('/')
        assert resp.status_code == 200

    def test_is_safe_req_is_false(self):

        def fake_func(_):
            return False

        SoociiAuthenticator(self.app, fake_func)
        resp = self.client.get('/')
        assert resp.status_code == 401

    def test_user_is_backstage(self):
        with self.app.test_client() as c:
            token = auth.generate_access_token(
                'MP01', uuid.uuid4().hex, 1, '', soocii_id='fake_soocii_id', device_type='BACKSTAGE'
            ).decode('utf-8')
            SoociiAuthenticator(self.app)
            resp = c.get('/', headers={'Authorization': 'Bearer {}'.format(token)})
            assert resp.status_code == 200
            assert isinstance(g.user, users.BackstageUser)

    def test_user_is_normal(self):
        with self.app.test_client() as c:
            token = auth.generate_access_token(
                'MP01', uuid.uuid4().hex, 1, '', soocii_id='fake_soocii_id'
            ).decode('utf-8')
            SoociiAuthenticator(self.app)
            resp = c.get('/', headers={'Authorization': 'Bearer {}'.format(token)})
            assert resp.status_code == 200
            assert isinstance(g.user, users.User)

    def test_user_anonymous(self):

        def fake_func(_):
            return True

        with self.app.test_client() as c:
            SoociiAuthenticator(self.app, fake_func)
            resp = c.get('/')
            assert resp.status_code == 200
            assert isinstance(g.user, users.AnonymousUser)

    def test_user_soocii_guest(self):
        with self.app.test_client() as c:
            token = auth.generate_access_token(
                'MP01', uuid.uuid4().hex, 1, '', soocii_id='soocii_guest'
            ).decode('utf-8')
            SoociiAuthenticator(self.app)
            resp = c.get('/', headers={'Authorization': 'Bearer {}'.format(token)})
            assert resp.status_code == 200
            assert isinstance(g.user, users.SoociiGuest)

    def test_env_vars_invalid(self):
        os.environ['ACCESS_TOKEN_SECRET'] = 'None'
        os.environ['REFRESH_TOKEN_SECRET'] = 'None'

        with pytest.raises(exceptions.InvalidTokenSecretError):
            SoociiAuthenticator(self.app)
