import pulumi
from helm.prometheus_stack import PrometheusStack

# --------------------------------------------------------------------------------------
#
#   Configuration
#
# --------------------------------------------------------------------------------------

# Minikube does not implement services of type `LoadBalancer`; require the user to specify if we're
# running on minikube, and if so, create only services of type ClusterIP.
config = pulumi.Config()
k8s_config = pulumi.Config("kubernetes")

pulumi.export("kubernetes/context", k8s_config.require("context"))
pulumi.export("project/environment", config.require("environment"))
pulumi.export("project/isMinikube", config.require_bool("isMinikube"))


# --------------------------------------------------------------------------------------
#
#   Helm Charts
#
# --------------------------------------------------------------------------------------

PrometheusStack("kube-prometheus-stack")
