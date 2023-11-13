import time
import traceback
from functools import wraps
from typing import Any, Callable, Tuple

import psycopg2
import psycopg2.pool
import psycopg2.extras
from psycopg2.extras import RealDictCursor, execute_values

from flask import current_app


def db_pool_conn_exchange(fn: Callable) -> Callable:
    """Wrapper function that handles pool connections and database connection retries.
    If a connection from the pool is available, it's occupied and used by the query function, then returned to the pool.
    If it's not available, and there is room to create more, it creates a new connection, uses it, and destroys it in the end.
    If it can't create a new connection, it has a waiting mechanism to get a new connection as soon as one opens up.
    Handles retries logic if the connection is closed.

    Args:
        fn (function): A query funciton

    Raises:
        Exception: psycopg2.InterfaceError - Connection is closed, need to retry
        Exception: default exception - raise error

    Returns:
        callable: Returns the query function
    """

    @wraps(fn)
    def wrapper(*args, **kw):
        cls = args[0]
        db_conn, db_cur = None, None
        for i in range(cls._RECONNECT_TRIES):
            try:
                db_conn, db_cur = cls.db_pool.get_conn_cur()
                cls.db_connection = db_conn
                cls.db_cur = db_cur
                return fn(*args, **kw)
            except psycopg2.InterfaceError as interface_err:
                print("Idle for %s seconds" % (cls._RECONNECT_IDLE))
                time.sleep(cls._RECONNECT_IDLE)
                connection_key = cls.db_pool.postgreSQL_pool._rused[id(db_conn)]
                print(connection_key, "cK")
                db_conn = cls.db_pool.postgreSQL_pool._connect(
                    connection_key
                )  # just used to reconnect the connection
                print("Reconnected {}!".format(connection_key))
            finally:
                if db_conn:
                    return_retries = 0
                    while return_retries < 3:
                        try:
                            return_retries += 1
                            cls.db_cur.close()
                            cls.db_pool.postgreSQL_pool.putconn(db_conn)
                            break
                        except psycopg2.OperationalError as e:
                            print(
                                "Failed to return to pool, return counter is {}".format(
                                    return_retries
                                )
                            )
                            if return_retries >= 3:
                                raise Exception(
                                    "Unable to return the used connection to the database connection pool!"
                                )
                            continue
                        except Exception as e:
                            print(
                                traceback.format_exc(),
                                "Unable to return the used connection to the database connection pool!",
                            )
                            if return_retries >= 3:
                                raise Exception(
                                    "Unable to return the used connection to the database connection pool!"
                                )
                        time.sleep(cls._RECONNECT_IDLE)

    return wrapper


class DatabasePool(object):
    """Class for creating a pool of database connections."""

    def __init__(self, annotation_db=False, min_conn=1, max_conn=3):
        """Creates and initializes a connection pool for the database

        Args:
            annotation_db (bool, optional): Are the connections toward the annotation database. Defaults to False.
            min_conn (int, optional): Min number of connections in the pool. Defaults to 1.
            max_conn (int, optional): Max number of connections in the pool. Defaults to 3.
        """
        self.annotation_db_conn = annotation_db
        # print(self.annotation_db_conn)
        self.max_conn = max_conn
        self.min_conn = min_conn
        self.hostname = current_app.config["DB_HOST"]
        self.username = current_app.config["DB_USER"]
        self.password = current_app.config["DB_PASSWORD"]
        self.database = current_app.config["DB_NAME"]

        self.GET_POOL_CONN_TIMEOUT = 30

        # print(self.username, self.password, self.hostname, self.database)
        self.postgreSQL_pool = psycopg2.pool.ThreadedConnectionPool(
            self.min_conn,
            self.max_conn,
            user=self.username,
            password=self.password,
            host=self.hostname,
            port="5432",
            database=self.database,
        )

    def get_conn_cur(self) -> Tuple:
        """Fetch a single connection and a cursor from it from the pool

        Returns:
            tuple: db_connection, db_cursor
        """
        db_connection = None
        db_cur = None
        start_time = time.time()

        while time.time() - start_time < self.GET_POOL_CONN_TIMEOUT:
            a = time.time()
            try:
                db_connection = self.postgreSQL_pool.getconn()
            except psycopg2.pool.PoolError as pool_err:
                time.sleep(0.03)
            if db_connection:
                db_cur = db_connection.cursor(cursor_factory=RealDictCursor)
                break
        return db_connection, db_cur

    def db_pool_conn_exchange(func):
        """Decorator function to handle connection and cursor exchange with the database pool"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            db_pool = DatabasePool()
            db_connection, db_cur = db_pool.get_conn_cur()
            kwargs["db_connection"] = db_connection
            kwargs["db_cur"] = db_cur
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                db_connection.rollback()
                raise e
            finally:
                db_pool.postgreSQL_pool.putconn(db_connection)
            return result

        return wrapper

    @db_pool_conn_exchange
    def execute_query(
        self,
        query: str,
        data: dict[str, Any] | tuple[Any] | None = None,
        conn_autocommit: bool = True,
        fetch_all: bool = False,
        execute_many: bool = False,
    ) -> dict | list:
        """Handles logic to execute a sql query string, pass along its data, and format what kind of format to return

        Args:
            query (str): sql query string
            data (dict[str, Any] | tuple[Any] | None, optional): The arguments passed to the query. Defaults to None.
            conn_autocommit (bool, optional): Whether to automatically commit the transaction after the query is done executing. Defaults to True.
            fetch_all (bool, optional):
            Whether to return an array of all items fetched from the database, or a dictionary with the first one found. Defaults to False.
            execute_many(bool, optional): Whether to execute for many rows at once. Defaults to False.
        Raises:
            Exception: handles query rollback and resets the autocommit property on exception.

        Returns:
            dict | list: The result of the query from the database.
        """
        try:
            # set connection to (auto)commit
            self.db_connection.autocommit = conn_autocommit

            if execute_many:
                # execute query for multiple values
                result = execute_values(self.db_cur, query, data, fetch=True)
            else:
                # execute single query
                self.db_cur.execute(query, data) if data else self.db_cur.execute(query)
                # fetch the data
                result = self.db_cur.fetchall() if fetch_all else self.db_cur.fetchone()

            # manually commit if user designated so
            if conn_autocommit == False:
                self.db_connection.commit()
            self.db_connection.autocommit = False

            # When trying to fetch many results psycopg2 will return empty list
            # if there are no results, however if we're fetching just one result
            # psycopg2 will return None if no result found, but since a Flask route
            # can't return None we defalt this value to empty dict in that case.
            return {} if result is None else result

        except Exception as e:
            print(e.args, "Failed to execute a DB query in suiteapi")
            if conn_autocommit == False:
                self.db_connection.rollback()
            self.db_connection.autocommit = False

            raise e

    def __del__(self):
        pass  # implement deletion method for connection pool
