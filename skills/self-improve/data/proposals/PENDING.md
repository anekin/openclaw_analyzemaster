# 待审批的配置修改建议

> 只有固化到系统文件时需要确认，其他全自动。

---

## [P-001] 添加 Cron 定时任务

- **来源:** self-improve 安装
- **建议修改:** 在 openclaw.json 的 cron 中添加：

```json
{
  "name": "self-improve",
  "schedule": {
    "kind": "cron",
    "expr": "0 4 */3 * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "你是 Self-Improve 系统的执行者。请按以下步骤执行：\n1. 读取 /home/ubuntu/.openclaw/workspace-analyzer_agent/skills/self-improve/data/SYSTEM.md 了解完整流程\n2. 读取 /home/ubuntu/.openclaw/workspace-analyzer_agent/skills/self-improve/data/config.yaml 了解模块配置\n3. 扫描 /home/ubuntu/.openclaw 下所有 agent 的 memory/ 目录\n4. 按执行顺序运行所有已启用模块\n5. 如有待审批建议，用 message 工具发送到 feishu:ou_748ca9fa159c6e40ba15f64fc3fe2976\n6. 记录运行日志到 run-log.jsonl",
    "model": "moonshot/kimi-k2.5"
  }
}
```

- **目标文件:** openclaw.json
- **理由:** 每 3 天自动运行自我改进
- **状态:** ✅ 已完成

---

## [P-002] 可选：添加 HEARTBEAT 入口

- **来源:** self-improve 安装
- **建议修改:** 在 HEARTBEAT.md 添加：

```markdown
## Self-Improve（每 3 天）
- 检查上次运行时间，如 ≥ 3 天 → 提醒运行
- 检查 proposals/PENDING.md，如有待审批 → 提醒
```

- **目标文件:** HEARTBEAT.md
- **理由:** 补充检查入口
- **状态:** ✅ 已完成

---

## [P-003] 更新 AGENTS.md - 用户称呼

- **来源:** 2026-04-04 Self-Improve 运行
- **建议修改:** 在 AGENTS.md 中添加：

```markdown
## 用户称呼偏好
- 用户偏好被称为"老板"
- 在沟通中使用"老板"作为称呼
```

- **目标文件:** AGENTS.md
- **理由:** 记录用户明确的称呼偏好
- **状态:** ✅ 已完成

---

## [P-004] 更新 TOOLS.md - 数据处理最佳实践

- **来源:** 2026-04-04 Self-Improve 运行
- **建议修改:** 在 TOOLS.md 中添加：

```markdown
### 数据处理安全检查
- 对 API 返回的数值字段进行 None 值检查
- 使用 try-except 捕获转换异常
- 重要数据变更前进行备份
```

- **目标文件:** TOOLS.md
- **理由:** 沉淀 QVeris 数据获取错误的教训
- **状态:** ✅ 已完成

---

## [P-005] 记录高价值教训 - ETF代码核对

- **来源:** 2026-04-04 Self-Improve 运行
- **建议修改:** 创建 data/high-value/etf-code-verification.md：

```markdown
# ETF代码核对教训

## 事件
2026-03-26 发现新能源ETF代码错误

## 影响
- 错误代码: 159806.SZ
- 正确代码: 516160.SH
- 总市值偏差: ~¥6,400

## 预防措施
1. 定期核对持仓代码与实际持仓
2. 价格异常时立即检查代码匹配
3. 新添加ETF时双重确认代码
```

- **目标文件:** data/high-value/etf-code-verification.md
- **理由:** 记录重要教训，防止类似错误
- **状态:** ✅ 已完成

---

*上次更新: 2026-04-04*
