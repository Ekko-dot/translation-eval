# NLLB 翻译模型基线评测报告

## 项目概述

本项目旨在评估传统机器翻译模型 NLLB 在酒旅领域地名翻译任务上的表现，为后续 Prompt Engineering 优化提供基线对照。

---

## 实验环境

| 项目 | 配置 |
|------|------|
| 模型 | facebook/nllb-200-distilled-600M |
| 模型大小 | 600M 参数 (蒸馏版) |
| 设备 | CUDA GPU |
| 语言对 | 中文 → 英文 (zho_Hans → eng_Latn) |
| 测试样本 | 50 条 |

---

## 评测结果

### 总体准确率

| 指标 | 数值 |
|------|------|
| **平均准确率** | **43.00%** |
| 正确翻译 (CORRECT) | 23 个地名 |
| 可接受翻译 (ACCEPTABLE) | 3 个地名 |
| 缺失实体 (MISSING_ENTITY) | 46 个地名 |

### 性能指标

| 指标 | 数值 |
|------|------|
| 总翻译时间 | 11.78 秒 |
| 平均每条翻译时间 | 0.24 秒 |

---

## 错误类型分析

### 1. 地名缺失 (MISSING_ENTITY) - 最常见问题

模型未能识别并翻译地名，直接省略或用泛指词替代。

| 中文原文 | NLLB 翻译 | 标准译名 |
|---------|---------|---------|
| 外滩 | the main entrance / outdoor nightlife | The Bund |
| 九寨沟风景区 | The area | Jiuzhai Valley |
| 颐和园 | (缺失) | The Summer Palace |
| 宽窄巷子 | (缺失) | Kuanzhai Alley |

### 2. 非标准译名

模型使用直译或拼音，而非官方/通用译名。

| 中文原文 | NLLB 翻译 | 标准译名 | 问题类型 |
|---------|---------|---------|---------|
| 广州白云国际机场 | Guangzhou White Cloud International Airport | Guangzhou Baiyun International Airport | 直译非拼音 |
| 东方明珠塔 | East Pearl Tower | Oriental Pearl Tower | 非官方译名 |
| 黄山 | Yellow Mountain | Mount Huangshan | 可接受但不标准 |
| 布达拉宫 | The Buda Palace | Potala Palace | 错误音译 |

### 3. 拼音格式错误

| 中文原文 | NLLB 翻译 | 标准译名 | 问题 |
|---------|---------|---------|------|
| 深圳宝安国际机场 | Shenzhen Bao An International Airport | Shenzhen Bao'an International Airport | 音节未分隔 |
| 天安门广场 | Tiananmen Square | Tian'anmen Square | 缺少隔音符 |

### 4. 严重误译

| 中文原文 | NLLB 翻译 | 标准译名 | 问题 |
|---------|---------|---------|------|
| 新加坡樟宜机场 | Singapore's Xi'an Airport | Singapore Changi Airport | 完全错误 |
| 大三巴牌坊 | The Grand Saloon | Ruins of St. Paul's | 完全错误 |
| 兵马俑 | Warrior Horse Museum | Terracotta Warriors | 严重误译 |
| 凤凰古城 | The ancient city of Yangon | Phoenix Ancient Town | 地名混淆 |

---

## 正确翻译示例

以下地名 NLLB 能够正确翻译：

| 中文 | 英文翻译 | 状态 |
|------|---------|------|
| 北京首都国际机场 | Beijing Capital International Airport | ✓ |
| 上海浦东国际机场 | Shanghai Pudong International Airport | ✓ |
| 长城 | The Great Wall | ✓ |
| 故宫博物院 | The Palace Museum | ✓ |
| 西湖 | West Lake | ✓ |
| 台北101 | Taipei 101 | ✓ |
| 香港国际机场 | Hong Kong International Airport | ✓ |
| 北京大兴国际机场 | Beijing Daxing International Airport | ✓ |

---

## 问题根因分析

### 1. 训练数据局限性
- NLLB 训练数据可能缺乏酒旅领域专业地名
- 官方译名、UNESCO 世界遗产名称等特殊名词覆盖不足

### 2. 翻译策略问题
- 倾向于直译或音译，而非使用约定俗成的官方译名
- 对专有名词的识别和处理能力有限

### 3. 上下文理解不足
- 无法根据语境判断是否需要保留/翻译地名
- 对地名在句子中的重要性缺乏感知

---

## 后续优化方向

### 1. Prompt Engineering
- 在提示词中注入地名库上下文
- 明确要求使用官方译名
- 添加地名翻译规则和示例

### 2. RAG 增强
- 构建地名知识库
- 检索相关地名后注入翻译上下文

### 3. 后处理修正
- 基于地名库进行后处理匹配和修正
- 拼音格式自动校正

---

## 文件清单

```
translation-eval/
├── data/
│   ├── testset.json                    # 测试数据集 (50条)
│   └── gazetteer/
│       ├── airports.json               # 机场名称库 (80个)
│       └── attractions.json            # 景点名称库 (100个)
├── evals/
│   └── gazetteer_match.py              # 评测脚本
├── reports/
│   ├── nllb_translations.json          # NLLB翻译结果
│   ├── nllb_translations_only.json     # 纯翻译文本
│   └── nLLB_evaluation_report.txt      # 详细评测报告
├── nllb_translate.py                   # NLLB翻译脚本
└── REPORT.md                           # 本报告
```

---

## 结论

NLLB-200-distilled-600M 模型在酒旅领域地名翻译任务上的基线准确率为 **43%**，主要问题集中在：

1. **地名缺失**：大量地名未被正确识别和翻译
2. **非标准译名**：使用直译/拼音而非官方译名
3. **严重误译**：部分地名翻译完全错误

该基线准确率可作为后续 Prompt Engineering 优化和 LLM 翻译效果对比的参考基准。预期通过优化提示词、注入地名知识等方式，可将准确率提升至 80% 以上。

---

*报告生成时间: 2026-03-16*
*模型版本: facebook/nllb-200-distilled-600M*
