from os.path import dirname
from pathlib import Path
from pulumi import ComponentResource, Config, export, ResourceOptions
from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs
from pulumi_kubernetes.yaml.v2 import ConfigGroup
from requests import get


class LgtmStack(ComponentResource):

    def __init__(
        self,
        name: str,
        props: dict = None,
        opts: ResourceOptions = None,
        remote: bool = False,
    ) -> None:
        """Create a LGTM stack using helm charts. The stack contains

        - Loki for logs
        - Grafana for visualizations
        - tempo for traces
        - Mimir for metrics

        Args:
            name (str): The name of the LGTM stack. Will be used for the namespace and as prefix for the resources.
            props (dict, optional): A list of input properties to use as inputs for the resource.
            opts (ResourceOptions, optional): A set of pulumi.ResourceOptions to use for this resource.
            remote (bool, optional): True if this is a remote component resource.

        Stack Options:
            `helm:lgtmStackChartVersion`: The version of the LGTM stack helm chart. Defaults to latest version.
            `helm:lgtmStackMinioEnabled`: A boolean value to enable or disable minio. Defaults to False.
            `helm:lgtmStackStorageClass`: The storage class to use for the LGTM stack. Defaults to "".

        Returns:
            None
        """
        super().__init__("my:components:LgtmStack", name, props, opts, remote)
        config = Config("helm")
        chart_values = self.create_chart_values(config)
        chart_version = config.get("lgtmStackChartVersion", None)
        self.namespace = self.create_namespace(name)
        self.release = self.create_release(name, chart_version, chart_values)
        self.create_exports(name)

    def create_chart_values(self, config: Config) -> dict:
        return {
            "loki": {
                "schemaConfig": {
                    "configs": [
                        {
                            "from": "2024-04-01",
                            "object_store": "s3",
                            "store": "tsdb",
                            "schema": "v13",
                            "index": {
                                "prefix": "index_",
                                "period": "24h",
                            },
                        },
                    ],
                },
            }
        }

    def create_exports(self, name: str) -> None:
        export(
            f"{name}/appVersion",
            self.release.status.apply(lambda s: s.app_version),
        )
        export(
            f"{name}/namespace",
            self.release.status.apply(lambda s: s.namespace),
        )
        export(f"{name}/revision", self.release.status.apply(lambda s: s.revision))
        export(f"{name}/status", self.release.status.apply(lambda s: s.status))
        export(f"{name}/version", self.release.status.apply(lambda s: s.version))

    def create_namespace(self, name: str) -> Namespace:
        return Namespace(
            f"{name}-namespace",
            metadata={"name": f"{name}"},
            opts=ResourceOptions(parent=self),
        )

    def create_release(self, name: str, version: str, values: dict = {}) -> Release:
        return Release(
            f"{name}",
            ReleaseArgs(
                chart="loki",
                create_namespace=False,
                dependency_update=True,
                namespace=self.namespace.metadata["name"],
                repository_opts=RepositoryOptsArgs(
                    repo="https://grafana.github.io/helm-charts",
                ),
                skip_crds=True,
                values=values,
                version=version,
            ),
            opts=ResourceOptions(
                depends_on=[
                    self.namespace,
                ],
                parent=self.namespace,
            ),
        )
