import re
from flask import g
from nameko.standalone.rpc import ClusterRpcProxy
from .connection_pool import ConnectionPool
from .errors import (
    BadConfigurationError,
    ClusterNotConfiguredError
)

class PooledClusterRpcProxy(object):

    _pool = None
    _config = None

    def __init__(self, config=None):
        if config:
            self.configure(config)

    def configure(self, config):
        if not config.get('AMQP_URI'):
            raise BadConfigurationError("Please provide a valid configuration.")

        self._config = config
        self._pool = ConnectionPool(
            self._get_nameko_connection,
            initial_connections=config.get('INITIAL_CONNECTIONS', 2),
            max_connections=config.get('MAX_CONNETIONS', 8)
        )

    def _get_nameko_connection(self):
        proxy = ClusterRpcProxy(self._config)
        return proxy.start()

    def get_connection(self):
        if not self._pool:
            raise ClusterNotConfiguredError("Please configure your cluster beore requesting a connection.")
        return self._pool.get_connection()

    def release_connection(self, connection):
        return self._pool.release_connection(connection)


class FlaskPooledClusterRpcProxy(PooledClusterRpcProxy):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        config = dict()
        for key, val in app.config.iteritems():
            match = re.match(r"NAMEKO\_(?P<name>.*)", key)
            if match:
                config[match.group('name')] = val
        self.configure(config)
        app.teardown_appcontext(self._teardown_nameko_connection)

    def get_connection(self):
        connection = getattr(g, '_nameko_connection', None)
        if not connection:
            connection = super(FlaskPooledClusterRpcProxy, self).get_connection()
            g._nameko_connection = connection
        return connection

    def _teardown_nameko_connection(self, exception):
        connection = getattr(g, '_nameko_connection', None)
        if connection is not None:
            self.release_connection(connection)

    def __getattr__(self, name):
        return getattr(self.get_connection(), name)

    def __getitem__(self, name):
        return getattr(self.get_connection(), name)

