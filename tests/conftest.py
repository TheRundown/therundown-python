import pytest

from rundown.rundown import Rundown


@pytest.fixture
def rundown():
    return Rundown()
