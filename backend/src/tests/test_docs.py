"""Tests to verify that the client API documentation matches the actual API."""

import json
import re

import pytest

from src.infrastructure.api.docs.content import ENDPOINTS, get_endpoints_by_group
from src.main import CLIENT_ENDPOINT_WHITELIST, get_client_openapi_schema


class TestDocsPages:
    """Verify documentation pages load correctly."""

    def test_index_page_loads(self, client):
        resp = client.get("/api/docs")
        assert resp.status_code == 200
        assert "Extracto API" in resp.text

    def test_each_endpoint_page_loads(self, client):
        for ep in ENDPOINTS:
            resp = client.get(f"/api/docs/{ep.slug}")
            assert resp.status_code == 200, f"Page /api/docs/{ep.slug} failed"
            assert ep.title in resp.text

    def test_invalid_slug_returns_404(self, client):
        resp = client.get("/api/docs/nonexistent-endpoint")
        assert resp.status_code == 404

    def test_openapi_json_loads(self, client):
        resp = client.get("/api/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "paths" in data
        assert "info" in data


class TestDocsMatchWhitelist:
    """Verify documented endpoints match the CLIENT_ENDPOINT_WHITELIST in main.py."""

    def test_all_whitelisted_endpoints_are_documented(self):
        """Every endpoint in CLIENT_ENDPOINT_WHITELIST should have a docs page."""
        documented = {(ep.method, ep.path) for ep in ENDPOINTS}
        for method, path in CLIENT_ENDPOINT_WHITELIST:
            assert (method, path) in documented, (
                f"({method}, {path}) is in CLIENT_ENDPOINT_WHITELIST "
                f"but missing from docs content.py"
            )

    def test_all_documented_endpoints_are_whitelisted(self):
        """Every documented endpoint should exist in CLIENT_ENDPOINT_WHITELIST."""
        for ep in ENDPOINTS:
            assert (ep.method, ep.path) in CLIENT_ENDPOINT_WHITELIST, (
                f"({ep.method}, {ep.path}) is documented in docs "
                f"but missing from CLIENT_ENDPOINT_WHITELIST"
            )


class TestDocsMatchOpenAPI:
    """Verify documented endpoints match the actual OpenAPI spec."""

    @pytest.fixture()
    def openapi_spec(self):
        return get_client_openapi_schema()

    def test_all_documented_paths_exist_in_openapi(self, openapi_spec):
        """Every documented endpoint should exist in the OpenAPI spec."""
        spec_paths = openapi_spec.get("paths", {})
        for ep in ENDPOINTS:
            assert ep.path in spec_paths, (
                f"Documented path {ep.path} not found in OpenAPI spec. "
                f"Available: {list(spec_paths.keys())}"
            )
            methods = spec_paths[ep.path]
            assert ep.method.lower() in methods, (
                f"Documented method {ep.method} for {ep.path} not in OpenAPI. "
                f"Available: {list(methods.keys())}"
            )

    def test_documented_query_params_match_openapi(self, openapi_spec):
        """Query parameters documented should exist in the OpenAPI spec."""
        spec_paths = openapi_spec.get("paths", {})
        for ep in ENDPOINTS:
            query_params = [p for p in ep.params if p.location == "query"]
            if not query_params:
                continue

            operation = spec_paths.get(ep.path, {}).get(ep.method.lower(), {})
            spec_params = operation.get("parameters", [])
            spec_query_names = {
                p["name"] for p in spec_params if p.get("in") == "query"
            }

            for param in query_params:
                assert param.name in spec_query_names, (
                    f"Documented query param '{param.name}' for "
                    f"{ep.method} {ep.path} not found in OpenAPI. "
                    f"Available: {spec_query_names}"
                )

    def test_documented_path_params_match_openapi(self, openapi_spec):
        """Path parameters documented should exist in the OpenAPI spec."""
        spec_paths = openapi_spec.get("paths", {})
        for ep in ENDPOINTS:
            path_params = [p for p in ep.params if p.location == "path"]
            if not path_params:
                continue

            operation = spec_paths.get(ep.path, {}).get(ep.method.lower(), {})
            spec_params = operation.get("parameters", [])
            spec_path_names = {
                p["name"] for p in spec_params if p.get("in") == "path"
            }

            for param in path_params:
                assert param.name in spec_path_names, (
                    f"Documented path param '{param.name}' for "
                    f"{ep.method} {ep.path} not found in OpenAPI. "
                    f"Available: {spec_path_names}"
                )

    def test_documented_body_params_match_openapi(self, openapi_spec):
        """Body parameters documented should exist in the request body schema."""
        spec_paths = openapi_spec.get("paths", {})
        schemas = openapi_spec.get("components", {}).get("schemas", {})

        for ep in ENDPOINTS:
            body_params = [p for p in ep.params if p.location == "body"]
            if not body_params:
                continue

            operation = spec_paths.get(ep.path, {}).get(ep.method.lower(), {})
            request_body = operation.get("requestBody", {})
            if not request_body:
                continue

            # Resolve the schema (may be a $ref)
            content = request_body.get("content", {})
            json_schema = content.get("application/json", {}).get("schema", {})

            if "$ref" in json_schema:
                ref_name = json_schema["$ref"].split("/")[-1]
                json_schema = schemas.get(ref_name, {})

            schema_props = json_schema.get("properties", {})
            if not schema_props:
                continue

            for param in body_params:
                # Skip file params (multipart)
                if "file" in param.type.lower() or "multipart" in param.type.lower():
                    continue
                assert param.name in schema_props, (
                    f"Documented body param '{param.name}' for "
                    f"{ep.method} {ep.path} not found in OpenAPI schema. "
                    f"Available: {list(schema_props.keys())}"
                )

    @staticmethod
    def _normalize_json(text: str) -> str:
        """Replace placeholder patterns so the JSON can be parsed."""
        # Replace "value..." patterns inside strings
        text = re.sub(r'"([^"]*)\.\.\."', r'"\1_placeholder"', text)
        # Replace { ... } (object placeholder) with empty object
        text = re.sub(r'\{\s*\.\.\.\s*\}', '{}', text)
        # Replace standalone ...  (e.g. as object value)
        text = text.replace("...", '"__placeholder__"')
        return text

    def test_response_bodies_are_valid_json(self):
        """All documented response bodies should be valid JSON."""
        for ep in ENDPOINTS:
            if not ep.response_body:
                continue
            body = self._normalize_json(ep.response_body)
            try:
                json.loads(body)
            except json.JSONDecodeError:
                pytest.fail(
                    f"Response body for {ep.method} {ep.path} "
                    f"is not valid JSON:\n{ep.response_body}"
                )

    def test_request_bodies_are_valid_json(self):
        """All documented request bodies should be valid JSON (where applicable)."""
        for ep in ENDPOINTS:
            if not ep.request_body:
                continue
            body = ep.request_body
            # Skip multipart descriptions
            if "multipart" in body.lower():
                continue
            body = self._normalize_json(body)
            try:
                json.loads(body)
            except json.JSONDecodeError:
                pytest.fail(
                    f"Request body for {ep.method} {ep.path} "
                    f"is not valid JSON:\n{ep.request_body}"
                )


class TestDocsContent:
    """Verify documentation content quality."""

    def test_all_endpoints_have_descriptions(self):
        for ep in ENDPOINTS:
            assert ep.description, f"{ep.method} {ep.path} has no description"

    def test_all_endpoints_have_at_least_one_example(self):
        for ep in ENDPOINTS:
            assert len(ep.examples) >= 1, (
                f"{ep.method} {ep.path} has no code examples"
            )

    def test_all_endpoints_have_unique_slugs(self):
        slugs = [ep.slug for ep in ENDPOINTS]
        assert len(slugs) == len(set(slugs)), (
            f"Duplicate slugs found: {[s for s in slugs if slugs.count(s) > 1]}"
        )

    def test_all_groups_have_endpoints(self):
        groups = get_endpoints_by_group()
        for gid, glabel, eps in groups:
            assert len(eps) > 0, f"Group '{glabel}' has no endpoints"

    def test_sidebar_nav_has_all_endpoints(self, client):
        """The sidebar on the index page should link to every endpoint."""
        resp = client.get("/api/docs")
        for ep in ENDPOINTS:
            assert f"/api/docs/{ep.slug}" in resp.text, (
                f"Sidebar missing link to /api/docs/{ep.slug}"
            )


class TestDynamicBaseUrl:
    """Verify the API base URL placeholder is replaced with the actual host."""

    def test_index_has_no_placeholder(self, client):
        resp = client.get("/api/docs")
        assert "$$API_BASE$$" not in resp.text, "Placeholder not replaced on index"

    def test_endpoint_pages_have_no_placeholder(self, client):
        for ep in ENDPOINTS:
            resp = client.get(f"/api/docs/{ep.slug}")
            assert "$$API_BASE$$" not in resp.text, (
                f"Placeholder not replaced on /api/docs/{ep.slug}"
            )

    def test_index_contains_resolved_url(self, client):
        """The rendered page should contain the testserver host, not a placeholder."""
        resp = client.get("/api/docs")
        assert "http://testserver" in resp.text

    def test_endpoint_page_contains_resolved_url(self, client):
        resp = client.get("/api/docs/extract")
        assert "http://testserver" in resp.text


class TestIndexExamples:
    """Verify the full examples on the index page show the complete flow."""

    def test_python_example_lists_extractors(self, client):
        resp = client.get("/api/docs")
        assert "/extractors" in resp.text, "Python example missing GET /extractors"

    def test_python_example_uses_extractor_id(self, client):
        resp = client.get("/api/docs")
        assert "extractor_id" in resp.text, (
            "Python example missing extractor_id in extract call"
        )

    def test_quick_start_mentions_extractor_step(self, client):
        resp = client.get("/api/docs")
        assert "Elegir un extractor" in resp.text or "Elegir extractor" in resp.text, (
            "Quick start missing extractor selection step"
        )
