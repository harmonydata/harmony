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


with Diagram("Harmony architecture (deployed)", show=False):

    browser = Tablet("User browser")
    dash = Lambda("File processor")
    tika = Lambda("Tika app service\nfor processing PDFs\n(Java)")
    matcher = Lambda("Matcher")
    vectoriser = Lambda("Vectoriser (HuggingFace)")

    browser >> dash >> tika
    browser >> matcher >> vectoriser
