# CERTIFICATE_FOR_SERVICE_TEST_TLD
# KEY_FOR_SERVICE_TEST_TLD

import pytest
from ..main import AcmeDistributor


@pytest.fixture
def acme_distributor():
    acme_file_path = "acme.json"
    host = "test_host"
    user = "test_user"
    return AcmeDistributor(acme_file_path, host, user)


def test_acme_distributor_read_acme_files(acme_distributor):
    acme_distributor.read_acme_files()
    assert acme_distributor.cert is "CERTIFICATE_FOR_SERVICE_TEST_TLD"
    assert acme_distributor.key is "KEY_FOR_SERVICE_TEST_TLD"
