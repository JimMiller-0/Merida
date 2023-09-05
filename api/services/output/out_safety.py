from flask_restx import Namespace, Resource, fields
from flask import Flask, jsonify, request
import os 
import google.cloud.dlp
from typing import List

api = Namespace("dlp", description="inspect user input for PII and redact")

dlp = api.model(
    "dlp",
    {
        "user_input": fields.String(description="original text"),
        "dlp_output": fields.String(description="redacted text"), 
    }
)

DLP_RESPONSE = [

    {"user_input": "medor", "dlp_output": "Medor"},
]

@api.route("/dlp", methods=["POST"])
@api.response(404, "Error")
class DLP(Resource):
    @api.doc("post_dlp")
   # @api.marshal_with(dlp)
    def post(self):
            user_text = request.form.get("user_input")
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

            dlp_output=deidentify_with_replace_infotype(PROJECT_ID, user_text, ["PERSON_NAME","EMAIL_ADDRESS"])

            return jsonify(dlp_output)
   