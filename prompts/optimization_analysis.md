# Prompt 优化分析报告

## 当前版本: v0.1 (基线)

**准确率**: 83.67% (Qwen Plus)

## 错误分析

### 问题1: MISSING_ENTITY (20.8%)

**原因分析**:
- Prompt 未充分强调必须识别并翻译所有地名
- 缺乏足够的 few-shot 示例展示复杂地名的翻译
- 部分地名在语境中被当作普通名词处理

**典型错误**:
1. 兵马俑 → 未识别 (应为 Emperor Qinshihuang's Mausoleum Site Museum)
2. 九寨沟风景区 → 直译为 Jiuzhaigou Scenic Area (应为 Jiuzhai Valley)
3. 熊猫基地 → 直译为 Giant Panda Base (应为 Chengdu Research Base of Giant Panda Breeding)
4. 天安门广场 → 未识别 (应为 Tian'anmen Square)
5. 大三巴牌坊 → 未识别 (应为 Ruins of St. Paul's)

**优化策略**:
1. 添加明确的指令："必须识别并翻译原文中的所有地名"
2. 增加更多 few-shot 示例，特别是景点类地名
3. 添加常见错误警示：不要直译，优先使用官方/通用译名

### 问题2: ACCEPTABLE (5.6%)

**原因分析**:
- 部分地名使用了可接受的别名而非标准译名
- 如：天坛公园 → temple of heaven (应为 The Temple of Heaven)

**优化策略**:
1. 强调使用标准官方译名
2. 添加更多标准译名示例

## 优化建议汇总

| 优先级 | 问题 | 优化措施 |
|-------|------|---------|
| P0 | MISSING_ENTITY | 添加强制翻译所有地名的指令 |
| P0 | MISSING_ENTITY | 增加 10+ 个景点类地名 few-shot |
| P1 | ACCEPTABLE | 强调使用官方标准译名 |
| P1 | 通用性 | 添加常见错误警示 |

## 预期改进

- 目标准确率: 90%+
- 主要改进: MISSING_ENTITY 错误减少 50%+
