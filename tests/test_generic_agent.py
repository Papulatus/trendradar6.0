from unittest.mock import Mock, patch

from trendradar.notification.senders import send_trigger_to_generic_agent


def test_generic_agent_sends_only_control_trigger():
    token_response = Mock()
    token_response.raise_for_status.return_value = None
    token_response.json.return_value = {"tenant_access_token": "token"}

    send_response = Mock()
    send_response.raise_for_status.return_value = None
    send_response.json.return_value = {"code": 0}

    with patch(
        "trendradar.notification.senders.requests.post",
        side_effect=[token_response, send_response],
    ) as post:
        ok = send_trigger_to_generic_agent(
            app_id="app-id",
            app_secret="app-secret",
            chat_id="oc_target",
            trigger_message="[trendradar:report-ready]",
        )

    assert ok is True
    assert post.call_count == 2
    message = post.call_args_list[1]
    assert message.kwargs["params"] == {"receive_id_type": "chat_id"}
    assert message.kwargs["json"]["receive_id"] == "oc_target"
    assert "[trendradar:report-ready]" in message.kwargs["json"]["content"]
