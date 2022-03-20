import pytest

from main import main


@pytest.fixture
def fixtures():
    pass


def test_main():
    assert main() is None
