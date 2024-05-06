from components import HelmRelease


class Loki(HelmRelease):

    def configure(self, name: str):
        config = self.load_config(name)

        chart_version = config.require("version")
        crd_version = config.require("crdVersion")
        s3_access_key_id = config.get("s3AccessKeyId", "loki")
        s3_protocol = config.get("s3Protocol", "https")
        s3_secret_access_key = config.get_secret("s3SecretAccessKey", "loki")
        s3_url = config.require("s3Url")
        s3_bucket = config.get("s3Bucket", "loki")

        self.chart_name = "loki"
        self.chart_repo = "https://grafana.github.io/helm-charts"
        self.chart_values = {
            "loki": {
                "auth_enabled": False,
                "minio": {
                    "enabled": False,
                },
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
                "storage": {
                    "type": "s3",
                    "s3": {
                        "s3": (
                            f"{s3_protocol}://{s3_access_key_id}:{s3_secret_access_key}"
                            f"@{s3_url}/{s3_bucket}"
                        ),
                        "s3ForcePathStyle": True,
                    },
                },
            },
        }
        self.chart_version = chart_version
        self.crd_base_url = (
            f"https://raw.githubusercontent.com/"
            f"grafana/helm-charts/"
            f"grafana-agent-operator-{crd_version}/"
            f"charts/agent-operator/crds/"
        )
        self.crd_version = crd_version
        self.crd_files = [
            "monitoring.coreos.com_podmonitors.yaml",
            "monitoring.coreos.com_probes.yaml",
            "monitoring.coreos.com_servicemonitors.yaml",
            "monitoring.grafana.com_grafanaagents.yaml",
            "monitoring.grafana.com_integrations.yaml",
            "monitoring.grafana.com_logsinstances.yaml",
            "monitoring.grafana.com_metricsinstances.yaml",
            "monitoring.grafana.com_podlogs.yaml",
        ]
