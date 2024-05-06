from helpers import StringConverter
import pytest


@pytest.mark.parametrize(
    "input,expected",
    [
        ("hello_world", "helloWorld"),
        ("hello-world", "helloWorld"),
        ("helloWorld", "helloWorld"),
        ("HelloWorld", "helloWorld"),
        ("hello1world", "hello1world"),
    ],
)
def test_camel_case(input: str, expected: str):
    print(f"Input: {input}")
    output = StringConverter.camel_case(input)
    print(f"Output: {output}")
    assert output == expected
