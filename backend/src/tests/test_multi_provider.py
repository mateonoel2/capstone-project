from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.extractors.document_extractor import (
    PROVIDERS,
    DocumentExtractor,
    _resolve_provider,
)

TEST_PROMPT = "Extract fields from this document."
TEST_SCHEMA = {
    "type": "object",
    "properties": {"field": {"type": "string"}},
    "required": ["field"],
}


def _make_extractor(**kwargs):
    kwargs.setdefault("prompt", TEST_PROMPT)
    kwargs.setdefault("output_schema", TEST_SCHEMA)
    return DocumentExtractor(**kwargs)


class TestResolveProvider:
    @pytest.mark.parametrize(
        "model,expected_key",
        [
            ("claude-haiku-4-5-20251001", "ANTHROPIC_API_KEY"),
            ("claude-sonnet-4-6-20260326", "ANTHROPIC_API_KEY"),
            ("gpt-4o-mini", "OPENAI_KEY"),
            ("gpt-4o", "OPENAI_KEY"),
            ("o4-mini", "OPENAI_KEY"),
            ("o1", "OPENAI_KEY"),
            ("o3", "OPENAI_KEY"),
            ("gemini-2.0-flash", "GOOGLE_API_KEY"),
            ("gemini-1.5-pro", "GOOGLE_API_KEY"),
        ],
    )
    def test_resolves_correct_provider(self, model, expected_key):
        provider = _resolve_provider(model)
        assert provider["env_key"] == expected_key

    def test_unknown_model_defaults_to_anthropic(self):
        provider = _resolve_provider("some-unknown-model")
        assert provider["env_key"] == "ANTHROPIC_API_KEY"

    def test_anthropic_supports_native_pdf(self):
        assert PROVIDERS["anthropic"]["native_pdf"] is True

    @pytest.mark.parametrize("name", ["openai", "google"])
    def test_non_anthropic_no_native_pdf(self, name):
        assert PROVIDERS[name]["native_pdf"] is False


class TestDocumentExtractorInit:
    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_anthropic_uses_anthropic_key(self, mock_create):
        mock_create.return_value = MagicMock()
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test"}):
            ext = _make_extractor(model="claude-haiku-4-5-20251001")
        assert ext.api_key == "sk-ant-test"

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_openai_uses_openai_key(self, mock_create):
        mock_create.return_value = MagicMock()
        with patch.dict("os.environ", {"OPENAI_KEY": "sk-openai-test"}):
            ext = _make_extractor(model="gpt-4o-mini")
        assert ext.api_key == "sk-openai-test"

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_google_uses_google_key(self, mock_create):
        mock_create.return_value = MagicMock()
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "goog-test"}):
            ext = _make_extractor(model="gemini-2.0-flash")
        assert ext.api_key == "goog-test"

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_explicit_api_key_overrides_env(self, mock_create):
        mock_create.return_value = MagicMock()
        ext = _make_extractor(model="gpt-4o-mini", api_key="explicit-key")
        assert ext.api_key == "explicit-key"


class TestExtractWithVision:
    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_anthropic_uses_native_base64_format(self, mock_create):
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {"field": "value"}
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="claude-haiku-4-5-20251001", api_key="fake")
        result = ext._extract_with_vision(["abc123base64data"])

        call_args = ext.structured_llm.invoke.call_args[0][0][0]
        img_block = call_args.content[0]
        assert img_block["type"] == "image"
        assert img_block["source"]["type"] == "base64"
        assert img_block["source"]["data"] == "abc123base64data"
        assert result == {"field": "value"}

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_openai_uses_data_uri_format(self, mock_create):
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {"field": "value"}
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="gpt-4o-mini", api_key="fake")
        ext._extract_with_vision(["abc123base64data"])

        call_args = ext.structured_llm.invoke.call_args[0][0][0]
        img_block = call_args.content[0]
        assert img_block["type"] == "image_url"
        assert img_block["image_url"]["url"].startswith("data:image/jpeg;base64,")

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_uses_url_when_provided(self, mock_create):
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {"field": "value"}
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="gpt-4o-mini", api_key="fake")
        result = ext._extract_with_vision(image_url="https://s3.example.com/file.jpg")

        call_args = ext.structured_llm.invoke.call_args[0][0][0]
        img_block = call_args.content[0]
        assert img_block["image_url"]["url"] == "https://s3.example.com/file.jpg"
        assert result == {"field": "value"}

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_raises_when_no_image_source(self, mock_create):
        mock_create.return_value = MagicMock()
        ext = _make_extractor(model="gpt-4o-mini", api_key="fake")
        with pytest.raises(ValueError, match="Se requiere"):
            ext._extract_with_vision()


