---
name: trans-translate
description: 酒旅领域地名翻译执行器。读取测试集，使用当前 Prompt 版本翻译每条样本，保存结果。触发词：翻译测试集、执行翻译、run translation、地名翻译。
---

# 地名翻译执行

## 工作流程

### 1. 读取测试集

```bash
cat ~/.openclaw/workspace/translation-eval/data/testset.json
```

### 2. 确定 Prompt 版本

检查 `~/.openclaw/workspace/translation-eval/prompts/iterations/` 目录：
- 如果有多个版本，使用最新的（按文件名排序）
- 如果没有迭代版本，使用 `~/.openclaw/workspace/translation-eval/prompts/baseline.md`

如果 baseline.md 不存在，使用以下默认 Prompt：

```
你是一位专业的酒旅领域翻译专家。
将以下中文翻译为英文。要求：
1. 使用地名的官方/通用英文译名
2. 拼音格式正确（如 Xi'an 非 Xian，Bao'an 非 Baoan）
3. 机场名称包含完整后缀（如 International Airport）
4. 保持语义完整

原文：{source_text}

直接输出译文，不要解释。
```

### 3. 加载地名库参考

```bash
cat ~/.openclaw/workspace/translation-eval/data/gazetteer/airports.json
cat ~/.openclaw/workspace/translation-eval/data/gazetteer/attractions.json
```

### 4. 执行翻译

对测试集中每条样本：
1. 读取 `source` 字段
2. 从地名库查找 `entities` 中地名的标准译名
3. 将地名参考注入 Prompt
4. 调用 LLM 翻译
5. 记录结果

### 5. 保存结果

保存到 `~/.openclaw/workspace/translation-eval/reports/translations_<version>_<timestamp>.json`

```json
{
  "metadata": {
    "prompt_version": "v0.1",
    "timestamp": "2026-03-13T10:00:00Z",
    "total": 50
  },
  "results": [
    {
      "id": "001",
      "source": "原文",
      "translation": "译文",
      "entities": ["地名1"]
    }
  ]
}
```

## 输出摘要

翻译完成后报告：
- 翻译条目数
- Prompt 版本
- 结果文件路径

## 地名翻译规则速查

| 中文 | 英文 | 注意 |
|------|------|------|
| 西安 | Xi'an | 撇号分隔 |
| 宝安 | Bao'an | 撇号分隔 |
| 故宫 | The Forbidden City | 非拼音 |
| 外滩 | The Bund | 非拼音 |
| 长城 | The Great Wall | 非拼音 |
| 机场 | International Airport | 完整后缀 |
