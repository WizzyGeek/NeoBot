from collections import deque

import psycopg2
from psycopg2 import extensions as _ext
from psycopg2.pool import PoolError

from .DbObjects import Cursor, Connection
from ..errors import ConnectionAlreadyAcquiredError

class ConnectionContext:
    def __init__(self, pool):
        self.pool = pool
        self._conn = None
        self.acquired: bool = False

    def __enter__(self):
        if self.conn is not None or self.acquired:
            raise ConnectionAlreadyAcquiredError("Connection already acquired.")
        else:
            self._conn = self.pool._getconn()
            return self._conn
    
    def __exit__(self, *exc):
        self.pool._putconn(self._conn)
        self._conn = None
        self.acquired = True

class ConnectionPool:
    """A faster pool without bloat.
    
    Initialize seperate pools for different databases as
    this pool doesn't support binding a connection to a key."""
    def __init__(self, minconn: int = 1, maxconn: int = 5, *args, **kwargs):
        self.minconn: int = minconn
        self.maxconn: int = maxconn
        self.closed: bool = False

        self._args = args
        self._kwargs = kwargs

        self._pool = deque()          # REASON : [a pool is at base a list of connections.
        for i in range(self.minconn): # deque has faster appends and pops which in theory,
            self.connect()            # coupled with less checks(i.e keys), should speed up the pool.]

    def connect(self):
        """Create a new connection."""
        conn = psycopg2.connect(*self._args, **self._kwargs)
        self._pool.append(conn)
        return conn

    def _getconn(self):
        """Get a free connection."""
        if self.closed:
            raise PoolError("connection pool is closed")

        if self._pool:
            # We checked if connections present.
            conn = self._pool.popleft()
            return conn
        else:
            if len(self._pool) == self.maxconn:
                raise PoolError("connection pool exhausted")
            return self.connect()

    def _putconn(self, conn, close=False):
        """Put away a connection."""
        if self.closed:
            raise PoolError("connection pool is closed")

        if len(self._pool) < self.minconn and not close:
            # Return the connection into a consistent state before putting
            # it back into the pool
            if not conn.closed:
                status = conn.info.transaction_status
                if status == _ext.TRANSACTION_STATUS_UNKNOWN:
                    # server connection lost
                    conn.close()
                elif status != _ext.TRANSACTION_STATUS_IDLE:
                    # connection in error or in transaction
                    conn.rollback()
                    self._pool.append(conn)
                else:
                    # regular idle connection
                    self._pool.append(conn)
        else:
            conn.close()

    def close(self):
        """Close """
        def closer(conn):
            try:
                conn.close()
            except:
                pass
        if self.closed:
            raise PoolError("connection pool is closed")
        map(closer, self._pool) # C level loop
        self._pool.clear()
        self.closed = True
        return None

    def reset(self):
        """Close all connections and reset pool"""
        self._closeall()
        self._pool.clear()
        self.closed = False
        return None

    def extend(self, pool):
        """
        Merge another connection pool into this pool,
        without destroying the other pool.
        """
        count = 0
        while len(self._pool) < self.maxconn:
            self._pool.append(pool._pool[count])
            count += 0
        else:
            return None

    def acquire(self):
        return ConnectionContext(self)