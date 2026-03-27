import tempfile
import time
from pathlib import Path

from src.domain.entities import ApiCallResult, ExtractionError, ExtractorConfigData
from src.domain.postprocessors.mexican_bank_statement import (
    postprocess as postprocess_mexican_bank,
)
from src.infrastructure.extractors.document_extractor import (
    SUPPORTED_EXTENSIONS,
    DocumentExtractor,
)


def _logger():
    from src.core.logger import get_logger

    return get_logger(__name__)


ALLOWED_EXTENSIONS = SUPPORTED_EXTENSIONS

POSTPROCESSORS = {
    "mexican_bank_statement": postprocess_mexican_bank,
}


def _create_extractor(config: ExtractorConfigData) -> DocumentExtractor:
    return DocumentExtractor(
        prompt=config.prompt,
        model=config.model,
        output_schema=config.output_schema,
    )


class ExtractionService:
    def extract(
        self,
        file_bytes: bytes,
        filename: str,
        config: ExtractorConfigData,
        image_url: str | None = None,
    ) -> tuple[dict, ApiCallResult, ExtractorConfigData]:
        if not filename:
            raise ValueError("No se proporcionó un archivo")

        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Tipo de archivo no soportado: {suffix}. "
                f"Formatos aceptados: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(file_bytes)
                tmp_file_path = Path(tmp_file.name)

            extractor = _create_extractor(config)

            start = time.monotonic()
            _logger().info(
                "Calling extract_file (model=%s, postprocessor=%s)",
                extractor.model_name,
                config.postprocessor,
            )
            _logger().info("Prompt: %s", config.prompt[:300])
            _logger().info("Output schema: %s", config.output_schema)
            try:
                raw_result = extractor.extract_file(tmp_file_path, image_url=image_url)
            except ValueError as e:
                elapsed_ms = round((time.monotonic() - start) * 1000, 1)
                call_result = ApiCallResult(
                    model=extractor.model_name,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error_type="InvalidDocument",
                    error_message=str(e),
                )
                raise ExtractionError(str(e), call_result)
            except Exception as e:
                elapsed_ms = round((time.monotonic() - start) * 1000, 1)
                call_result = ApiCallResult(
                    model=extractor.model_name,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                )
                raise ExtractionError(str(e), call_result)

            elapsed_ms = round((time.monotonic() - start) * 1000, 1)

            # Validate document type if model flagged it as invalid
            if raw_result.get("is_valid_document") is False:
                desc = config.description
                call_result = ApiCallResult(
                    model=extractor.model_name,
                    success=False,
                    response_time_ms=elapsed_ms,
                    error_type="InvalidDocument",
                    error_message=f"El documento no corresponde al tipo: {desc}",
                )
                raise ExtractionError(f"El documento no corresponde al tipo: {desc}", call_result)
            # Remove is_valid_document from result before returning
            raw_result.pop("is_valid_document", None)
            _logger().info("Raw extraction result: %s", raw_result)

            # Apply postprocessor if configured
            postprocessor_fn = POSTPROCESSORS.get(config.postprocessor or "")
            if postprocessor_fn:
                _logger().info("Applying postprocessor: %s", config.postprocessor)
                try:
                    raw_result = postprocessor_fn(extractor, tmp_file_path, raw_result)
                    _logger().info("After postprocessor: %s", raw_result)
                except ValueError as e:
                    call_result = ApiCallResult(
                        model=extractor.model_name,
                        success=False,
                        response_time_ms=elapsed_ms,
                        error_type="InvalidDocument",
                        error_message=str(e),
                    )
                    raise ExtractionError(str(e), call_result)

            call_result = ApiCallResult(
                model=extractor.model_name,
                success=True,
                response_time_ms=elapsed_ms,
            )
            return raw_result, call_result, config
        finally:
            if tmp_file_path and tmp_file_path.exists():
                tmp_file_path.unlink()
