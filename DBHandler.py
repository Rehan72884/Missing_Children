import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DBHandler:
    Base = declarative_base()

    def __init__(self, server, database, username, password):
        connection_url = URL.create(
            "mssql+pyodbc",
            username=username,
            password=password,
            host=server,
            database=database,
            query={"driver": "ODBC Driver 17 for SQL Server"},
        )
        self.engine = create_engine(connection_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)


def _database_settings():
    environment_variables = {
        "server": "DB_SERVER",
        "database": "DB_NAME",
        "username": "DB_USERNAME",
        "password": "DB_PASSWORD",
    }
    settings = {
        name: os.getenv(environment_variable)
        for name, environment_variable in environment_variables.items()
    }
    missing = [
        environment_variable
        for name, environment_variable in environment_variables.items()
        if not settings[name]
    ]
    if missing:
        raise RuntimeError(
            "Missing required database environment variables: "
            + ", ".join(missing)
        )
    return settings


def return_session():
    db_handler = DBHandler(**_database_settings())
    return db_handler.Session()


def check_database_connection():
    db_handler = DBHandler(**_database_settings())
    with db_handler.engine.connect():
        print("Database connection successful.")
