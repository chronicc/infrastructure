from components import HelmRelease


class MinioTenant(HelmRelease):

    def configure(self, name: str):
        config = self.load_config(name)

        chart_version = config.require("chartVersion")

        self.chart_name = "tenant"
        self.chart_repo = "https://operator.min.io/"
        self.chart_values = {
            "tenant": {
                "buckets": [
                    {
                        "name": config.get("bucketName", "loki"),
                        "objectLock": config.get("bucketObjectLock", False),
                    }
                ],
                "name": name,
                "pools": [
                    {
                        "name": config.get("poolName", "pool-0"),
                        "servers": config.get("poolServers", 1),
                        "size": config.get("poolSize", "1Gi"),
                        "volumesPerServer": config.get("poolVolumes", 1),
                    },
                ],
                "users": [
                    {
                        "CONSOLE_ACCESS_KEY": "loki",
                        "CONSOLE_SECRET_KEY": "loki",
                    }
                ],
            },
        }
        self.chart_version = chart_version
