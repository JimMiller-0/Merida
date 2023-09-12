
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

    # create 'votes' table in database if it does not already exist
def pidetect_db(db: sqlalchemy.engine.base.Engine) -> None:
        pidetect_db_create='CREATE TABLE IF NOT EXISTS threatmgmt (pi_id SERIAL NOT NULL, date_added timestamp NOT NULL, date_lastseen timestamp NOT NULL, prompt_injection_text TEXT, prompt_injection_embedding VECTOR(768), PRIMARY KEY (pi_id) );'
        with db.connect() as conn:
            conn.execute(sqlalchemy.text(pidetect_db_create))
            conn.commit()

def extension_db(db: sqlalchemy.engine.base.Engine) -> None:
        ml_extension_create='CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;'
        vector_extension_create='CREATE EXTENSION IF NOT EXISTS vector;'
        with db.connect() as conn:
            conn.execute(sqlalchemy.text(ml_extension_create))
            conn.commit()
            conn.execute(sqlalchemy.text(vector_extension_create))
            conn.commit()



def index_table(db: sqlalchemy.engine.base.Engine) -> None:
        index_create ="CREATE INDEX complaint_embed_idx ON threatmgmt USING ivf (prompt_injection_embedding vector_cosine_ops) WITH (lists = 20, quantizer = 'SQ8');"
        with db.connect() as conn:
            conn.execute(sqlalchemy.text(index_create))
            conn.commit()
