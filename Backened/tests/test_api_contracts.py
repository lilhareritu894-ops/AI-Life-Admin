import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
from pydantic import ValidationError
from bson import ObjectId
from pymongo.errors import ServerSelectionTimeoutError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.session import get_database, mongo_error_detail
from app.main import app
from app.api.endpoints.auth import get_current_user
from app.schemas.finance import TransactionCreate
from app.services.doc_agent import doc_agent
from app.utils.file_parser import extract_text_from_file
from app.utils.mongo import serialize_document


class FakeCollection:
    def __init__(self):
        self.document = None

    async def insert_one(self, document):
        self.document = document.copy()
        return type("InsertResult", (), {"inserted_id": ObjectId()})()


class FakeDatabase:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        self.collections.setdefault(name, FakeCollection())
        return self.collections[name]


class PrivateApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.original_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_database] = lambda: None
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://testserver",
        )

    async def asyncTearDown(self):
        await self.client.aclose()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.original_overrides)

    async def test_private_list_and_summary_routes_require_authentication(self):
        paths = (
            "/api/v1/auth/me",
            "/api/v1/tasks/",
            "/api/v1/calendar/",
            "/api/v1/documents/",
            "/api/v1/agent/runs",
            "/api/v1/finance/",
            "/api/v1/finance/summary",
            "/api/v1/analytics/summary",
        )
        for path in paths:
            with self.subTest(path=path):
                response = await self.client.get(path)
                self.assertEqual(response.status_code, 401)

    async def test_task_create_stores_owner_and_hides_internal_id(self):
        user_id = ObjectId()
        database = FakeDatabase()
        app.dependency_overrides[get_database] = lambda: database
        app.dependency_overrides[get_current_user] = lambda: {"_id": user_id}

        response = await self.client.post("/api/v1/tasks/", json={"title": "Private task"})

        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(database["tasks"].document["owner_id"], user_id)
        self.assertNotIn("owner_id", response.json())


class FinanceSchemaTests(unittest.TestCase):
    def test_rejects_non_positive_or_non_finite_amount(self):
        for amount in (0, -1, float("nan"), float("inf")):
            with self.subTest(amount=amount):
                with self.assertRaises(ValidationError):
                    TransactionCreate(title="Example", amount=amount, kind="expense")

    def test_accepts_valid_transaction(self):
        transaction = TransactionCreate(title="Example", amount=12.5, kind="income")
        self.assertEqual(transaction.amount, 12.5)
        self.assertEqual(transaction.category, "General")


class DocumentParserTests(unittest.TestCase):
    def test_reads_supported_utf8_text(self):
        self.assertEqual(extract_text_from_file("notes.txt", "hello".encode()), "hello")

    def test_rejects_unsupported_binary_format(self):
        with self.assertRaisesRegex(ValueError, "Unsupported file type"):
            extract_text_from_file("photo.png", b"image bytes")

    def test_rejects_invalid_utf8_text(self):
        with self.assertRaisesRegex(ValueError, "valid UTF-8"):
            extract_text_from_file("notes.txt", b"\xff")

    def test_image_upload_uses_gemini_multimodal_extraction(self):
        image_bytes = b"png image content"
        with patch("app.services.doc_agent.llm_service.generate_document_completion", return_value="Receipt text") as generate:
            result = doc_agent.parse_uploaded_document("receipt.png", image_bytes)
        self.assertEqual(result, "Receipt text")
        self.assertEqual(generate.call_args.args[1:], (image_bytes, "image/png"))


class DatabaseDiagnosticsTests(unittest.TestCase):
    def test_local_connection_refusal_has_actionable_detail(self):
        error = ServerSelectionTimeoutError("localhost:27017: connection refused")
        self.assertIn("Start the local MongoDB server", mongo_error_detail(error))

    def test_owner_id_is_not_serialized_to_api_response(self):
        document = {"_id": ObjectId(), "owner_id": ObjectId(), "title": "Private"}
        result = serialize_document(document)
        self.assertNotIn("owner_id", result)
        self.assertIn("_id", document)


if __name__ == "__main__":
    unittest.main()
