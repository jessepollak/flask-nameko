#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from mock import Mock, patch, ANY, MagicMock
from nameko.standalone.rpc import ClusterRpcProxy
from flask import Flask, g
from flask_nameko import FlaskPooledClusterRpcProxy
from flask_nameko.connection_pool import ConnectionPool
from flask_nameko.proxies import LazyServiceProxy
from flask_nameko.errors import (
    ClientUnavailableError,
    ClusterNotConfiguredError
)

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

def test_not_configured_raises_exception(flask_app):
    rpc = FlaskPooledClusterRpcProxy()
    with flask_app.test_request_context():
        with pytest.raises(ClusterNotConfiguredError):
            rpc.not_configured_service.test()

def test_connection_is_reused_in_app_context(flask_app):
    with patch('flask_nameko.proxies.ClusterRpcProxy'):
        rpc = FlaskPooledClusterRpcProxy(flask_app, connect_on_method_call=False)
        with flask_app.test_request_context():
            connection = rpc.get_connection()
            connection1 = rpc.get_connection()
            assert connection == connection1

def test_connection_is_returned_and_reused_when_app_context_ends(flask_app):
    flask_app.config.update(dict(NAMEKO_INITIAL_CONNECTIONS=1))
    with patch('flask_nameko.proxies.ClusterRpcProxy'):
        rpc = FlaskPooledClusterRpcProxy(flask_app, connect_on_method_call=False)
        with flask_app.test_request_context():
            connection = rpc.get_connection()
        with flask_app.test_request_context():
            connection1 = rpc.get_connection()
        assert connection1 ==  connection

def test_new_connection_is_used_for_new_app_context(flask_app):
    class FakeClusterRpcProxy(object):
        n = 0
        def start(self):
            self.n = self.n + 1
            return self.n

    mock = FakeClusterRpcProxy()
    with patch('flask_nameko.proxies.ClusterRpcProxy', return_value=mock):

        rpc = FlaskPooledClusterRpcProxy(flask_app, connect_on_method_call=False)

        with flask_app.test_request_context():
            connection = rpc.get_connection()

        with flask_app.test_request_context():
            connection1 = rpc.get_connection()

        assert connection1 != connection

def test_connect_on_method_call_false_returns_connection(flask_app):
    with flask_app.test_request_context():
        with patch('flask_nameko.proxies.ClusterRpcProxy', return_value=MagicMock()):
            rpc = FlaskPooledClusterRpcProxy(flask_app, connect_on_method_call=False)
            assert isinstance(rpc.service, Mock)

def test_connect_on_method_call_returns_lazy_proxy(flask_app):
    with patch('flask_nameko.proxies.ClusterRpcProxy', return_value=MagicMock()):
        rpc = FlaskPooledClusterRpcProxy(flask_app, connect_on_method_call=True)
        assert isinstance(rpc.service, LazyServiceProxy)

def test_timeout_is_passed_through_to_cluster(flask_app):
    flask_app.config.update(dict(NAMEKO_RPC_TIMEOUT=10))
    with patch('flask_nameko.proxies.ClusterRpcProxy', spec_set=ClusterRpcProxy) as mock:
        FlaskPooledClusterRpcProxy(flask_app, connect_on_method_call=True)
        mock.assert_called_with(ANY, timeout=10)

def test_pool_recycle_is_passed_through_to_cluster(flask_app):
    flask_app.config.update(dict(NAMEKO_POOL_RECYCLE=3600))
    with patch('flask_nameko.proxies.ConnectionPool', spec_set=ConnectionPool) as mock:
        FlaskPooledClusterRpcProxy(flask_app)
        mock.assert_called_with(ANY, initial_connections=ANY, max_connections=ANY, recycle=3600)
