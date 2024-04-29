from os.path import dirname
from pathlib import Path
from pulumi import Config, export, ResourceOptions
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs
from pulumi_kubernetes.yaml.v2 import ConfigGroup
from requests import get


class RookCephOperator:
    """
    RookCephOperator class creates a rook ceph operator using the rook-ceph-operator helm chart.

    :param name: The name of the rook ceph operator.
    :param depends_on: The resources that the rook ceph operator depends on.
    """

    def __init__(self, name: str, depends_on: list = []):
        config = Config()
        helm_config = Config("helm")

        self.name = name
        self.namespace = f"{config.require("environment")}-{name}"
        self.depends_on = depends_on

        if helm_config.get_bool("rookCephOperatorEnabled", default=False):
            self.__release__()

    def __release__(
        self,
        name: str,
        namespace: str,
        version: str,
        values: dict = {},
        depends_on: list = [],
    ):
        self.release = Release(
            f"{name}-release",
            ReleaseArgs(
                chart="kube-prometheus-stack",
                create_namespace=False,
                dependency_update=True,
                namespace=namespace,
                repository_opts=RepositoryOptsArgs(
                    repo="https://prometheus-community.github.io/helm-charts",
                ),
                skip_crds=True,
                values=values,
                version=version,
            ),
            opts=ResourceOptions(
                depends_on=[
                    self.crds,
                    self.namespace,
                ]
                + depends_on
            ),
        )
