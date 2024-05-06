from components import HelmRelease


class PrometheusStack(HelmRelease):

    def configure(self, name: str):
        config = self.load_config(name)

        adminPassword = config.require("adminPassword")
        chart_version = config.require("version")
        crd_version = config.require("crdVersion")
        ingressHost = config.require("ingressHost")
        usePersistency = config.get_bool("usePersistency", default=False)

        self.chart_name = "kube-prometheus-stack"
        self.chart_repo = "https://prometheus-community.github.io/helm-charts"
        self.crd_version = crd_version
        self.crd_base_url = (
            f"https://raw.githubusercontent.com/"
            f"prometheus-operator/prometheus-operator/"
            f"{crd_version}"
            f"/example/prometheus-operator-crd/"
        )
        self.crd_files = [
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
        self.chart_values = {
            "crds": {
                "enabled": False,
            },
            "grafana": {
                "adminPassword": adminPassword,
                "ingress": {
                    "enabled": True,
                    "hosts": [ingressHost],
                },
            },
        }
        self.chart_version = chart_version

        if usePersistency:
            alertmanagerVolumeSize = config.require("alertmanagerVolumeSize")
            prometheusVolumeSize = config.require("prometheusVolumeSize")
            storageClass = config.require("storageClass")

            self.chart_values |= {
                "alertmanager": {
                    "alertmanagerSpec": {
                        "storage": {
                            "volumeClaimTemplate": {
                                "spec": {
                                    "storageClassName": storageClass,
                                    "accessModes": ["ReadWriteOnce"],
                                    "resources": {
                                        "requests": {
                                            "storage": alertmanagerVolumeSize,
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
                                    "storageClassName": storageClass,
                                    "accessMode": ["ReadWriteOnce"],
                                    "resources": {
                                        "requests": {
                                            "storage": prometheusVolumeSize,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            }
