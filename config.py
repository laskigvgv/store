import os
import json
from datetime import timedelta


def load_env(key):
    """
    Loads non-string env variable, such as int, float, dict, list, etc.
    If var not declared or it's empty returns None.
    If var not properly JSON formatted raises exception.
    """
    try:
        result = os.getenv(key)
        parse_nums = {"parse_float": float, "parse_int": int}
        return None if result in (None, "") else json.loads(result, **parse_nums)
    except (TypeError, json.decoder.JSONDecodeError) as e:
        msg = f"Expecting properly formated {key} value in the .env file. See example.env."
        raise TypeError(msg) from e


class Config:
    """
    Holds all necessary environment variables for the app.
    Gets string variables with os.getenv.
    Gets all other variables with load_env.
    """

    # general settings
    API_ENV = os.getenv("API_ENV")
    ENV_URL = os.getenv("ENV_URL")

    # database hosts
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PORT = load_env("DB_PORT")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")

    # limites
    CLIENT_RATE_LIMIT = load_env("CLIENT_RATE_LIMIT")

    # general settings
    LOGIN_DB_CONN = load_env("LOGIN_DB_CONN")
    CLIENT_CACHE_DB = load_env("CLIENT_CACHE_DB")
    DB_POOL_MIN_CONN = load_env("DB_POOL_MIN_CONN") or 1
    DB_POOL_MAX_CONN = load_env("DB_POOL_MAX_CONN") or 2


class DevConfig(Config):
    FLASK_ENV = "development"
    TEST_USERNAME = os.getenv("TEST_USERNAME")
    TEST_EMAIL = os.getenv("TEST_EMAIL")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD")
    TEST_HOST = os.getenv("TEST_HOST") or "localhost"
    TEST_PORT = load_env("TEST_PORT") or 5000
    CLIENT_PUBLIC_ID = os.getenv("CLIENT_PUBLIC_ID")
    SUITE_API_TESTING = load_env("SUITE_API_TESTING")
    TEST_SENDER_EMAIL_ADDR = os.getenv("TEST_SENDER_EMAIL_ADDR")
    TEST_RECEIVER_EMAIL_ADDR = os.getenv("TEST_RECEIVER_EMAIL_ADDR")
    DEBUG = True
    TESTING = True


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False
