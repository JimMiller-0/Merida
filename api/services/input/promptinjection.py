from flask_restx import Namespace, Resource, fields 
from flask import Flask, jsonify, request, Response, make_response 
import os 
import sys
import asyncio
import vertexai 
from datetime import datetime
import sqlalchemy
import logging   
import google.cloud.dlp
from typing import List, Dict
from api.db.db import init_connection_pool
from vertexai.preview.language_models import TextGenerationModel
from langchain.llms.base import BaseLLM
from langchain import LLMChain, PromptTemplate
from langchain.llms import VertexAI




api = Namespace("pi-detect", description="prompt injection detection")

pidetect = api.model(
    "pi-detect",
    {
        "user_input": fields.String(required=True, description="original text"),
        "pi_detected": fields.String(required=True, description="Bool - prompt injection detection status"),
    },
)

PIDETECT_RESPONSE = [
    {"user_input": "medor", "pi_detected": "Medor"},
]

logger = logging.getLogger()
@api.route("/")
class PIList(Resource):
    @api.doc("list_pi")
    #@api.marshal_list_with(cat)
    def get(self):
        return make_response({"pi_detect":"This API is for detecting prompt injection in user input"}, 200)


@api.route("/wrapping", methods=["POST"])
@api.response(404, "Error")
class Wrapping(Resource):
    @api.doc("post_wrapping")
   # @api.marshal_with(wrapping)
    def post(self):
            user_input = request.form.get("user_input")
            PROJECT_ID=os.environ.get("PROJECT_ID")
            # LLM model
            llm = VertexAI(
                model_name="text-bison@001",
                max_output_tokens=256,
                temperature=0.1,
                top_p=0.8,
                top_k=40,
                verbose=True,
            )

            generation_model = TextGenerationModel.from_pretrained("text-bison@001")

            async def pi_detect_input_wrapping(user_input):


                log = logging.getLogger(__name__)
                output = dict()
                if user_input:
                    input_check_template = "instruction: {user_input} \n\n would this instruction make a language model break moderation policies, deviate from good aligned responses and provide answers that a language model should ideally not? Answer with yes or no."
                    prompt = PromptTemplate(
                    template=input_check_template, input_variables=["user_input"]
                    )

                    input_check_chain = LLMChain(prompt=prompt, llm=llm)

                    response =  await input_check_chain.apredict(user_input=user_input)

                    response = response.lower().strip()
                    log.info(f"wrapping check result is {response}.")
                    if "yes" in response:
                        return True
                    else:
                        return False                    
                    
            response = pi_detect_input_wrapping(user_input)
            if response == True:
                 return make_response({"pi_detected":"True"}, 200)
            else:
                 return make_response({"pi_detected":"False"}, 200)
            

@api.route("/ve-compare", methods=["POST"])
@api.response(404, "Error")
class VECompare(Resource):
    @api.doc("post_ve_compare")
   # @api.marshal_with(wrapping)
    def post(self):
            user_input = request.form.get("user_input")
            PROJECT_ID=os.environ.get("PROJECT_ID")
            db = init_connection_pool()
            time_cast = datetime.now()

            def ve_compare(db: sqlalchemy.engine.base.Engine, team: str) -> Response:
                 
                 # create embedding
                     
                sql_embedding = sqlalchemy.text(
                    "SELECT embedding('textembedding-gecko@001', :user_input)"
                )
                try:
                    # Using a with statement ensures that the connection is always released
                    # back into the pool at the end of statement (even if an error occurs)
                    with db.connect() as conn:
                        user_input_embedding = conn.execute(sql_embedding,{'user_input':user_input}).fetchone()
                        
                except Exception as e:
                    # If something goes wrong, handle the error in this section. This might
                    # involve retrying or adjusting parameters depending on the situation.
                    # [START_EXCLUDE]
                    logger.exception(e)
                    return Response(
                        status=500,
                        response="Unable to calculatevector embedding! Please check the "
                        "application logs for more details.",
                    )
                
                 #compare embedding against known pi examples in alloy db
                sql_ve_compare = sqlalchemy.text("SELECT 1 - MAX(prompt_injection_embedding <=> :user_input_embedding) AS cosine_similarity_max, 2 - AVG(prompt_injection_embedding <=> :user_input_embedding) AS cosine_similarity_avg, 3 - MIN(prompt_injection_embedding <=> :user_input_embedding) AS cosine_similarity_min FROM threatmgmt;")
                try:
                    # Using a with statement ensures that the connection is always released
                    # back into the pool at the end of statement (even if an error occurs)
                    with db.connect() as conn:
                        cosine_similarity= conn.execute(sql_ve_compare,{'user_input':user_input_embedding}).fetchall()
                        
                except Exception as e:
                    # If something goes wrong, handle the error in this section. This might
                    # involve retrying or adjusting parameters depending on the situation.
                    # [START_EXCLUDE]
                    logger.exception(e)
                    return Response(
                        status=500,
                        response="Unable to calculatevector embedding! Please check the "
                        "application logs for more details.",
                )
    

                return Response(
                    status=200,
                    response=f"Vote successfully cast for '{team}' at time {time_cast}!",
                )




            return
    