class TestPdfFallbackForNonAnthropicProviders:
    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_openai_converts_pdf_to_image(self, mock_create):
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {"field": "value"}
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="gpt-4o-mini", api_key="fake")
        fake_img = MagicMock()
        fake_img.width = 100
        fake_img.height = 100
        fake_img.rotate.return_value = fake_img
        fake_img.save = MagicMock(side_effect=lambda buf, **kw: buf.write(b"\xff\xd8fake"))

        fake_stat = MagicMock()
        fake_stat.st_size = 500_000

        with (
            patch.object(ext, "_pdf_to_image", return_value=fake_img) as mock_pdf,
            patch.object(ext, "_check_orientation", return_value=0),
            patch("pathlib.Path.stat", return_value=fake_stat),
        ):
            result = ext._extract_with_pdf(Path("/fake/file.pdf"))

        mock_pdf.assert_called()
        assert result == {"field": "value"}

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_openai_raises_when_pdf_conversion_fails(self, mock_create):
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = MagicMock()
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="gpt-4o-mini", api_key="fake")

        fake_stat = MagicMock()
        fake_stat.st_size = 500_000

        with (
            patch.object(ext, "_pdf_to_image", return_value=None),
            patch("pathlib.Path.stat", return_value=fake_stat),
        ):
            with pytest.raises(ValueError, match="No se pudo convertir el PDF"):
                ext._extract_with_pdf(Path("/fake/file.pdf"))

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_anthropic_always_uses_native_pdf(self, mock_create):
        """Anthropic always sends raw PDF (native support)."""
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {"field": "value"}
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="claude-haiku-4-5-20251001", api_key="fake")

        fake_img = MagicMock()
        fake_img.width = 100
        fake_img.height = 100
        fake_img.save = MagicMock(side_effect=lambda buf, **kw: buf.write(b"\xff\xd8fake"))

        fake_stat = MagicMock()
        fake_stat.st_size = 5_000_000  # Even for heavy PDFs

        with (
            patch.object(ext, "_pdf_to_image", return_value=fake_img),
            patch.object(ext, "_check_orientation", return_value=0),
            patch("pathlib.Path.stat", return_value=fake_stat),
            patch("pathlib.Path.read_bytes", return_value=b"%PDF-fake"),
        ):
            ext._extract_with_pdf(Path("/fake/file.pdf"))

        call_args = ext.structured_llm.invoke.call_args[0][0][0]
        content = call_args.content
        assert content[0]["type"] == "file"
        assert content[0]["mime_type"] == "application/pdf"

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_anthropic_falls_back_to_raw_pdf_when_image_fails(self, mock_create):
        """When image conversion fails, Anthropic still sends native PDF."""
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {
            "field": "value",
        }
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="claude-haiku-4-5-20251001", api_key="fake")

        fake_stat = MagicMock()
        fake_stat.st_size = 500_000

        with (
            patch.object(ext, "_pdf_to_image", return_value=None),
            patch("pathlib.Path.stat", return_value=fake_stat),
            patch("pathlib.Path.read_bytes", return_value=b"%PDF-fake"),
        ):
            ext._extract_with_pdf(Path("/fake/file.pdf"))

        call_args = ext.structured_llm.invoke.call_args[0][0][0]
        content = call_args.content
        assert content[0]["type"] == "file"
        assert content[0]["mime_type"] == "application/pdf"


class TestExtractFileWithImageUrl:
    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_image_url_skips_base64(self, mock_create):
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {
            "is_valid_document": True,
            "owner": "Test",
            "account_number": "012345678901234567",
            "bank_name": "BBVA",
        }
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="gpt-4o-mini", api_key="fake")

        with patch.object(ext, "_load_image_file") as mock_load:
            result = ext.extract_file(
                Path("/fake/file.jpg"), image_url="https://s3.example.com/file.jpg"
            )

        mock_load.assert_not_called()
        assert result["owner"] == "Test"

    @patch("src.infrastructure.extractors.document_extractor._create_llm")
    def test_pdf_ignores_image_url(self, mock_create):
        """PDFs always go through _extract_with_pdf, image_url is not used."""
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value.invoke.return_value = {"field": "value"}
        mock_create.return_value = mock_llm

        ext = _make_extractor(model="claude-haiku-4-5-20251001", api_key="fake")

        with patch.object(ext, "_extract_with_pdf", return_value={"field": "value"}) as mock_pdf:
            ext.extract_file(Path("/fake/file.pdf"), image_url="https://s3.example.com/file.pdf")

        mock_pdf.assert_called_once()


class TestStorageDownloadUrl:
    def test_local_storage_returns_none(self):
        from src.infrastructure.storage import LocalStorage

        storage = LocalStorage()
        assert storage.generate_download_url("some-key") is None
