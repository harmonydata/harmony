from diagrams import Cluster, Diagram
from diagrams.azure.compute import AppServices
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB
from diagrams.aws.network import Route53
from diagrams.generic.os import Ubuntu
from diagrams.generic.device import Tablet
from diagrams.programming.language import Python, Java
from diagrams.onprem.container import Docker
from diagrams.aws.compute import Lambda
from diagrams.generic.compute import Rack
from diagrams.aws.integration import StepFunctions
from diagrams.aws.network import APIGateway

with Diagram("Deployed Harmony architecture", show=False):

    browser = Tablet("Front end (React)")
    api = APIGateway("AWS API Gateway")
    step = StepFunctions("Step function\nExpress state machine")
    tika = Lambda("Tika app service\nfor processing PDFs\n(Java)")
    fileproc = Lambda("File processor")
    matcher = Lambda("Matcher")
    vectoriser = Rack("Vectoriser\n(HuggingFace API)")

    browser >> api >> step >> tika
    step >> fileproc
    api >> matcher >> vectoriser
