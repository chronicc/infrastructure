from pulumi_kubernetes.core.v1 import Namespace
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs
from pulumi_kubernetes.yaml.v2 import ConfigGroup
from requests import get
import git
import os
import pathlib
import pulumi
import re


class HelmRelease(pulumi.ComponentResource):
    """
    Instance Attributes:
        chart_name: (str): The name of the helm chart to deploy.
        chart_repo: (str): The repository URL of the helm chart.
        chart_values: (dict: {}): A dictionary of values to pass to the helm chart.
        chart_version: (str): The version of the helm chart to deploy.
        crd_base_url: (str: ""): The base URL where the CRDs can be downloaded.
        crd_files: (list: []): A list of CRD files to download.
        crd_version: (str: ""): The version of the CRDs to download.
    """

    _crds: ConfigGroup
    _namespace: Namespace
    _release: Release

    chart_name: str
    chart_repo: str
    chart_values: dict = {}
    chart_version: str
    crd_base_url: str = ""
    crd_files: list[str] = []
    crd_version: str = ""

    def __init__(
        self,
        name: str,
        props: dict = None,
        opts: pulumi.ResourceOptions = None,
        remote: bool = False,
    ) -> None:
        """A helm release deployed in a custom namespace. To configure the release,
        override the `configure` method.

        Args:
            name (str): The name of the LGTM stack. Will be used for the namespace and as
            prefix for the resources.
            props (dict, optional): A list of input properties to use as inputs for the
            resource.
            opts (ResourceOptions, optional): A set of pulumi.ResourceOptions to use for
            this resource.
            remote (bool, optional): True if this is a remote component resource.

        Returns:
            None
        """
        super().__init__(
            f"chronicc:apps:{self.__class__.__name__}", name, props, opts, remote
        )
        self.configure(name)
        self._crds = self.create_crds(name)
        self._namespace = self.create_namespace(name)
        self._release = self.create_release(name)

    def configure(self, name: str):
        """This method is run at the start of initializing the class and can be used to
        configure instance attributes. Use the load_config method to load the configuration
        for the stack."""
        pass

    def create_crds(self, name: str):
        if len(self.crd_files) > 0:
            repo_root = git.Repo(
                os.getcwd(), search_parent_directories=True
            ).working_tree_dir
            crd_dir = f"{repo_root}/.crds/{name}/{self.crd_version}"

            pathlib.Path(crd_dir).mkdir(parents=True, exist_ok=True)
            for file in self.crd_files:
                file_path = f"{crd_dir}/{file}"
                if not pathlib.Path(file_path).is_file():
                    with open(file_path, "w") as f:
                        f.write(get(f"{self.crd_base_url}{file}").text)

            crds = ConfigGroup(
                f"{name}-crds",
                files=[f"{crd_dir}/*.yaml"],
                opts=pulumi.ResourceOptions(parent=self),
            )
            self.export("customCrdsInstalled", "true")
        else:
            crds = ConfigGroup(
                f"{name}-no-crds",
                opts=pulumi.ResourceOptions(parent=self),
            )
            self.export("customCrdsInstalled", "false")
        return crds

    def create_namespace(self, name: str) -> Namespace:
        namespace = Namespace(
            f"{name}-namespace",
            metadata={"name": f"{name}"},
            opts=pulumi.ResourceOptions(parent=self),
        )
        self.export("namespace", namespace.metadata.apply(lambda m: m.name))
        return namespace

    def create_release(self, name: str):
        release = Release(
            f"{name}-release",
            ReleaseArgs(
                chart=self.chart_name,
                create_namespace=False,
                dependency_update=True,
                namespace=self._namespace.metadata.apply(lambda m: m.name),
                repository_opts=RepositoryOptsArgs(repo=self.chart_repo),
                skip_crds=True,
                values=self.chart_values,
                version=self.chart_version,
            ),
            opts=pulumi.ResourceOptions(
                depends_on=[self._crds, self._namespace],
                parent=self._namespace,
            ),
        )
        self.export("appVersion", release.status.apply(lambda s: s.app_version))
        self.export("id", release.id)
        self.export("revision", release.status.apply(lambda s: s.revision))
        self.export("status", release.status.apply(lambda s: s.status))
        self.export("version", release.status.apply(lambda s: s.version))
        return release

    def export(self, name: str, value: any) -> None:
        pulumi.export(f"{self.__class__.__name__}/{name}", value)

    def load_config(self, name: str) -> pulumi.Config:
        """Load the stack configuration. The name is converted to camel case to align
        with the pulumi stack config standard."""
        title_case = re.sub(r"(_|-)+", " ", name).title().replace(" ", "")
        camel_case = "".join([title_case[0].lower() + title_case[1:]])
        return pulumi.Config(camel_case)
