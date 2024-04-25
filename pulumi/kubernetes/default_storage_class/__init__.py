from pulumi import Config, export
from pulumi_kubernetes.storage.v1 import StorageClassPatch


class DefaultStorageClass:

    def __init__(self, name: str):
        config = Config()
        if config.require_bool("isMinikube"):
            self.__minikube__(name)

    def __minikube__(self, name: str):
        StorageClassPatch(
            f"{name}-old-default-disabled",
            metadata={
                "annotations": {
                    "pulumi.com/patchForce": "true",
                    "storageclass.kubernetes.io/is-default-class": "false",
                },
                "name": "standard",
            },
        )
        StorageClassPatch(
            f"{name}-new-default",
            metadata={
                "annotations": {"storageclass.kubernetes.io/is-default-class": "true"},
                "name": "csi-hostpath-sc",
            },
        )
        export("kubernetes/defaultStorageClass", "csi-hostpath-sc")
