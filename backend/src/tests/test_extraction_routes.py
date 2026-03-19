from unittest.mock import MagicMock, patch

from src.domain.entities import ApiCallResult, MetricsData


class TestGetBanks:
    def test_returns_sorted_banks(self, client):
        resp = client.get("/extraction/banks")
        assert resp.status_code == 200
        banks = resp.json()["banks"]
        assert len(banks) > 0
        names = [b["name"] for b in banks]
        assert names == sorted(names)


class TestExtractFromFile:
    def test_successful_extraction(self, client):
        config_data = MagicMock()
        config_data.id = 1
        config_data.name = "test-config"
        config_data.output_schema = {"properties": {"field": {}}}
        config_data.is_default = False
        config_data.description = ""
        config_data.prompt = "test"
        config_data.model = "test-model"

        call_result = ApiCallResult(
            model="test-model", success=True, response_time_ms=100.0
        )

        with patch(
            "src.infrastructure.api.extraction.routes.get_storage"
        ) as mock_storage, patch(
            "src.infrastructure.api.extraction.routes.ExtractionService"
        ) as MockService, patch(
            "src.infrastructure.api.extraction.routes.ExtractorConfigRepository"
        ) as MockConfigRepo, patch(
            "src.infrastructure.api.extraction.routes.ApiCallRepository"
        ), patch(
            "src.infrastructure.api.extraction.routes.AiUsageLogRepository"
        ), patch(
            "src.infrastructure.api.extraction.routes.QuotaService"
        ) as MockQuota:
            MockQuota.return_value.check_extraction_quota.return_value = None
            mock_storage.return_value.download.return_value = b"file-bytes"
            MockService.return_value.extract.return_value = (
                {"field": "value"},
                call_result,
                None,
            )
            MockConfigRepo.return_value.get_by_id.return_value = config_data
            MockConfigRepo.return_value.get_active_versions.return_value = []

            resp = client.post(
                "/extraction/extract",
                json={
                    "s3_key": "test/file.pdf",
                    "filename": "file.pdf",
                    "extractor_config_id": 1,
                },
            )
        assert resp.status_code == 200
        assert resp.json()["fields"]["field"] == "value"

    def test_config_not_found_returns_404(self, client):
        with patch(
            "src.infrastructure.api.extraction.routes.ExtractorConfigRepository"
        ) as MockConfigRepo, patch(
            "src.infrastructure.api.extraction.routes.ApiCallRepository"
        ), patch(
            "src.infrastructure.api.extraction.routes.AiUsageLogRepository"
        ), patch(
            "src.infrastructure.api.extraction.routes.QuotaService"
        ) as MockQuota:
            MockQuota.return_value.check_extraction_quota.return_value = None
            MockConfigRepo.return_value.get_by_id.return_value = None
            resp = client.post(
                "/extraction/extract",
                json={
                    "s3_key": "test/file.pdf",
                    "filename": "file.pdf",
                    "extractor_config_id": 999,
                },
            )
        assert resp.status_code == 404


class TestSubmitExtraction:
    def test_records_submission(self, client):
        with patch(
            "src.infrastructure.api.extraction.routes.ExtractionRepository"
        ) as MockRepo:
            MockRepo.return_value.create.return_value = MagicMock(id=42)
            resp = client.post(
                "/extraction/submit",
                json={
                    "filename": "test.pdf",
                    "extracted_fields": {"name": "Alice"},
                    "final_fields": {"name": "Alice"},
                    "extractor_config_id": 1,
                },
            )
        assert resp.status_code == 200


class TestGetLogs:
    def test_returns_paginated_response(self, client):
        mock_log = MagicMock()
        mock_log.id = 1
        mock_log.filename = "test.pdf"
        mock_log.extracted_fields = {}
        mock_log.final_fields = {}
        mock_log.corrected_fields = {}
        mock_log.timestamp = "2026-01-01T00:00:00"
        mock_log.extractor_config_version_id = None
        with patch(
            "src.infrastructure.api.extraction.routes._get_repository"
        ), patch(
            "src.infrastructure.api.extraction.routes.SubmissionService"
        ) as MockService:
            MockService.return_value.get_extraction_logs.return_value = ([mock_log], 1, 1)
            resp = client.get("/extraction/logs")
        assert resp.status_code == 200
        data = resp.json()
        assert "logs" in data
        assert "pagination" in data


class TestGetMetrics:
    def test_returns_metrics(self, client):
        metrics = MetricsData(
            total_extractions=10,
            total_corrections=2,
            accuracy_rate=0.8,
            this_week=5,
            field_accuracies={"name": 0.9},
        )
        with patch(
            "src.infrastructure.api.extraction.routes.ExtractionRepository"
        ) as MockRepo:
            MockRepo.return_value.count_total.return_value = 10
            MockRepo.return_value.count_corrections.return_value = 2
            MockRepo.return_value.count_this_week.return_value = 5
            MockRepo.return_value.get_field_accuracies.return_value = {"name": 0.9}

            # Patch MetricsService to return our data
            with patch(
                "src.infrastructure.api.extraction.routes.MetricsService"
            ) as MockService:
                MockService.return_value.get_metrics.return_value = metrics
                resp = client.get("/extraction/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_extractions"] == 10
