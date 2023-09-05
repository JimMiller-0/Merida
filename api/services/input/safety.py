from flask_restx import Namespace, Resource, fields
from flask import Flask, jsonify, request
import os 
import google.cloud.dlp
from typing import List

api = Namespace("dogs", description="Dogs related operations")

dog = api.model(
    "Dog",
    {
        "id": fields.String(required=True, description="The dog identifier"),
        "name": fields.String(required=True, description="The dog name"),
    },
)

DOGS = [
    {"id": "medor", "name": "Medor"},
]


@api.route("/")
class DogList(Resource):
    @api.doc("list_dogs")
    @api.marshal_list_with(dog)
    def get(self):
        """List all dogs"""
        return DOGS


@api.route("/<id>")
@api.param("id", "The dog identifier")
@api.response(404, "Dog not found")
class Dog(Resource):
    @api.doc("get_dog")
    @api.marshal_with(dog)
    def get(self, id):
        """Fetch a dog given its identifier"""
        for dog in DOGS:
            if dog["id"] == id:
                return dog
        api.abort(404)


@api.route("/DLP", methods=["POST"])
@api.response(404, "Error")
class DLP(Resource):
    @api.doc("post_dlp")
    def dlp():
        if request.method == "POST":
            user_text = request.form("user_input")
            PROJECT_ID=os.environ.get("PROJECT_ID")

            def deidentify_with_replace_infotype(
                project: str, item: str, info_types: List[str]
            ) -> None:
                """Uses the Data Loss Prevention API to deidentify sensitive data in a
                string by replacing it with the info type.
                Args:
                    project: The Google Cloud project id to use as a parent resource.
                    item: The string to deidentify (will be treated as text).
                    info_types: A list of strings representing info types to look for.
                        A full list of info type categories can be fetched from the API.
                Returns:
                    None; the response from the API is printed to the terminal.
                """

                # Instantiate a client
                dlp = google.cloud.dlp_v2.DlpServiceClient()

                # Convert the project id into a full resource id.
                parent = f"projects/{PROJECT_ID}"

                # Construct inspect configuration dictionary
                inspect_config = {"info_types": [{"name": info_type} for info_type in info_types]}

                # Construct deidentify configuration dictionary
                deidentify_config = {
                    "info_type_transformations": {
                        "transformations": [
                            {"primitive_transformation": {"replace_with_info_type_config": {}}}
                        ]
                    }
                }

                # Call the API
                response = dlp.deidentify_content(
                    request={
                        "parent": parent,
                        "deidentify_config": deidentify_config,
                        "inspect_config": inspect_config,
                        "item": {"value": item},
                    }
                )

                # Print out the results.
                return response.item.value

            deidentify_with_replace_infotype(PROJECT_ID, user_text.text, ["PERSON_NAME","EMAIL_ADDRESS"])

        else:
            api.abort(404)
