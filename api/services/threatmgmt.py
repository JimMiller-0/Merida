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

api = Namespace("threat_mgmt", description="managing threats seen in production")

threatmgmt = api.model(
    "Threat Management",
    {
        "id": fields.String(required=True, description="The dog identifier"),
        "name": fields.String(required=True, description="The dog name"),
    },
)

THREATMANAGEMENT = [
    {"id": "medor", "name": "Medor"},
]


@api.route("/")
class ThreatList(Resource):
    @api.doc("list_Threats")
    #@api.marshal_list_with(threatmgmt)
    def get(self):
        """List all dogs"""
        return make_response({"pi_detect":"This API is for detecting prompt injection in user input"}, 200)
