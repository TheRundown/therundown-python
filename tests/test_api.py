import pytest

from rundown.rundown import Rundown as rd


@pytest.fixture
def rundown():
    return rd()


def test_some_route(rundown):
    assert rundown.some_route() == "hello from Rundown"
