import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

spec = importlib.util.spec_from_file_location(
    "academic_search", Path(__file__).parents[1] / "scripts" / "academic_search.py"
)
search = importlib.util.module_from_spec(spec)
spec.loader.exec_module(search)


class OpenAlexRequests(unittest.TestCase):
    def response(self, *_args, **_kwargs):
        return io.BytesIO(json.dumps({"results": [], "message": {"items": []}}).encode())

    def test_key_covers_work_author_and_orcid_without_leaking_to_crossref(self):
        with patch.dict(os.environ, {"OPENALEX_API_KEY": "test-key"}), patch.object(
            search.urllib.request, "urlopen", side_effect=self.response
        ) as opened:
            search.search("heat transfer")
            search.fetch_author_candidates("Example Author")
            search.resolve_by_orcid("0000-0002-1825-0097")
            search.crossref_search("heat transfer")
        for call in opened.call_args_list[:3]:
            req = call.args[0]
            self.assertEqual(req.get_header("Authorization"), "Bearer test-key")
            self.assertNotIn("test-key", req.full_url)
        self.assertIsNone(opened.call_args_list[3].args[0].get_header("Authorization"))

    def test_anonymous_queries_do_not_require_a_key(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            search.urllib.request, "urlopen", side_effect=self.response
        ) as opened:
            self.assertEqual(search.search("heat transfer"), [])
        self.assertIsNone(opened.call_args.args[0].get_header("Authorization"))

    def test_reranked_and_author_requests_respect_page_limit(self):
        with patch.object(search.urllib.request, "urlopen", side_effect=self.response) as opened:
            search.search("heat transfer", limit=50, sort="cited_by_count")
            search.fetch_author_candidates("Example Author", per_page=200)
        for call in opened.call_args_list:
            params = parse_qs(urlparse(call.args[0].full_url).query)
            self.assertEqual(params["per_page"], ["100"])


if __name__ == "__main__":
    unittest.main()
