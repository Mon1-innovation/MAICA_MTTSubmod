#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import tempfile
import types

sys.path.insert(0, os.path.dirname(__file__))

requests_stub = types.ModuleType("requests")
requests_stub.get = None
requests_stub.post = None
sys.modules["requests"] = requests_stub

import mtts_package


class FakeResponse(object):
    status_code = 200
    content = b"ogg-data"

    def json(self):
        raise ValueError("not json audio")


def test_generate_uses_instance_timeout():
    calls = []
    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return FakeResponse()

    cache_dir = tempfile.mkdtemp()
    try:
        mtts_package.requests.get = fake_get
        instance = mtts_package.MTTS(
            url="https://example.invalid/tts/",
            token="token",
            cache_path=cache_dir,
        )
        instance.generate_timeout = 23

        result = instance.generate("hello", label_name="label")

        assert result.is_success()
        assert calls
        assert calls[0][1]["timeout"] == 23
    finally:
        mtts_package.requests.get = None
        shutil.rmtree(cache_dir)


if __name__ == "__main__":
    test_generate_uses_instance_timeout()
    print("test_generate_uses_instance_timeout passed")
