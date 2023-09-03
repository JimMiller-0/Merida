from api.services.input.promptinjection import api as input_pi_checks_ns
from api.services.input.safety import api as input_safety_ns
from api.services.output.out_safety import api as output_safety_ns
from api.services.threatmgmt import api as threatmgmt_ns

from flask import Blueprint
from flask_restx import Api

blueprint = Blueprint("api", __name__)

api = Api(
    blueprint, title="Merida API", version="1.0", description="LLM Application Security Service API"
)


api.add_namespace(input_pi_checks_ns, path="/input/pi")
api.add_namespace(input_safety_ns, path="/input/safety")
api.add_namespace(output_safety_ns, path="/output/safety")
api.add_namespace(threatmgmt_ns, path="/threatmgmt")