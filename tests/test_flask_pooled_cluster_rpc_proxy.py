#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from mock import Mock, patch
from flask import Flask, g
from flask_nameko import FlaskPooledClusterRpcProxy
from flask_nameko.errors import ClientUnavailableError

@pytest.fixture
def some_fixture():
    pass

@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.config.update(dict(NAMEKO_AMQP_URI='test'))
    return app

def test_configuration_pulls_nameko_names(flask_app):
    with patch.object(FlaskPooledClusterRpcProxy, 'configure') as configure:
        rpc = FlaskPooledClusterRpcProxy(flask_app)
        configure.assert_called_once_with(dict(AMQP_URI='test'))

def test_connection_is_reused_in_app_context(flask_app):
    with patch('flask_nameko.proxies.ClusterRpcProxy'):
        rpc = FlaskPooledClusterRpcProxy(flask_app)
        with flask_app.test_request_context():
            connection = rpc.get_connection()
            connection1 = rpc.get_connection()
            assert connection == connection1

def test_connection_is_returned_and_reused_when_app_context_ends(flask_app):
    flask_app.config.update(dict(NAMEKO_INITIAL_CONNECTIONS=1))
    with patch('flask_nameko.proxies.ClusterRpcProxy'):
        rpc = FlaskPooledClusterRpcProxy(flask_app)
        with flask_app.test_request_context():
            connection = rpc.get_connection()
        with flask_app.test_request_context():
            connection1 = rpc.get_connection()
        assert connection1 ==  connection

def test_new_connection_is_used_for_new_app_context(flask_app):
    with patch('flask_nameko.proxies.ClusterRpcProxy', side_effect=lambda x: Mock()):
        rpc = FlaskPooledClusterRpcProxy(flask_app)

        with flask_app.test_request_context():
            connection = rpc.get_connection()

        with flask_app.test_request_context():
            connection1 = rpc.get_connection()

        assert connection1 != connection

