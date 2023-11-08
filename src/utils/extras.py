import json
import functools
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from psycopg_pool import ConnectionPool
from pydantic import BaseModel, ValidationError

from flask import abort


def validate_data(
    data: dict, model: type[BaseModel], exclude_unset: bool = False
) -> dict:
    """
    Return dict of validated data on constrains given in a model.
    Raise 422 error with Pydantic detail as an error description.
    :param: data: Dict containing the input data to be validated.
    :param: model: Appropriate Pydantic class that will validate the data.
    :param: exclude_unset: Whether to return the fields
    that were not provided in the input data
    """
    try:
        return model(**data).dict(exclude_unset=exclude_unset)
    except ValidationError as e:
        abort(422, json.loads(e.json()))


def validate_data(
    data: dict, model: type[BaseModel], exclude_unset: bool = False
) -> dict:
    """
    Return dict of validated data on constrains given in a model.
    Raise 422 error with Pydantic detail as an error description.
    :param: data: Dict containing the input data to be validated.
    :param: model: Appropriate Pydantic class that will validate the data.
    :param: exclude_unset: Whether to return the fields
    that were not provided in the input data
    """
    try:
        return model(**data).dict(exclude_unset=exclude_unset)
    except ValidationError as e:
        abort(422, json.loads(e.json()))


@functools.cache
def read_query(path: str | Path) -> str:
    return Path(path).read_text()


@contextmanager
def db_connection(db_pool: ConnectionPool, autocommit: bool = True) -> Generator:
    """
    Just a thin context wrapper arround psycopg3 to avoid constantly setting
    `conn.autocommit = autocommit` which will be True in the majority of the use cases.
    """
    with db_pool.connection() as conn:
        conn.autocommit = autocommit
        yield conn
