import hashlib
import hmac
import json
from unittest.mock import Mock, patch

from trendradar.notification.senders import send_to_generic_webhook


def test_generic_webhook_uses_hermes_v2_signature(monkeypatch):
    monkeypatch.setenv("GENERIC_WEBHOOK_SECRET", "shared-secret")
    response = Mock(status_code=200, text="ok")

    def split_content(*args, **kwargs):
        return ["报告正文"]

    with patch("trendradar.notification.senders.time.time", return_value=1700000000), patch(
        "trendradar.notification.senders.requests.post", return_value=response
    ) as post:
        ok = send_to_generic_webhook(
            "https://hermes.example/webhooks/trendradar-report",
            '{"event_type":"trendradar_report","title":"{title}","content":"{content}"}',
            {},
            "测试报告",
            split_content_func=split_content,
        )

    assert ok is True
    kwargs = post.call_args.kwargs
    body = kwargs["data"]
    payload = json.loads(body)
    assert payload["event_type"] == "trendradar_report"
    assert payload["title"] == "测试报告"
    assert "报告正文" in payload["content"]
    expected = hmac.new(
        b"shared-secret", b"1700000000." + body, hashlib.sha256
    ).hexdigest()
    assert kwargs["headers"]["X-Webhook-Timestamp"] == "1700000000"
    assert kwargs["headers"]["X-Webhook-Signature-V2"] == expected
