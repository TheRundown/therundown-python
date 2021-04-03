import os
import json

import pytest

from rundown.rundown import Rundown


@pytest.fixture(scope="module")
def vcr_config():
    # Hide API keys in VCR cassettes.
    return {
        "filter_headers": [("x-rapidapi-key", "DUMMY"), ("X-TheRundown-Key", "DUMMY")]
    }


def patched_build_url_and_get_json(request, original_fn):
    # Save request JSON body to file with same name as test cassette.
    def _patched(*segments, **params):
        data = original_fn(*segments, **params)
        with open(f"tests/json/{request.node.name}.json", "w") as f:
            json.dump(data, f, indent=2)

        return data

    return _patched


@pytest.fixture
def rundown(request, monkeypatch):
    r = Rundown(os.getenv("RAPIDAPI_KEY"))
    original_fn = r._build_url_and_get_json
    # Patch method in order to save JSON data along with VCR cassette.
    monkeypatch.setattr(
        r,
        "_build_url_and_get_json",
        patched_build_url_and_get_json(request, original_fn),
    )
    return r
