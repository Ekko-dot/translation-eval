---
name: trans-optimize
description: 酒旅领域翻译 Prompt 优化器。分析评测报告，识别问题模式，生成改进版 Prompt。触发词：优化提示词、optimize prompt、改进翻译、迭代优化。
---

# 翻译 Prompt 优化

## 工作流程

### 1. 读取评测报告

```bash
ls -t ~/.openclaw/workspace/translation-eval/reports/eval_*.json | head -1
```

### 2. 分析错误模式

统计各类错误的占比和典型样本：

**高频问题识别**：
- PINYIN_ERROR > 10% → 需要加强拼音规则说明
- WRONG_TRANSLATION > 10% → 需要增加地名示例
- INCOMPLETE > 10% → 需要强调完整性要求
- MISSING > 5% → 需要强调必须翻译所有地名

### 3. 提取典型错误样本

从评测结果中提取每种错误类型的典型样本（各 3-5 个）。

### 4. 生成优化建议

基于错误分析，生成具体的 Prompt 改进建议：

```markdown
## 优化建议

### 问题1: 拼音格式错误 (12.3%)
- 原因: Prompt 未明确拼音分隔规则
- 建议: 添加拼音格式示例

### 问题2: 使用直译非通用名 (7.7%)
- 原因: 地名库未充分注入
- 建议: 增加 few-shot 示例，展示通用译名
```

### 5. 生成新版 Prompt

基于当前 Prompt 和优化建议，生成新版本。

**Prompt 版本命名**: v0.1 → v0.2 → v0.3 ...

保存到 `~/.openclaw/workspace/translation-eval/prompts/iterations/vX.X.md`

### 6. 记录优化历史

更新 `~/.openclaw/workspace/translation-eval/prompts/optimization_log.json`：

```json
{
  "history": [
    {
      "version": "v0.1",
      "timestamp": "2026-03-13T10:00:00Z",
      "accuracy": 0.65,
      "main_issues": ["PINYIN_ERROR", "WRONG_TRANSLATION"]
    },
    {
      "version": "v0.2",
      "timestamp": "2026-03-13T11:00:00Z",
      "accuracy": 0.78,
      "changes": ["添加拼音格式示例", "增加地名 few-shot"],
      "improvement": "+13%"
    }
  ]
}
```

## Prompt 模板库

### 基线结构

```markdown
# 角色定义
你是一位酒旅领域翻译专家...

# 翻译规则
1. ...
2. ...

# 地名示例
| 中文 | 英文 |
|------|------|
| 故宫 | The Forbidden City |
...

# 翻译任务
原文：{source_text}
译文：
```

### 优化方向

| 问题类型 | 优化策略 |
|---------|---------|
| 拼音错误 | 添加 Xi'an, Bao'an 等示例 |
| 通用名错误 | 添加故宫→The Forbidden City 等对照表 |
| 不完整 | 强调机场必须包含 International Airport |
| 遗漏地名 | 要求列出所有地名并逐一翻译 |

## 输出摘要

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Prompt 优化报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  当前版本: v0.1 → v0.2
  准确率变化: 65% → ? (待测试)

  主要改进:
  1. 添加拼音格式示例
  2. 增加地名 few-shot 示例
  3. 强调机场名称完整性

  新 Prompt 保存至:
  prompts/iterations/v0.2.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
