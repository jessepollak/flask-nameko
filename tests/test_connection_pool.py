#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
import eventlet
from datetime import timedelta
from mock import Mock, patch
from flask_nameko.connection_pool import ConnectionPool, Connection
from flask_nameko.errors import ClientUnavailableError

@pytest.fixture
def some_fixture():
    pass

@pytest.fixture
def get_connection():
    connection = Mock(side_effect=lambda: object())
    return connection

def test_connections_recycled(get_connection):
    pool = ConnectionPool(get_connection, initial_connections=0)

    o = pool.get_connection()
    pool.release_connection(o)
    o1 = pool.get_connection()
    o2 = pool.get_connection()

    assert o1 == o
    assert o1 != o2

def test_new_connections_used(get_connection):
    pool = ConnectionPool(get_connection, initial_connections=0)

    o = pool.get_connection()
    o1 = pool.get_connection()

    assert o1 != o

def test_max_connections_raises(get_connection):
    pool = ConnectionPool(get_connection, initial_connections=0, max_connections=2)

    pool.get_connection()
    pool.get_connection()

    with pytest.raises(ClientUnavailableError):
        pool.get_connection(next_timeout=0)

def test_creates_initial_connections(get_connection):
    pool = ConnectionPool(get_connection, initial_connections=2)
    assert get_connection.call_count == 2

def test_connections_get_recycled(get_connection):
    pool = ConnectionPool(
        get_connection,
        initial_connections=1,
        max_connections=1,
        recycle=3600
    )

    conn = pool.get_connection()
    pool.release_connection(conn)
    conn2 = pool.get_connection()
    pool.release_connection(conn2)

    assert conn == conn2

    with patch.object(conn2, 'is_stale', return_value=True):
        conn3 = pool.get_connection()

    assert conn3 != conn
    assert conn3 != conn2

def test_connection_is_stale_for_stale_connection():
    connection = Connection(None)
    eventlet.sleep(2)
    assert connection.is_stale(timedelta(seconds=1))

def test_connection_is_not_stale_for_good_connection():
    connection = Connection(None)
    assert not connection.is_stale(timedelta(seconds=3600))
