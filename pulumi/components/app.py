import helpers
import pulumi
import re


class App(pulumi.ComponentResource):

    def configure(self, name: str):
        """This method is run at the start of initializing the class and can be used to
        configure instance attributes. Use the load_config method to load the configuration
        for the stack."""
        pass

    def export(self, name: str, value: any) -> None:
        pulumi.export(
            f"{helpers.StringConverter.camel_case(self.__class__.__name__)}/{name}",
            value,
        )

    def load_config(self, name: str) -> pulumi.Config:
        """Load the stack configuration. The name is converted to camel case to align
        with the pulumi stack config standard."""
        return pulumi.Config(helpers.StringConverter.camel_case(name))
