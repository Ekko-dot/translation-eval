# 酒旅领域地名翻译质量评测 + Prompt Engineering 优化项目

## 项目概述

- **领域**: 酒店与旅游 (Hotel & Tourism)
- **核心问题**: 地名/实体名翻译标准化（机场、景点、酒店、商圈、车站等）
- **语言对**: 中英双向翻译
- **评测指标**: 地名翻译准确性、语义保真度
- **目标**: 构建地名翻译评测系统，优化 Prompt 提升地名翻译准确率

---

## 典型问题示例

| 中文原文 | 错误翻译 | 正确翻译 | 问题类型 |
|---------|---------|---------|---------|
| 深圳宝安机场 | Shenzhen Baoan Airport | Shenzhen Bao'an Airport | 拼音格式错误 |
| 广州白云机场 | Guangzhou Baiyun Airport | Guangzhou Baiyun International Airport | 名称不完整 |
| 外滩 | Waitan | The Bund | 未使用通用译名 |
| 故宫 | Gugong | The Forbidden City | 未使用官方译名 |
| 天安门广场 | Tiananmen Square | Tian'anmen Square | 拼音格式错误 |
| 颐和园 | Yiheyuan | The Summer Palace | 未使用通用译名 |
| 宽窄巷子 | Kuanzhai Xiangzi | Kuanzhai Alley | 语义理解偏差 |
| 春熙路 | Chunxi Road | Chunxi Road Pedestrian Street | 信息不完整 |
| 东方明珠 | Dongfang Mingzhu | Oriental Pearl Tower | 未使用通用译名 |
| 长城 | Changcheng | The Great Wall | 未使用通用译名 |
| 兵马俑 | Bingmayong | Terracotta Warriors | 未使用通用译名 |
| 九寨沟 | Jiuzhaigou | Jiuzhai Valley | 语义理解偏差 |

---

## Phase 1: 项目架构设计

### 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    地名翻译评测优化系统                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  地名库     │───▶│  评测引擎   │───▶│  Prompt优化 │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                  │                  │                  │
│        ▼                  ▼                  ▼                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │ 机场名称    │    │ 地名匹配    │    │ 提示词版本  │         │
│  │ 景点名称    │    │ 拼音检查    │    │ 优化记录    │         │
│  │ 酒店名称    │    │ 语义评估    │    │ 最佳实践    │         │
│  │ 商圈地名    │    │ 错误分类    │    │ 效果对比    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 核心模块

1. **地名数据库** (`data/gazetteer/`)
   - `airports.json` - 国内外机场中英对照
   - `attractions.json` - 景点名称中英对照
   - `hotels.json` - 知名酒店品牌中英对照
   - `districts.json` - 商圈/区域名称中英对照
   - `stations.json` - 火车站/地铁站名称

2. **评测引擎** (`evals/`)
   - `gazetteer_match.py` - 地名库精确匹配
   - `pinyin_check.py` - 拼音格式检查
   - `semantic_eval.py` - 语义保真度评估
   - `error_classifier.py` - 错误类型分类

3. **Prompt优化** (`prompts/`)
   - `baseline.md` - 基线提示词
   - `iterations/` - 迭代版本
   - `best_practices.md` - 最佳实践

---

## Phase 2: 地名数据库构建

### 2.1 数据来源

**机场名称**:
- IATA 官方机场代码表
- 中国民航局机场名称标准
- Wikipedia 机场列表

**景点名称**:
- 国家旅游局官方译名
- UNESCO 世界遗产名录
- 各省市文旅局官方译名
- TripAdvisor/携程双语页面

**酒店品牌**:
- 各酒店集团官网
- OTA平台双语数据

### 2.2 数据格式

```json
{
  "airports": [
    {
      "zh": "深圳宝安国际机场",
      "en": "Shenzhen Bao'an International Airport",
      "iata": "SZX",
      "aliases": ["深圳宝安机场", "深圳机场", "Shenzhen Airport"]
    },
    {
      "zh": "广州白云国际机场",
      "en": "Guangzhou Baiyun International Airport",
      "iata": "CAN",
      "aliases": ["广州白云机场", "广州机场", "Guangzhou Airport"]
    }
  ],
  "attractions": [
    {
      "zh": "故宫博物院",
      "en": "The Palace Museum",
      "aliases": ["故宫", "紫禁城", "The Forbidden City"],
      "location": "北京"
    },
    {
      "zh": "外滩",
      "en": "The Bund",
      "aliases": ["外滩风景区"],
      "location": "上海"
    }
  ]
}
```

### 2.3 预期产出

- [ ] 中国主要机场名称库 (200+)
- [ ] 国内外热门景点名称库 (500+)
- [ ] 酒店品牌名称库 (100+)
- [ ] 城市商圈名称库 (200+)
- [ ] 测试数据集 (100+ 样本)

---

## Phase 3: 评测指标体系

### 3.1 地名准确性评测

**评测维度**:

