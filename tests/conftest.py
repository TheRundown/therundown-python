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
    JSON_DIR = "tests/json"

    def build_file_name():
        """Match file name from pytest-vcr."""
        path_segments = request.node.nodeid.split("::")
        class_name = path_segments[-2]
        node_name = path_segments[-1]
        return f"{JSON_DIR}/{class_name}.{node_name}.json"
        pass

    # Save request JSON body to file with same name as test cassette.
    def patched(*segments, **params):
        data = original_fn(*segments, **params)
        with open(build_file_name(), "w") as f:
            json.dump(data, f, indent=2)

        return data

    return patched


@pytest.fixture
def rundown(request, monkeypatch):
    r = Rundown(os.getenv("RAPIDAPI_KEY"), timezone="America/Phoenix")
    original_fn = r._build_url_and_get_json
    # Patch method in order to save JSON data along with VCR cassette.
    monkeypatch.setattr(
        r,
        "_build_url_and_get_json",
        patched_build_url_and_get_json(request, original_fn),
    )
    return r
