from diagrams import Cluster, Diagram
from diagrams.azure.compute import AppServices
from diagrams.aws.database import ElastiCache, RDS
from diagrams.aws.network import ELB
from diagrams.aws.network import Route53
from diagrams.generic.os import Ubuntu
from diagrams.generic.device import Tablet
from diagrams.programming.language import Python, Java
from diagrams.onprem.container import Docker

with Diagram("Harmony architecture (FastAPI)", show=False):

    browser = Tablet("Front end (React)")
    dash = Docker("Docker/FastAPI\n(Python,\ntransformer model)")
    tika = Java("Tika app service\nfor processing PDFs\n(Java)")

    browser >> dash >> tika
