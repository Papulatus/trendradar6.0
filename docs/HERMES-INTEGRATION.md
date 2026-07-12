# TrendRadar → 飞书 → Hermes Generic Agent

## 数据流

`GitHub Actions / TrendRadar` → `飞书应用 API` → `目标飞书群` → `Hermes Generic Agent`

该方案不要求 Hermes 主机开放公网入口。TrendRadar 使用飞书应用凭据获取 tenant access token，并把完整报告按飞书消息上限分批发送到目标群，而不是只发送一条触发语句。

## GitHub Actions Secrets

原有配置按下列名称迁移：

- `GUPIAO_XIA_ENABLED` → `GENERIC_AGENT_ENABLED`
- `GUPIAO_XIA_APP_ID` → `GENERIC_AGENT_APP_ID`
- `GUPIAO_XIA_APP_SECRET` → `GENERIC_AGENT_APP_SECRET`
- `GUPIAO_XIA_CHAT_ID` → `GENERIC_AGENT_CHAT_ID`

`GUPIAO_XIA_TRIGGER_MESSAGE` 不再需要，因为现在发送的是完整报告。

原有 `FEISHU_WEBHOOK_URL` 保持不变，用于原报告渠道；如果它与 `GENERIC_AGENT_CHAT_ID` 指向同一群，将出现两份报告，建议让两条链路指向不同群，或停用其中一条。

## Hermes 飞书入站要求

Hermes 默认拒绝其他 bot/app 发出的群消息。目标群要接收本飞书应用发送的报告，需要在 Hermes 飞书配置中启用：

```yaml
feishu:
  allow_bots: all
```

并为目标群设置单独规则。完整示例：

```yaml
feishu:
  allow_bots: all
  group_rules:
    <目标群 chat_id>:
      policy: open
      require_mention: false
```

`allow_bots: all` 是飞书平台级设置；应通过专用群和群规则限制使用范围，避免其他机器人消息触发 Hermes。

## 运行与验证

生产运行仅由 GitHub Actions 托管。本地只用于代码编辑和测试。

1. 在 GitHub Actions Secrets 配置上述四个 `GENERIC_AGENT_*` 值。
2. 确认发送应用与 Hermes 应用都在目标群中。
3. 重启 Hermes gateway 以加载飞书配置。
4. 手动运行 `Get Hot News`。
5. 检查 Actions 日志出现“完整报告已分 N 批发送”。
6. 检查目标群收到完整报告，并确认 Hermes 创建对应群 Session 后开始处理。
