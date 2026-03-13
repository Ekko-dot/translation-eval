---
name: trans-evaluate
description: 酒旅领域地名翻译评测器。对翻译结果运行地名匹配评测，计算准确率，生成评测报告。触发词：评测翻译、评估翻译、evaluate translation、翻译评测。
---

# 地名翻译评测

## 工作流程

### 1. 读取翻译结果

```bash
ls -t ~/.openclaw/workspace/translation-eval/reports/translations_*.json | head -1
```

读取最新的翻译结果文件。

### 2. 加载地名库

```bash
cat ~/.openclaw/workspace/translation-eval/data/gazetteer/airports.json
cat ~/.openclaw/workspace/translation-eval/data/gazetteer/attractions.json
```

### 3. 执行评测

对每条翻译结果：

**步骤 3.1 提取原文地名**

从 `entities` 字段获取原文中的地名列表。

**步骤 3.2 检查译文匹配**

| 匹配情况 | 得分 | 判定 |
|---------|------|------|
| 完全匹配标准译名 | 1.0 | CORRECT |
| 匹配可接受别名 | 0.9 | ACCEPTABLE |
| 拼音格式错误 | 0.7 | PINYIN_ERROR |
| 遗漏后缀 | 0.8 | INCOMPLETE |
| 使用直译非通用名 | 0.5 | WRONG_TRANSLATION |
| 未翻译 | 0.0 | MISSING |

**步骤 3.3 记录详情**

```json
{
  "id": "001",
  "accuracy": 0.85,
  "details": [
    {"zh": "深圳宝安机场", "en_found": "Shenzhen Baoan Airport", "en_standard": "Shenzhen Bao'an International Airport", "status": "PINYIN_ERROR"}
  ]
}
```

### 4. 计算总体指标

```
总准确率 = 所有地名得分之和 / 地名总数
```

### 5. 生成评测报告

保存到 `~/.openclaw/workspace/translation-eval/reports/eval_<version>_<timestamp>.json`

```json
{
  "metadata": {
    "translation_file": "translations_v0.1_xxx.json",
    "timestamp": "2026-03-13T10:30:00Z"
  },
  "summary": {
    "total_samples": 50,
    "total_entities": 65,
    "accuracy": 0.78,
    "error_distribution": {
      "CORRECT": 40,
      "ACCEPTABLE": 10,
      "PINYIN_ERROR": 8,
      "WRONG_TRANSLATION": 5,
      "MISSING": 2
    }
  },
  "results": [...]
}
```

### 6. 输出摘要

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  地名翻译评测报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  总样本: 50
  总地名: 65
  准确率: 78.0%

  错误分布:
  ✓ 正确: 40 (61.5%)
  ○ 可接受: 10 (15.4%)
  ⚠ 拼音错误: 8 (12.3%)
  ✗ 翻译错误: 5 (7.7%)
  ✗ 遗漏: 2 (3.1%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 常见错误类型

| 错误类型 | 示例 | 修正 |
|---------|------|------|
| PINYIN_ERROR | Baoan | Bao'an |
| WRONG_TRANSLATION | Gugong | The Forbidden City |
| INCOMPLETE | Shenzhen Bao'an Airport | Shenzhen Bao'an International Airport |
| MISSING | 未翻译 | 必须翻译 |
