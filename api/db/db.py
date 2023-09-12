
from flask import Flask
from flask import make_response
import sqlalchemy
from sqlalchemy import text 
import logging
import os
from api.db.connect_tcp import connect_tcp_socket


def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    # use a TCP socket when INSTANCE_HOST (e.g. 127.0.0.1) is defined
        if os.environ.get("INSTANCE_HOST"):
            return connect_tcp_socket()

        raise ValueError(
            "Missing database connection parameter. Please define INSTANCE_HOST"
        )
    
    # create 'votes' table in database if it does not already exist
def migrate_db(db: sqlalchemy.engine.base.Engine) -> None:
        query_db_create='CREATE TABLE IF NOT EXISTS votes (vote_id SERIAL NOT NULL, time_cast timestamp NOT NULL, candidate VARCHAR(6) NOT NULL, PRIMARY KEY (vote_id) );'
        with db.connect() as conn:
            conn.execute(sqlalchemy.text(query_db_create))
            conn.commit()




