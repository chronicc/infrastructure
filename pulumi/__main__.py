from helm.prometheus_stack import PrometheusStack
from kubernetes.default_storage_class import DefaultStorageClass
import apps
import pulumi

# ---------------------------------------------------------------------------------------
#
#   Configuration
#
# ---------------------------------------------------------------------------------------

# Minikube does not implement services of type `LoadBalancer`; require the user to specify
# if we're running on minikube, and if so, create only services of type ClusterIP.
config = pulumi.Config()
k8s_config = pulumi.Config("kubernetes")

pulumi.export("kubernetes/context", k8s_config.require("context"))
pulumi.export("project/environment", config.require("environment"))
pulumi.export("project/isMinikube", config.require_bool("isMinikube"))
pulumi.export("project/stack", pulumi.get_stack())


# ---------------------------------------------------------------------------------------
#
#   Kubernetes Cluster
#
# ---------------------------------------------------------------------------------------

default_storage_class = DefaultStorageClass("default-storage-class")

# ---------------------------------------------------------------------------------------
#
#   Applications
#
# ---------------------------------------------------------------------------------------

s3ninja = apps.S3Ninja("s3ninja")
minio_operator = apps.MinioOperator("minio-operator")
minio_tenant = apps.MinioTenant("minio-tenant-1")


# ---------------------------------------------------------------------------------------
#
#   Helm Charts
#
# ---------------------------------------------------------------------------------------

# prometheus_stack = PrometheusStack("kube-prometheus-stack")
