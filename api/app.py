from flask import Flask, render_template, request, Response
from flask import make_response
from api.routes.routes import blueprint as api
import sqlalchemy
import logging
import os
from api.db.connect_tcp import connect_tcp_socket
from api.db.db import init_connection_pool, migrate_db, pidetect_db, extension_db, index_table


# flask app factory to create app


def create_app():
    app = Flask(__name__)

    logger = logging.getLogger()


    # init_db lazily instantiates a database connection pool. Users of Cloud Run or
    # App Engine may wish to skip this lazy instantiation and connect as soon
    # as the function is loaded. This is primarily to help testing.
    with app.app_context():
                db = init_connection_pool()
                migrate_db(db)
                extension_db(db)
                pidetect_db(db)    

    @app.route("/", methods=["GET"])
    def home():
        return make_response(({"success": True}), 200)

    app.register_blueprint(api, url_prefix="/v1")
    return app