from components import HelmRelease


class MinioOperator(HelmRelease):

    def configure(self, name: str):
        config = self.load_config(name)

        chart_version = config.require("chartVersion")

        self.chart_name = "operator"
        self.chart_repo = "https://operator.min.io/"
        self.chart_version = chart_version
