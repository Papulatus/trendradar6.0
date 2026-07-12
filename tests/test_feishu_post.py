from unittest.mock import Mock, patch

from trendradar.notification.senders import send_to_feishu


def test_open_feishu_webhook_uses_rich_text_post():
    response = Mock(status_code=200)
    response.json.return_value = {"code": 0}

    with patch("trendradar.notification.senders.requests.post", return_value=response) as post:
        ok = send_to_feishu(
            "https://open.feishu.cn/open-apis/bot/v2/hook/test",
            {"stats": []},
            "测试报告",
            split_content_func=lambda *args, **kwargs: ["**总新闻：** 56 条\n1. [新闻标题](https://example.com)"],
            get_time_func=lambda: None,
        )

    assert ok is True
    payload = post.call_args.kwargs["json"]
    assert payload["msg_type"] == "post"
    post_body = payload["content"]["post"]["zh_cn"]
    assert post_body["title"] == "测试报告"
    flat = [element for row in post_body["content"] for element in row]
    assert any(e["tag"] == "text" and "总新闻" in e["text"] for e in flat)
    assert any(e["tag"] == "a" and e["text"] == "新闻标题" for e in flat)
