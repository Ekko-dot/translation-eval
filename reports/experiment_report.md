# 酒旅地名翻译多模型对比实验报告

生成时间: 2026-03-16 15:15:23

---

## 实验概述
- 测试样本数: 50 条
- 地名实体数: 72 个
- 测试模型数: 5 个
- 评测维度: 地名翻译准确性

## 结果汇总

| 模型 | 类型 | 准确率 | 平均延迟 | 错误数 |
|------|------|--------|----------|--------|
| Qwen Plus (通用推荐模型) | general | 83.67% | 0.99s | 19 |
| Qwen-MT Plus (专业翻译模型) | translation | 82.67% | 0.43s | 21 |
| Qwen Turbo (快速通用模型) | general | 82.67% | 0.60s | 20 |
| Qwen Max (最强通用模型) | general | 82.00% | 2.31s | 17 |
| Qwen-MT Lite (轻量翻译模型) | translation | 76.00% | 0.36s | 27 |

## 详细分析

### Qwen Plus (通用推荐模型)

**整体表现**: 准确率 83.67%

**错误分布**:
- ACCEPTABLE: 4
- CORRECT: 53
- MISSING_ENTITY: 15

**典型错误案例**:

原文: 从西安咸阳国际机场出发，乘坐高铁可直达兵马俑博物馆。
译文: Departing from Xi'an Xianyang International Airport, you can take a high-speed train directly to the Terracotta Warriors Museum.
  - 兵马俑 → None (标准: Emperor Qinshihuang's Mausoleum Site Museum)

原文: 九寨沟风景区以其独特的自然风光闻名于世。
译文: Jiuzhaigou Scenic Area is world-renowned for its unique natural landscapes.
  - 九寨沟风景区 → None (标准: Jiuzhai Valley)
  - 九寨沟 → jiuzhaigou (标准: Jiuzhai Valley)

原文: 天安门广场是世界上最大的城市广场之一。
译文: Tian’anmen Square is one of the largest city squares in the world.
  - 天安门广场 → None (标准: Tian'anmen Square)
  - 天安门 → None (标准: Tian'anmen Square)

### Qwen-MT Plus (专业翻译模型)

**整体表现**: 准确率 82.67%

**错误分布**:
- ACCEPTABLE: 6
- CORRECT: 51
- MISSING_ENTITY: 15

**典型错误案例**:

原文: 酒店距离深圳宝安国际机场仅30分钟车程，提供免费接送机服务。
译文: The hotel is just a 30-minute drive from Shenzhen Bao’an International Airport and offers complimentary airport shuttle service.
  - 深圳宝安国际机场 → None (标准: Shenzhen Bao'an International Airport)

原文: 从西安咸阳国际机场出发，乘坐高铁可直达兵马俑博物馆。
译文: From Xi’an Xianyang International Airport, you can take a high-speed train directly to the Terracotta Army Museum.
  - 西安咸阳国际机场 → None (标准: Xi'an Xianyang International Airport)
  - 兵马俑 → None (标准: Emperor Qinshihuang's Mausoleum Site Museum)

原文: 九寨沟风景区以其独特的自然风光闻名于世。
译文: The Jiuzhaigou Scenic Area is world-renowned for its unique natural scenery.
  - 九寨沟风景区 → None (标准: Jiuzhai Valley)
  - 九寨沟 → jiuzhaigou (标准: Jiuzhai Valley)

### Qwen Turbo (快速通用模型)

**整体表现**: 准确率 82.67%

**错误分布**:
- ACCEPTABLE: 6
- CORRECT: 52
- MISSING_ENTITY: 14

**典型错误案例**:

原文: 故宫博物院每天接待数万名游客，建议提前网上预约。
译文: The Forbidden City receives tens of thousands of visitors every day, and it is recommended to book tickets online in advance.
  - 故宫博物院 → the forbidden city (标准: The Palace Museum)
  - 故宫 → None (标准: The Palace Museum)

原文: 从西安咸阳国际机场出发，乘坐高铁可直达兵马俑博物馆。
译文: The high-speed rail from Xi'an Xianyang International Airport can reach the Terracotta Warriors Museum directly.
  - 兵马俑 → None (标准: Emperor Qinshihuang's Mausoleum Site Museum)

原文: 九寨沟风景区以其独特的自然风光闻名于世。
译文: The Jiuzhaigou Valley is renowned for its unique natural scenery.
  - 九寨沟风景区 → None (标准: Jiuzhai Valley)
  - 九寨沟 → jiuzhaigou valley (标准: Jiuzhai Valley)

### Qwen Max (最强通用模型)

**整体表现**: 准确率 82.00%

**错误分布**:
- ACCEPTABLE: 2
- CORRECT: 55
- MISSING_ENTITY: 15

**典型错误案例**:

原文: 从西安咸阳国际机场出发，乘坐高铁可直达兵马俑博物馆。
译文: Departing from Xi'an Xianyang International Airport, you can take a high-speed train directly to the Terracotta Warriors Museum.
  - 兵马俑 → None (标准: Emperor Qinshihuang's Mausoleum Site Museum)

原文: 九寨沟风景区以其独特的自然风光闻名于世。
译文: Jiuzhaigou Valley is world-renowned for its unique natural scenery.
  - 九寨沟风景区 → None (标准: Jiuzhai Valley)
  - 九寨沟 → jiuzhaigou valley (标准: Jiuzhai Valley)

原文: 从成都双流国际机场到熊猫基地约需40分钟车程。
译文: From Chengdu Shuangliu International Airport to the Panda Base, it takes about 40 minutes by car.
  - 熊猫基地 → None (标准: Chengdu Research Base of Giant Panda Breeding)

### Qwen-MT Lite (轻量翻译模型)

**整体表现**: 准确率 76.00%

**错误分布**:
- ACCEPTABLE: 7
- CORRECT: 45
- MISSING_ENTITY: 20

**典型错误案例**:

原文: 酒店距离深圳宝安国际机场仅30分钟车程，提供免费接送机服务。
译文: The hotel is just a 30-minute drive from Shenzhen Bao’an International Airport and offers free airport shuttle services.
  - 深圳宝安国际机场 → None (标准: Shenzhen Bao'an International Airport)

原文: 从西安咸阳国际机场出发，乘坐高铁可直达兵马俑博物馆。
译文: From Xi’an Xianyang International Airport, you can take a high-speed train directly to the Terracotta Warriors Museum.
  - 西安咸阳国际机场 → None (标准: Xi'an Xianyang International Airport)
  - 兵马俑 → None (标准: Emperor Qinshihuang's Mausoleum Site Museum)

原文: 九寨沟风景区以其独特的自然风光闻名于世。
译文: Jiuzhaigou Scenic Area is world-renowned for its unique natural scenery.
  - 九寨沟风景区 → None (标准: Jiuzhai Valley)
  - 九寨沟 → jiuzhaigou (标准: Jiuzhai Valley)

## 结论与建议

1. **最佳模型**: Qwen Plus (通用推荐模型)，准确率 83.67%
2. **通用模型表现更优**: 通用模型平均准确率 82.78%，Qwen-MT 系列平均 79.33%，差距 3.44%

3. **常见错误类型**:
   - MISSING_ENTITY: 79 次
   - ACCEPTABLE: 25 次

---

*本报告由 Qoder 自动生成*