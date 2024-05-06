from pulumi_docker import RemoteImage
from pulumi_kubernetes.apps.v1 import (
    Deployment,
    DeploymentSpecArgs,
)
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
from pulumi_kubernetes.networking.v1 import (
    HTTPIngressPathArgs,
    HTTPIngressRuleValueArgs,
    Ingress,
    IngressBackendArgs,
    IngressRuleArgs,
    IngressServiceBackendArgs,
    IngressSpecArgs,
    ServiceBackendPortArgs,
)
from pulumi_kubernetes.meta.v1 import (
    LabelSelectorArgs,
    ObjectMetaArgs,
)
import components
import pulumi


class K8sDeployment(components.App):
    """
    Instance Attributes:
        image_name (str): The name of the container image to use.
        image_version (str): The version of the container image to use.
        ingress_annotations (dict: {}): A dictionary of annotations to apply to the ingress.
        ingress_enabled (bool: False): True if an ingress should be created for the deployment.
        ingress_host (str): The hostname for the ingress. Mandatory when ingress is enabled.
        ingress_path_type (str: "Prefix"): The path type for the ingress.
        ingress_path (str: "/"): The path for the ingress. Defaults to "/".
        service_source_port (int: 80): The source port for the service which is
        pointing to the internet.
        service_target_port (int: 80): The target port for the service which is
        exposed by the container.
    """

    _deployment: Deployment
    _namespace: Namespace
    _service: Service
    _ingress: Ingress

    image_name: str
    image_version: str
    ingress_annotations: dict = {}
    ingress_enabled: bool = False
    ingress_host: str
    ingress_path_type: str = "Prefix"
    ingress_path: str = "/"
    service_source_port: int = 80
    service_target_port: int = 80

    def __init__(
        self,
        name: str,
        props: dict = None,
        opts: pulumi.ResourceOptions = None,
        remote: bool = False,
    ) -> None:
        """A Kubernetes deployment with a service and an optional ingress. To configure
        the deployment, override the `configure` method.

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
        self._namespace = self.create_namespace(name)
        self._deployment = self.create_deployment(name)
        self._service = self.create_service(name)
        if self.ingress_enabled:
            self._ingress = self.create_ingress(name)
        self.export("component", "K8sDeployment")

    def create_deployment(self, name: str) -> Deployment:
        image = RemoteImage(
            f"{name}-image",
            name=f"{self.image_name}:{self.image_version}",
            opts=pulumi.ResourceOptions(parent=self),
        )
        deployment = Deployment(
            f"{name}-deployment",
            metadata=ObjectMetaArgs(
                labels={"app": name},
                name=name,
                namespace=self._namespace.metadata.apply(lambda m: m.name),
            ),
            opts=pulumi.ResourceOptions(
                depends_on=[self._namespace], parent=self._namespace
            ),
            spec=DeploymentSpecArgs(
                replicas=1,
                selector=LabelSelectorArgs(match_labels={"app": name}),
                template=PodTemplateSpecArgs(
                    metadata=ObjectMetaArgs(labels={"app": name}),
                    spec=PodSpecArgs(
                        containers=[
                            ContainerArgs(
                                name=name,
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
        self.export("imageName", self.image_name)
        self.export("imageVersion", self.image_version)
        return deployment

    def create_ingress(self, name: str) -> None:
        ingress = Ingress(
            f"{name}-ingress",
            metadata=ObjectMetaArgs(
                annotations=self.ingress_annotations,
                name=name,
                namespace=self._namespace.metadata.apply(lambda m: m.name),
            ),
            opts=pulumi.ResourceOptions(
                depends_on=[self._namespace], parent=self._namespace
            ),
            spec=IngressSpecArgs(
                rules=[
                    IngressRuleArgs(
                        host=self.ingress_host,
                        http=HTTPIngressRuleValueArgs(
                            paths=[
                                HTTPIngressPathArgs(
                                    backend=IngressBackendArgs(
                                        service=IngressServiceBackendArgs(
                                            name=name,
                                            port=ServiceBackendPortArgs(
                                                number=self.service_source_port,
                                            ),
                                        ),
                                    ),
                                    path=self.ingress_path,
                                    path_type=self.ingress_path_type,
                                )
                            ],
                        ),
                    )
                ],
            ),
        )
        self.export("ingressHost", ingress.spec.apply(lambda s: s.rules[0].host))
        self.export(
            "loadBalancerIp",
            ingress.status.apply(lambda s: s.load_balancer.ingress[0].ip),
        )
        return ingress

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
                labels={"app": name},
                name=name,
                namespace=self._namespace.metadata.apply(lambda m: m.name),
            ),
            opts=pulumi.ResourceOptions(
                depends_on=[self._namespace], parent=self._namespace
            ),
            spec=ServiceSpecArgs(
                ports=[
                    ServicePortArgs(
                        port=80,
                        protocol="TCP",
                        target_port=self.service_target_port,
                    ),
                ],
                selector={
                    "app": name,
                },
            ),
        )
        self.export("serviceIp", service.spec.apply(lambda s: s.cluster_ip))
        self.export(
            "servicePorts",
            service.spec.apply(lambda s: s.ports).apply(
                lambda p: [v["port"] for v in p]
            ),
        )
        return service
