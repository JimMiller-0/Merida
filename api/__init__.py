from flask import Flask, jsonify
import os

def create_app(test_config=None):

    app = Flask(__name__,
    instance_relative_config=True)
    
    if test_config is None:

        app.config.from_mapping(
            SECRET_KET=os.environ.get("SECRET_KEY")

        )

    else:
        app.config.from_mapping(test_config)

    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"


    @app.get("/hello")
    def index():
        return jsonify({"message":"hello world"})
    

    
    
    return app