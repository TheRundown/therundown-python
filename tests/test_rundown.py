import pytest

from rundown.rundown import _Auth, _RundownAuth, _RapidAPIAuth


def test_auth_factory():
    a = _Auth.factory("rapidapi", "apikey")
    assert isinstance(a, _RapidAPIAuth)
    a = _Auth.factory("rundown", "apikey")
    assert isinstance(a, _RundownAuth)

    with pytest.raises(ValueError):
        _Auth.factory("foo", "apikey")
