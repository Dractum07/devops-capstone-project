"""
Test cases for the Accounts Service routes, security headers and CORS
"""
import unittest
from service import create_app, db
from service.models import Account

BASE_URL = "/accounts"
HTTPS_ENVIRON = {"wsgi.url_scheme": "https"}

ACCOUNT = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "address": "1 Main St",
    "phone_number": "555-1234",
    "date_joined": "2024-01-15",
}


class TestAccountService(unittest.TestCase):
    """Accounts Service tests"""

    def setUp(self):
        self.app = create_app(
            {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"}
        )
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        self.ctx.pop()

    def _post(self, data=None):
        return self.client.post(
            BASE_URL,
            json=data or ACCOUNT,
            environ_overrides=HTTPS_ENVIRON,
        )

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(resp.status_code, 200)

    def test_create_account(self):
        """It should Create a new Account"""
        resp = self._post()
        self.assertEqual(resp.status_code, 201)
        self.assertIsNotNone(resp.headers.get("Location"))
        self.assertEqual(resp.get_json()["name"], ACCOUNT["name"])

    def test_create_account_bad_data(self):
        """It should not Create an Account with missing data"""
        resp = self._post({"name": "No Email"})
        self.assertEqual(resp.status_code, 400)

    def test_create_account_bad_media_type(self):
        """It should not Create an Account with a wrong Content-Type"""
        resp = self.client.post(
            BASE_URL, data="x", content_type="text/plain",
            environ_overrides=HTTPS_ENVIRON,
        )
        self.assertEqual(resp.status_code, 415)

    def test_list_accounts(self):
        """It should List all Accounts"""
        self._post()
        self._post({**ACCOUNT, "name": "John Roe"})
        resp = self.client.get(BASE_URL, environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 2)

    def test_read_account(self):
        """It should Read a single Account"""
        account_id = self._post().get_json()["id"]
        resp = self.client.get(
            f"{BASE_URL}/{account_id}", environ_overrides=HTTPS_ENVIRON
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["name"], ACCOUNT["name"])

    def test_read_account_not_found(self):
        """It should not Read an Account that is not found"""
        resp = self.client.get(f"{BASE_URL}/0", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(resp.status_code, 404)

    def test_update_account(self):
        """It should Update an existing Account"""
        account_id = self._post().get_json()["id"]
        resp = self.client.put(
            f"{BASE_URL}/{account_id}",
            json={**ACCOUNT, "name": "Janet Doe"},
            environ_overrides=HTTPS_ENVIRON,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["name"], "Janet Doe")

    def test_update_account_not_found(self):
        """It should not Update an Account that is not found"""
        resp = self.client.put(
            f"{BASE_URL}/0", json=ACCOUNT, environ_overrides=HTTPS_ENVIRON
        )
        self.assertEqual(resp.status_code, 404)

    def test_delete_account(self):
        """It should Delete an Account"""
        account_id = self._post().get_json()["id"]
        resp = self.client.delete(
            f"{BASE_URL}/{account_id}", environ_overrides=HTTPS_ENVIRON
        )
        self.assertEqual(resp.status_code, 204)
        self.assertIsNone(Account.find(account_id))

    def test_security_headers(self):
        """It should return security headers"""
        resp = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(resp.status_code, 200)
        headers = {
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'self'; object-src 'none'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        for key, value in headers.items():
            self.assertEqual(resp.headers.get(key), value)

    def test_cors_security(self):
        """It should return a CORS header"""
        resp = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("Access-Control-Allow-Origin"), "*")
