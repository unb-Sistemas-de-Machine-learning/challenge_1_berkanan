import os
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from api.main import app
from api.routes import analysis as analysis_routes
from api.schemas.analysis import AnalysisHistoryResponse, MatchedSource
from db.database import AnalysisHistory
from scripts.llm_client import GeminiClient


class BackendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.startup_patch = patch("api.main.get_checker")
        cls.startup_patch.start()
        cls.client_context = TestClient(app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
        cls.startup_patch.stop()

    def test_invalid_short_text_is_rejected(self):
        with patch.object(analysis_routes, "analyze_claim") as analyze:
            response = self.client.post("/api/analyze", json={"text": "ab"})

        self.assertEqual(response.status_code, 422)
        analyze.assert_not_called()

    def test_analysis_response_and_cors_contract(self):
        analysis_id = uuid4()
        sources = [
            {
                "text": f"Evidence text {index}",
                "source": "guideline.txt",
                "similarity": 0.8,
            }
            for index in range(3)
        ]
        record = SimpleNamespace(
            id=analysis_id,
            input_text="Canela cura diabetes?",
            classification="FAKE",
            confidence_score=0.94,
            matched_sources=sources,
            model_version="LogisticRegression",
            analysis_date=datetime.now(timezone.utc),
            llm_model="gemini-test",
            rag_sources_count=3,
            response_time_ms=125,
        )
        result = {
            "input_text": record.input_text,
            "classification": record.classification,
            "confidence_score": record.confidence_score,
            "threshold": 0.3,
            "llm_explanation": None,
            "llm_model": record.llm_model,
            "matched_sources": sources,
            "model_version": record.model_version,
            "response_time_ms": record.response_time_ms,
        }

        with (
            patch.object(analysis_routes, "analyze_claim", return_value=result),
            patch.object(analysis_routes, "insert_analysis_orm", return_value=record),
        ):
            response = self.client.post(
                "/api/analyze",
                json={"text": "Canela cura diabetes?"},
            )

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertEqual(body["id"], str(analysis_id))
        self.assertEqual(body["matched_sources"], sources)
        self.assertIsNone(body["llm_explanation"])
        self.assertEqual(len(body["matched_sources"]), 3)
        self.assertEqual(body["rag_sources_count"], len(body["matched_sources"]))
        self.assertGreater(body["response_time_ms"], 0)

        cors = self.client.options(
            "/api/analyze",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(cors.status_code, 200)
        self.assertEqual(
            cors.headers["access-control-allow-origin"],
            "http://localhost:3000",
        )

    def test_health_and_history_openapi_contract(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/api/health").status_code, 200)

        with patch.object(analysis_routes, "get_recent_analyses_orm", return_value=[]):
            history_response = self.client.get("/api/history")
        self.assertEqual(history_response.status_code, 200)
        self.assertIsInstance(history_response.json(), list)

        schema = self.client.get("/openapi.json").json()
        paths = schema["paths"]
        history_schema = paths["/api/history"]["get"]["responses"]["200"][
            "content"
        ]["application/json"]["schema"]
        self.assertEqual(history_schema["type"], "array")
        self.assertIn("$ref", history_schema["items"])

        definitions = schema["components"]["schemas"]
        source_schema = definitions["MatchedSource"]
        self.assertEqual(source_schema["properties"]["similarity"]["maximum"], 1)
        self.assertEqual(source_schema["properties"]["similarity"]["minimum"], 0)
        response_schema = definitions["AnalysisResponse"]
        self.assertEqual(
            response_schema["properties"]["classification"]["enum"],
            ["REAL", "FAKE", "INCONCLUSIVE", "PARTIALLY_TRUE"],
        )
        self.assertIn("null", response_schema["properties"]["llm_explanation"]["anyOf"][1]["type"])
        self.assertEqual(
            response_schema["properties"]["matched_sources"]["items"]["$ref"],
            "#/components/schemas/MatchedSource",
        )


class PersistenceAndFallbackTests(unittest.TestCase):
    def test_source_count_is_derived_during_orm_persistence(self):
        class FakeSession:
            record = None

            def add(self, record):
                self.record = record

            def commit(self):
                pass

            def refresh(self, record):
                pass

        from db.database import insert_analysis_orm

        session = FakeSession()
        sources = [
            {"text": str(index), "source": "guideline.txt", "similarity": 0.8}
            for index in range(3)
        ]
        record = insert_analysis_orm(
            session,
            input_text="Canela cura diabetes?",
            classification="FAKE",
            confidence_score=0.9,
            matched_sources=sources,
            model_version="LogisticRegression",
            llm_explanation=None,
            llm_model="gemini-test",
            response_time_ms=42,
        )

        self.assertIsInstance(record, AnalysisHistory)
        self.assertEqual(record.rag_sources_count, len(sources))
        self.assertEqual(record.response_time_ms, 42)
        self.assertEqual(record.llm_model, "gemini-test")

    def test_service_measures_pipeline_with_monotonic_clock(self):
        from api.services import fact_checker_service

        checker = SimpleNamespace(
            check=lambda text, save_to_db: {
                "input_text": text,
                "classification": "FAKE",
                "p_fake": 0.9,
                "matched_sources": [],
                "model_version": "LogisticRegression",
                "llm_explanation": None,
            }
        )
        with (
            patch.object(fact_checker_service, "get_checker", return_value=checker),
            patch.object(fact_checker_service.time, "perf_counter", side_effect=[5.0, 5.125]),
        ):
            result = fact_checker_service.analyze_claim("Canela cura diabetes?")

        self.assertEqual(result["response_time_ms"], 125)

    def test_gemini_sdk_has_bounded_transient_retries(self):
        with patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "",
                "LLM_MODEL": "",
                "LLM_MAX_RETRIES": "3",
            },
        ), patch("scripts.llm_client.genai.Client") as sdk_client:
            GeminiClient(api_key="test-key", model_name="gemini-test")

        options = sdk_client.call_args.kwargs["http_options"]
        retry_options = options.retry_options
        self.assertEqual(retry_options.attempts, 3)
        self.assertIn(503, retry_options.http_status_codes)
        self.assertEqual(retry_options.exp_base, 2.0)

    def test_missing_gemini_key_returns_no_explanation(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "", "LLM_MODEL": ""}):
            client = GeminiClient(model_name="gemini-test")

        self.assertIsNone(client.client)
        self.assertIsNone(
            client.generate_fact_check_response(
                "Canela cura diabetes?",
                "FAKE",
                0.9,
                [],
            )
        )
        self.assertEqual(client.model_name, "gemini-test")

    def test_gemini_error_falls_back_without_exposing_error_as_explanation(self):
        from scripts.llm_client import GeminiClient

        client = object.__new__(GeminiClient)
        client.model_name = "gemini-test"
        client.client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=Mock(
                    side_effect=RuntimeError("503 UNAVAILABLE with internal details")
                )
            )
        )
        with patch.object(client, "_build_prompt", return_value="prompt"):
            explanation = client.generate_fact_check_response(
                "Canela cura diabetes?",
                "FAKE",
                0.9,
                [],
            )

        self.assertIsNone(explanation)

    def test_matched_source_similarity_is_validated(self):
        with self.assertRaises(ValueError):
            MatchedSource(text="Evidence", source="guideline.txt", similarity=1.1)

    def test_history_schema_supports_orm_fields(self):
        response = AnalysisHistoryResponse(
            id=uuid4(),
            input_text="Canela cura diabetes?",
            classification="FAKE",
            confidence_score=0.9,
            analysis_date=datetime.now(timezone.utc),
            user_feedback=None,
            model_version="LogisticRegression",
            llm_explanation=None,
            llm_model="gemini-test",
            rag_sources_count=0,
            response_time_ms=12,
            matched_sources=[],
        )
        self.assertIsNone(response.llm_explanation)


if __name__ == "__main__":
    unittest.main()