1. **精确匹配** - 译文是否与地名库完全匹配
2. **别名匹配** - 是否使用了可接受的别名
3. **拼音格式** - 拼音分隔符、大小写是否正确
4. **完整性** - 是否遗漏了"国际机场"、"博物馆"等后缀

**评分规则**:

| 情况 | 得分 | 说明 |
|------|------|------|
| 完全匹配标准译名 | 1.0 | 翻译正确 |
| 匹配别名 | 0.9 | 可接受但非最佳 |
| 拼音格式错误 | 0.7 | 如 Baoan vs Bao'an |
| 遗漏后缀 | 0.8 | 如缺少 International |
| 使用直译非通用译名 | 0.5 | 如 Gugong vs The Forbidden City |
| 翻译错误 | 0.0 | 完全错误 |

### 3.2 语义保真度评测

**评测方法**:

1. **关键信息提取** - 提取原文中的地名实体
2. **信息覆盖检查** - 检查译文是否包含所有地名
3. **语义相似度** - 使用嵌入模型计算语义相似度
4. **LLM 辅助判断** - 使用 LLM 判断翻译质量

---

## Phase 4: Prompt Engineering 设计

### 4.1 基线提示词 (v0.1)

```markdown
你是一位专业的酒旅领域翻译专家。

将以下中文翻译为英文：

{source_text}

要求：
1. 保持语义准确
2. 使用地道的英文表达
```

### 4.2 增强提示词 (v0.2)

```markdown
你是一位酒旅领域资深翻译专家，精通中英地名翻译规范。

## 任务
将以下中文翻译为英文

## 地名翻译规则
1. **优先使用官方/通用译名**
   - 故宫 → The Forbidden City (非 Gugong)
   - 外滩 → The Bund (非 Waitan)
   - 长城 → The Great Wall (非 Changcheng)

2. **拼音格式规范**
   - 音节分隔：Bao'an (非 Baoan)
   - 大小写：Tian'anmen (非 tian'anmen)

3. **完整名称**
   - 深圳宝安国际机场 → Shenzhen Bao'an International Airport
   - 广州白云机场 → Guangzhou Baiyun International Airport

## 常见地名参考
{gazetteer_context}

原文：{source_text}

译文：
```

### 4.3 专家提示词 (v0.3)

```markdown
# 角色定义
你是酒旅领域资深翻译专家，专注于中英地名翻译。你熟悉：
- IATA 机场命名规范
- UNESCO 世界遗产官方译名
- 中国地名拼音拼写规则
- 旅游行业通用译法

# 地名翻译核心原则

## 1. 官方译名优先
| 中文 | 正确译名 | 错误示例 |
|------|---------|---------|
| 故宫 | The Forbidden City | Gugong, Imperial Palace |
| 外滩 | The Bund | Waitan, The Bund Area |
| 颐和园 | The Summer Palace | Yiheyuan |
| 兵马俑 | Terracotta Warriors | Bingmayong |
| 九寨沟 | Jiuzhai Valley | Jiuzhaigou |

## 2. 拼音格式规范
- 音节分隔符：西安 → Xi'an (非 Xian)
- 大写规则：Tian'anmen Square
- 连写规则：Beijing (非 Bei Jing)

## 3. 机场命名规范
- 格式：城市 + 名称 + International Airport
- 示例：Shenzhen Bao'an International Airport

## 地名库（相关条目）
{relevant_gazetteer}

# 翻译任务
原文：{source_text}

请翻译并标注使用到的地名：
```
译文：[翻译结果]
地名：[使用的地名译名]
```
```

---

## Phase 5: 自动化评测流水线

### 流程图

```
测试样本 → 翻译执行 → 地名识别 → 匹配评测 → 语义评测 → 报告生成
              ↓            ↓           ↓           ↓
           翻译结果     提取地名    准确性分数   保真度分数
              ↓            ↓           ↓           ↓
           存储结果     标注问题    错误分类    优化建议
```

### 实现步骤

1. **批量翻译** - 调用模型翻译测试集
2. **地名识别** - 从原文和译文中提取地名
3. **匹配评测** - 与地名库对比，计算准确性
4. **语义评测** - 计算语义保真度
5. **报告生成** - 汇总结果，生成优化建议

---

## Phase 6: 迭代优化

### 优化循环

```
基线测试 → 问题分析 → 提示词调整 → 再测试 → 效果对比 → ...
```

### 验证标准

- 地名准确率提升 > 20%
- 拼音格式错误减少 > 80%
- 语义保真度保持 > 90%

---

## 下一步行动

1. ✅ 项目架构设计
2. ⏳ 收集地名数据
3. ⏳ 构建测试集
4. ⏳ 实现评测脚本
5. ⏳ 设计提示词
6. ⏳ 迭代优化

---

## 需要确认

1. **地名范围** - 是否只关注中国地名，还是也需要国外地名的中文翻译？
2. **测试集规模** - 初始测试集需要多少样本？
3. **评测标准** - 是否有现成的参考译文，还是需要人工标注？
