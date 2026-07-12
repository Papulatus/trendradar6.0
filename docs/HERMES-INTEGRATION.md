# TrendRadar → Hermes → 飞书集成

## 推荐数据流

`GitHub Actions / TrendRadar` → `Hermes Webhook` → `Generic Agent` → 当前飞书会话

不要再让一个飞书机器人向另一个机器人发消息。飞书自定义机器人 webhook 是单向入站通道，Hermes 也不应依赖“读取另一个机器人的历史消息”。TrendRadar 已有通用 Webhook；本 fork 只增加 Hermes Webhook V2 的 HMAC 签名。

## Hermes 侧

1. 为 `mini-analyze` profile 启用 webhook adapter，并使用可被 GitHub Actions 访问的 HTTPS 地址（反向代理或 Cloudflare Tunnel）。
2. 创建动态订阅：

```bash
hermes webhook subscribe trendradar-report \
  --prompt 'TrendRadar 报告批次：{title}\n\n{content}\n\n请保留关键数据，给出简洁摘要、风险点和需要进一步研究的标的。' \
  --events trendradar_report \
  --deliver feishu \
  --deliver-chat-id '<当前飞书 chat_id>' \
  --secret '<强随机共享密钥>'
```

如希望直接转发、不经过 LLM，可加 `--deliver-only`，并把 prompt 改为 `{title}\n\n{content}`。

> 实际 CLI 参数以部署机上的 `hermes webhook subscribe --help` 为准。Hermes 官方文档确认通用 V2 认证头为 `X-Webhook-Signature-V2` 与 `X-Webhook-Timestamp`，签名内容为 `<timestamp>.<raw body>` 的 HMAC-SHA256 hex。

## GitHub Secrets

- `GENERIC_WEBHOOK_URL=https://<Hermes-host>/webhooks/trendradar-report`
- `GENERIC_WEBHOOK_SECRET=<与 Hermes route 相同的密钥>`
- `GENERIC_WEBHOOK_TEMPLATE={"event_type":"trendradar_report","title":"{title}","content":"{content}"}`

`GENERIC_WEBHOOK_TEMPLATE` 必须是合法 JSON 字符串。TrendRadar 会对 `{title}` / `{content}` 做 JSON 转义。

## 验证

1. Hermes 本机：`curl http://localhost:8644/health`。
2. Hermes：`hermes webhook test trendradar-report --payload '{"event_type":"trendradar_report","title":"集成测试","content":"测试报告"}'`。
3. GitHub Actions 手动运行 `Get Hot News`。
4. 检查 Actions 日志出现“通用Webhook…发送成功”。
5. 当前飞书会话应收到 Hermes 处理后的报告；核对标题、首尾新闻、批次数及时间。
6. 使用错误密钥重测，应返回 HTTP 401；确认未认证数据不会进入 Agent。

## 回滚

删除三个 `GENERIC_WEBHOOK_*` Secrets 即可停用，不影响原 `FEISHU_WEBHOOK_URL` 推送。代码在未配置 `GENERIC_WEBHOOK_SECRET` 时仍兼容原无签名通用 Webhook。
