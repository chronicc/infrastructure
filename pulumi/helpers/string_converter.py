import re


class StringConverter:

    @staticmethod
    def camel_case(s: str) -> str:
        """Return the string in camel case."""
        s = re.sub(r"(_|-)+", " ", s)
        s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
        s = re.sub(r" ([a-zäöüA-ZÄÖÜ0-9])", lambda m: m.group(1).upper(), s)
        return "".join([s[0].lower() + s[1:]])
