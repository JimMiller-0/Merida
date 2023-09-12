from flask_restx import Namespace, Resource, fields 
from flask import Flask, jsonify, request, Response, make_response 
import os 
from datetime import datetime
import sqlalchemy
import logging   
import google.cloud.dlp
from typing import List, Dict
from api.db.db import init_connection_pool, migrate_db

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

logger = logging.getLogger()

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

    @api.route("/dbtestinsert", methods=["POST"])
    class DBI(Resource):
        @api.doc("post_dbi")
    # @api.marshal_with(dlp)
        def post(self):
            team = request.form.get("team")
            db = init_connection_pool()
            time_cast = datetime.now()
            migrate_db(db)

            def save_vote(db: sqlalchemy.engine.base.Engine, team: str) -> Response:
               
                # Verify that the team is one of the allowed options
                if team != "TABS" and team != "SPACES":
                    logger.warning(f"Received invalid 'team' property: '{team}'")
                    return Response(
                        response=(
                            "Invalid team specified."
                            " Should be one of 'TABS' or 'SPACES'"),
                        status=400,
                    )

                # [START cloud_sql_postgres_sqlalchemy_connection]
                # Preparing a statement before hand can help protect against injections.
                stmt = sqlalchemy.text(
                    "INSERT INTO votes (time_cast, candidate)"
                    " VALUES ('2022-04-22 10:34:23', 'SPACES');"
                )
                try:
                    # Using a with statement ensures that the connection is always released
                    # back into the pool at the end of statement (even if an error occurs)
                    with db.connect() as conn:
                        conn.execute(stmt)
                        conn.commit()
                except Exception as e:
                    # If something goes wrong, handle the error in this section. This might
                    # involve retrying or adjusting parameters depending on the situation.
                    # [START_EXCLUDE]
                    logger.exception(e)
                    return Response(
                        status=500,
                        response="Unable to successfully cast vote! Please check the "
                        "application logs for more details.",
                    )
                    # [END_EXCLUDE]
                # [END cloud_sql_postgres_sqlalchemy_connection]


                return Response(
                    status=200,
                    response=f"Vote successfully cast for '{team}' at time {time_cast}!",
                )
            
            def get_index_context(db: sqlalchemy.engine.base.Engine) -> Dict:
                votes = []

                with db.connect() as conn:
                    # Execute the query and fetch all results
                    firststmt = sqlalchemy.text(                        
                        "SELECT candidate, time_cast FROM votes"
                        " ORDER BY time_cast DESC LIMIT 5")
                    recent_votes = conn.execute(firststmt).fetchall()
                    # Convert the results into a list of dicts representing votes
                    for row in recent_votes:
                        votes.append({"candidate": row[0], "time_cast": row[1]})

                    stmt = sqlalchemy.text(
                        "SELECT COUNT(vote_id) FROM votes WHERE candidate=:candidate"
                    )
                    # Count number of votes for tabs
                    tab_result = conn.execute(stmt, {'candidate':'TABS'}).fetchone()
                    tab_count = tab_result[0]
                    # Count number of votes for spaces
                    space_result = conn.execute(stmt, {'candidate':'SPACES'}).fetchone()
                    space_count = space_result[0]

                return {
                    "space_count": space_count,
                    "recent_votes": votes,
                    "tab_count": tab_count,
                }
                        
            insertmsg=save_vote(db,team)
            countmsg=get_index_context(db)
            return make_response(({"success": insertmsg and countmsg}), 200)