from components import K8sDeployment
import pulumi


class S3Ninja(K8sDeployment):

    def configure(self, name: str):
        config = pulumi.Config(name)
        self.image_name = "chronicc/s3ninja"
        self.image_version = config.get("imageVersion", "latest")
        self.ingress_annotations = {
            "nginx.ingress.kubernetes.io/app-root": "/ui",
        }
        self.ingress_enabled = True
        self.ingress_host = config.require("ingressHost")
        self.service_target_port = 9000
