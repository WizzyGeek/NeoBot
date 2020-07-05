from collections import deque

import psycopg2
from psycopg2 import extensions as _ext
from psycopg2.pool import PoolError

from .DbObjects import Cursor, Connection

class ConnectionPool:
    """A faster pool without bloat for discord bots."""
    def __init__(self, minconn: int = 1, maxconn: int = 5, *args, **kwargs):
        self.minconn: int = minconn
        self.maxconn: int = maxconn
        self.closed: bool = False

        self._args = args
        self._kwargs = kwargs

        self._pool = deque()
        for i in range(self.minconn):
            self.connect()

    def connect(self):
        """Create a new connection."""
        conn = psycopg2.connect(*self._args, **self._kwargs)
        self._pool.append(conn)
        return conn

    def getconn(self):
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

    def putconn(self, conn, close=False):
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
            # If the connection is closed, we just discard it.
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
