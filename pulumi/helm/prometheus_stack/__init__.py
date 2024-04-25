from os.path import dirname
from pathlib import Path
from pulumi import Config, export, ResourceOptions
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs
from pulumi_kubernetes.yaml.v2 import ConfigGroup
from requests import get


class PrometheusStack:
    """
    PrometheusStack class creates a prometheus stack using the kube-prometheus-stack helm chart.

    :param name: The name of the prometheus stack.
    :param depends_on: The resources that the prometheus stack depends on.

    The chart can be configured by setting the following values in the pulumi configuration:

    - `helm:prometheusStackAdminPassword`: The admin password for the grafana dashboard.
    - `helm:prometheusStackAlertmanagerVolumeSize`: The size of the alertmanager volume.
    - `helm:prometheusStackCrdVersion`: The version of the prometheus stack crds.
    - `helm:prometheusStackEnabled`: A boolean value to enable or disable the prometheus stack.
    - `helm:prometheusStackHosts`: The hosts for the grafana ingress, sperated by comma.
    - `helm:prometheusStackPrometheusVolumeSize`: The size of the prometheus volume.
    - `helm:prometheusStackStorageClass`: The storage class to use for the prometheus stack.
    - `helm:prometheusStackUsePersistency`: A boolean value to enable or disable persistency for the prometheus stack.
    - `helm:prometheusStackVersion`: The version of the prometheus stack helm chart.
    - `infrastructure:environment`: The environment in which the chart is running.
    """


    def __init__(self, name: str, depends_on: list = []):
        config = Config()
        helm_config = Config("helm")

        if helm_config.get_bool("prometheusStackEnabled", default=False):
            crd_version = helm_config.require("prometheusStackCrdVersion")
            crd_base_url = (
                f"https://raw.githubusercontent.com/"
                f"prometheus-operator/prometheus-operator/"
                f"{helm_config.require("prometheusStackCrdVersion")}"
                f"/example/prometheus-operator-crd/"
            )
            crd_files = [
                "monitoring.coreos.com_alertmanagerconfigs.yaml",
                "monitoring.coreos.com_alertmanagers.yaml",
                "monitoring.coreos.com_podmonitors.yaml",
                "monitoring.coreos.com_probes.yaml",
                "monitoring.coreos.com_prometheusagents.yaml",
                "monitoring.coreos.com_prometheuses.yaml",
                "monitoring.coreos.com_prometheusrules.yaml",
                "monitoring.coreos.com_scrapeconfigs.yaml",
                "monitoring.coreos.com_servicemonitors.yaml",
                "monitoring.coreos.com_thanosrulers.yaml",
            ]
            namespace = f"{config.require("environment")}-{name}"
            chart_values = {
                "crds": {
                    "enabled": False,
                },
                "grafana": {
                    "adminPassword": helm_config.require(
                        "prometheusStackAdminPassword"
                    ),
                    "ingress": {
                        "enabled": True,
                        "hosts": helm_config.require("prometheusStackHosts").split(","),
                    },
                },
            }

            if helm_config.get_bool("prometheusStackUsePersistency", default=False):
                chart_values |= {
                    "alertmanager": {
                        "alertmanagerSpec": {
                            "storage": {
                                "volumeClaimTemplate": {
                                    "spec": {
                                        "storageClassName": helm_config.require("prometheusStackStorageClass"),
                                        "accessModes": ["ReadWriteOnce"],
                                        "resources": {
                                            "requests": {
                                                "storage": helm_config.require("prometheusStackAlertmanagerVolumeSize"),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    "prometheus": {
                        "prometheusSpec": {
                            "storageSpec": {
                                "volumeClaimTemplate": {
                                    "spec": {
                                        "storageClassName": helm_config.require("prometheusStackStorageClass"),
                                        "accessMode": ["ReadWriteOnce"],
                                        "resources": {
                                            "requests": {
                                                "storage": helm_config.require("prometheusStackPrometheusVolumeSize"),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                }

            chart_version = helm_config.require("prometheusStackVersion")
            self.__crds__(name, crd_version, crd_base_url, crd_files)
            self.__namespace__(name, namespace)
            self.__release__(name, namespace, chart_version, chart_values)
            self.__exports__()


    def __crds__(self, name: str, version: str, base_url: str, files: list[str]):
        cur_dir = dirname(__file__)
        crd_dir = f"{cur_dir}/.crds/{version}"

        with open(f"{cur_dir}/.gitignore", "w") as f:
            f.write(".crds/")

        Path(crd_dir).mkdir(parents=True, exist_ok=True)
        for file in files:
            file_path = f"{crd_dir}/{file}"
            if not Path(file_path).is_file():
                with open(file_path, "w") as f:
                    f.write(get(f"{base_url}{file}").text)

        self.crds = ConfigGroup(f"{name}-crds", files=[f"{crd_dir}/*.yaml"])


    def __namespace__(self, name: str, namespace: str):
        self.namespace = Namespace(
            f"{name}-namespace",
            metadata={
                "name": namespace,
            },
        )


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


    def __exports__(self):
        export("prometheusStack/appVersion", self.release.status.apply(lambda s: s.app_version))
        export(
            "prometheusStack/domains",
            self.release.values["grafana"]["ingress"]["hosts"],
        )
        export("prometheusStack/id", self.release.id)
        export("prometheusStack/namespace", self.release.status.apply(lambda s: s.namespace))
        export("prometheusStack/revision", self.release.status.apply(lambda s: s.revision))
        export("prometheusStack/status", self.release.status.apply(lambda s: s.status))
        export("prometheusStack/version", self.release.status.apply(lambda s: s.version))
