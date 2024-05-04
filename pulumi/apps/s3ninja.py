from components import K8sDeployment
import pulumi


class S3Ninja(K8sDeployment):

    def configure(self, name: str):
        config = pulumi.Config(name)

        image_version = config.get("imageVersion", "latest")
        ingress_host = config.require("ingressHost")

        self.image_name = "chronicc/s3ninja"
        self.image_version = image_version
        self.ingress_annotations = {
            "nginx.ingress.kubernetes.io/app-root": "/ui",
        }
        self.ingress_enabled = True
        self.ingress_host = ingress_host
        self.service_target_port = 9000
