import unittest
from time import time

from slack_bolt import App, BoltRequest
from slack_sdk.signature import SignatureVerifier
from slack_sdk.web import WebClient
from tests.mock_web_api_server import \
    setup_mock_web_api_server, cleanup_mock_web_api_server


class TestSSLCheck(unittest.TestCase):
    signing_secret = "secret"
    valid_token = "xoxb-valid"
    mock_api_server_base_url = "http://localhost:8888"
    signature_verifier = SignatureVerifier(signing_secret)
    web_client = WebClient(
        token=valid_token,
        base_url=mock_api_server_base_url,
    )

    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def generate_signature(self, body: str, timestamp: str):
        return self.signature_verifier.generate_signature(
            body=body,
            timestamp=timestamp,
        )

    def test_mock_server_is_running(self):
        resp = self.web_client.api_test()
        assert resp != None

    def test_ssl_check(self):
        app = App(
            client=self.web_client,
            signing_secret=self.signing_secret
        )

        timestamp, body = str(int(time())), "token=random&ssl_check=1"
        request: BoltRequest = BoltRequest(
            body=body,
            query={},
            headers={
                "content-type": ["application/x-www-form-urlencoded"],
                "x-slack-signature": [self.generate_signature(body, timestamp)],
                "x-slack-request-timestamp": [timestamp]
            }
        )
        response = app.dispatch(request)
        assert response.status == 200
        assert response.body == ""