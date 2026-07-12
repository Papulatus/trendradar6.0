from unittest.mock import Mock, patch

from trendradar.notification.senders import send_report_to_generic_agent


def test_generic_agent_receives_full_report_in_batches():
    token_response = Mock()
    token_response.raise_for_status.return_value = None
    token_response.json.return_value = {"tenant_access_token": "token"}

    send_response = Mock()
    send_response.raise_for_status.return_value = None
    send_response.json.return_value = {"code": 0}

    with patch(
        "trendradar.notification.senders.requests.post",
        side_effect=[token_response, send_response, send_response],
    ) as post:
        ok = send_report_to_generic_agent(
            app_id="app-id",
            app_secret="app-secret",
            chat_id="oc_target",
            report_data={"stats": []},
            report_type="测试报告",
            split_content_func=lambda *args, **kwargs: ["第一批报告", "第二批报告"],
            batch_interval=0,
        )

    assert ok is True
    assert post.call_count == 3
    first_message = post.call_args_list[1]
    second_message = post.call_args_list[2]
    assert first_message.kwargs["params"] == {"receive_id_type": "chat_id"}
    assert first_message.kwargs["json"]["receive_id"] == "oc_target"
    assert "第一批报告" in first_message.kwargs["json"]["content"]
    assert "第二批报告" in second_message.kwargs["json"]["content"]
