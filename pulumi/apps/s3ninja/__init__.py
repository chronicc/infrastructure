from pulumi_docker import RemoteImage
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
    ContainerArgs,
    ContainerPortArgs,
    Namespace,
    PodSpecArgs,
    PodTemplateSpecArgs,
    Service,
    ServicePortArgs,
    ServiceSpecArgs,
)
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs
import pulumi


class S3Ninja(pulumi.ComponentResource):

    def __init__(
        self,
        name: str,
        props: dict = None,
        opts: pulumi.ResourceOptions = None,
        remote: bool = False,
    ) -> None:
        """Create a S3Ninja deployment.

        Args:
            name (str): The name of the LGTM stack. Will be used for the namespace and as prefix for the resources.
            props (dict, optional): A list of input properties to use as inputs for the resource.
            opts (ResourceOptions, optional): A set of pulumi.ResourceOptions to use for this resource.
            remote (bool, optional): True if this is a remote component resource.

        Stack Options:
            `s3ninja:imageVersion`: The version of the S3Ninja image to use.

        Returns:
            None
        """
        super().__init__("chronicc:apps:S3Ninja", name, props, opts, remote)
        self.config = pulumi.Config("s3ninja")
        self.namespace = self.create_namespace(name)
        self.deployment = self.create_deployment(name)
        self.service = self.create_service(name)

    def create_deployment(self, name: str) -> Deployment:
        version = self.config.get("imageVersion", "latest")
        image = RemoteImage(
            f"{name}-image",
            name=f"chronicc/s3ninja:{version}",
            opts=pulumi.ResourceOptions(parent=self),
        )
        deployment = Deployment(
            f"{name}-deployment",
            metadata=ObjectMetaArgs(
                labels={"app": "s3ninja"},
                name=name,
                namespace=self.namespace.metadata.apply(lambda m: m.name),
            ),
            opts=pulumi.ResourceOptions(
                depends_on=[self.namespace], parent=self.namespace
            ),
            spec=DeploymentSpecArgs(
                replicas=1,
                selector=LabelSelectorArgs(match_labels={"app": "s3ninja"}),
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(labels={"app": "s3ninja"}),
                    spec=PodSpecArgs(
                        containers=[
                            ContainerArgs(
                                name="s3ninja",
                                image=image.repo_digest,
                                ports=[
                                    ContainerPortArgs(container_port=9000),
                                ],
                            )
                        ]
                    ),
                ),
            ),
        )
        self.export("imageVersion", version)
        return deployment

    def create_namespace(self, name: str) -> Namespace:
        namespace = Namespace(
            f"{name}-namespace",
            metadata={"name": f"{name}"},
            opts=pulumi.ResourceOptions(parent=self),
        )
        self.export("namespace", namespace.metadata.apply(lambda m: m.name))
        return namespace

    def create_service(self, name: str) -> Service:
        service = Service(
            f"{name}-service",
            metadata=ObjectMetaArgs(
                labels={"app": "s3ninja"},
                name=name,
                namespace=self.namespace.metadata.apply(lambda m: m.name),
            ),
            opts=pulumi.ResourceOptions(
                parent=self.namespace, depends_on=[self.namespace]
            ),
            spec=ServiceSpecArgs(
                ports=[
                    ServicePortArgs(
                        port=80,
                        protocol="TCP",
                        target_port=9000,
                    ),
                ],
                selector={
                    "app": "s3ninja",
                },
            ),
        )
        self.export("serviceIp", service.spec.apply(lambda s: s.cluster_ip))
        self.export(
            "servicePorts",
            service.spec.apply(lambda s: s.ports).apply(
                lambda p: [k["port"] for k in p]
            ),
        )
        return service

    def export(self, name: str, value: any) -> None:
        pulumi.export(f"{self.__class__.__name__.lower()}/{name}", value)
