from Queue import Queue, Empty
from threading import Lock
from .errors import ClientUnavailableError

class ConnectionPool(object):
    def __init__(self, get_connection, initial_connections=2, max_connections=8):
        """
        Create a new pool
        :param func get_connection: The function that returns a connection
        :param int initial_connections: The initial number of connection objects to create
        :param int max_connections: The maximum amount of connections to create. These
          connections will only be created on demand and will potentially be
          destroyed once they have been returned via a call to
          :meth:`release_connection`
        constructor
        """
        self._get_connection = get_connection
        self._queue = Queue()
        self._current_connections = 0
        self._max_connections = max_connections
        self._lock = Lock()

        for x in range(initial_connections):
            connection = self._make_connection()
            self._queue.put(connection)

    def _make_connection(self):
        ret = self._get_connection()
        self._current_connections += 1
        return ret

    def get_connection(self, initial_timeout=0.05, next_timeout=1):
        """
        Wait until a connection instance is available
        :param float initial_timeout:
          how long to wait initially for an existing connection to complete
        :param float next_timeout:
          if the pool could not obtain a connection during the initial timeout,
          and we have allocated the maximum available number of connections, wait
          this long until we can retrieve another one
        :return: A connection object
        """
        try:
            return self._queue.get(True, initial_timeout)
        except Empty:
            try:
                self._lock.acquire()
                if self._current_connections == self._max_connections:
                    raise ClientUnavailableError("Too many connections in use")
                cb = self._make_connection()
                return cb
            except ClientUnavailableError as ex:
                try:
                    return self._queue.get(True, next_timeout)
                except Empty:
                    raise ex
            finally:
                self._lock.release()

    def release_connection(self, cb):
        """
        Return a Connection object to the pool
        :param Connection cb: the connection to release
        """
        self._queue.put(cb, True)
