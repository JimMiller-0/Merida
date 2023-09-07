from flask import Flask
from flask import make_response
from api.routes.routes import blueprint as api
import sqlalchemy
import logging
import os

from api.config.connect_tcp import connect_tcp_socket


# flask app factory to create app


def create_app():
    app = Flask(__name__)

    logger = logging.getLogger()

    def init_connection_pool() -> sqlalchemy.engine.base.Engine:
    # use a TCP socket when INSTANCE_HOST (e.g. 127.0.0.1) is defined
        if os.environ.get("INSTANCE_HOST"):
            return connect_tcp_socket()

        raise ValueError(
            "Missing database connection parameter. Please define INSTANCE_HOST"
        )


    @app.route("/", methods=["GET"])
    def home():
        return make_response(({"success": True}), 200)

    app.register_blueprint(api, url_prefix="/v1")
    return app