from unittest.mock import Mock, patch

from trendradar.notification.senders import send_to_feishu


def test_open_feishu_webhook_uses_interactive_card():
    response = Mock(status_code=200)
    response.json.return_value = {"code": 0}

    with patch("trendradar.notification.senders.requests.post", return_value=response) as post:
        ok = send_to_feishu(
            "https://open.feishu.cn/open-apis/bot/v2/hook/test",
            {"stats": []},
            "测试报告",
            split_content_func=lambda *args, **kwargs: ["报告正文"],
            get_time_func=lambda: None,
        )

    assert ok is True
    payload = post.call_args.kwargs["json"]
    assert payload["msg_type"] == "interactive"
    assert payload["card"]["schema"] == "2.0"
    assert payload["card"]["body"]["elements"][0] == {
        "tag": "markdown",
        "content": "报告正文",
    }
