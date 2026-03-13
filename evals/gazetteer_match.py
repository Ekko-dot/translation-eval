#!/usr/bin/env python3
"""
地名翻译评测脚本
评测维度：地名准确性、语义保真度
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 加载地名库
def load_gazetteer(gazetteer_dir: str) -> Dict:
    """加载所有地名库"""
    gazetteer = {
        "airports": {},
        "attractions": {},
        "all_zh": {},
        "all_en": {}
    }

    gazetteer_path = Path(gazetteer_dir)

    # 加载机场
    airports_file = gazetteer_path / "airports.json"
    if airports_file.exists():
        with open(airports_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for airport in data.get("airports", []):
                zh = airport["zh"]
                en = airport["en"]
                gazetteer["airports"][zh] = en
                gazetteer["all_zh"][zh] = {"en": en, "type": "airport"}
                gazetteer["all_en"][en.lower()] = {"zh": zh, "type": "airport"}
                # 添加别名
                for alias in airport.get("aliases_zh", []):
                    gazetteer["all_zh"][alias] = {"en": en, "type": "airport"}
                for alias in airport.get("aliases_en", []):
                    gazetteer["all_en"][alias.lower()] = {"zh": zh, "type": "airport"}

    # 加载景点
    attractions_file = gazetteer_path / "attractions.json"
    if attractions_file.exists():
        with open(attractions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for attraction in data.get("attractions", []):
                zh = attraction["zh"]
                en = attraction["en"]
                gazetteer["attractions"][zh] = en
                gazetteer["all_zh"][zh] = {"en": en, "type": "attraction"}
                gazetteer["all_en"][en.lower()] = {"zh": zh, "type": "attraction"}
                # 添加别名
                for alias in attraction.get("aliases_zh", []):
                    gazetteer["all_zh"][alias] = {"en": en, "type": "attraction"}
                for alias in attraction.get("aliases_en", []):
                    gazetteer["all_en"][alias.lower()] = {"zh": zh, "type": "attraction"}

    return gazetteer


def extract_entities(source: str, gazetteer: Dict) -> List[Dict]:
    """从源文本中提取地名实体"""
    entities = []
    found = set()

    # 按长度排序，优先匹配长地名
    sorted_terms = sorted(gazetteer["all_zh"].keys(), key=len, reverse=True)

    for term in sorted_terms:
        if term in source and term not in found:
            entity_info = gazetteer["all_zh"][term]
            entities.append({
                "zh": term,
                "en_standard": entity_info["en"],
                "type": entity_info["type"]
            })
            found.add(term)

    return entities


def check_translation(source: str, translation: str, gazetteer: Dict) -> Dict:
    """检查翻译质量"""
    # 提取源文本中的地名
    entities = extract_entities(source, gazetteer)

    if not entities:
        return {
            "entities": [],
            "accuracy": 1.0,
            "matched": 0,
            "total": 0,
            "details": []
        }

    details = []
    matched = 0

    for entity in entities:
        zh = entity["zh"]
        en_standard = entity["en_standard"]

        # 检查是否包含标准译名
        if en_standard in translation:
            details.append({
                "zh": zh,
                "en_found": en_standard,
                "en_standard": en_standard,
                "status": "exact_match",
                "score": 1.0
            })
            matched += 1
            continue

        # 检查是否包含别名
        found_alias = False
        for alias_en, info in gazetteer["all_en"].items():
            if info["zh"] == zh and alias_en in translation.lower():
                # 检查是否是可接受的别名
                details.append({
                    "zh": zh,
                    "en_found": alias_en,
                    "en_standard": en_standard,
                    "status": "alias_match",
                    "score": 0.9
                })
                matched += 1
                found_alias = True
                break

        if not found_alias:
            # 检查拼音格式问题
            # 简单检查：是否有类似但格式错误的翻译
            pinyin_pattern = re.sub(r"[^\w\s]", "", zh.lower())
            if pinyin_pattern in translation.lower():
                details.append({
                    "zh": zh,
                    "en_found": pinyin_pattern,
                    "en_standard": en_standard,
                    "status": "pinyin_error",
                    "score": 0.5
                })
                matched += 0.5
            else:
                details.append({
                    "zh": zh,
                    "en_found": None,
                    "en_standard": en_standard,
                    "status": "missing",
                    "score": 0.0
                })

    accuracy = matched / len(entities) if entities else 1.0

    return {
        "entities": entities,
        "accuracy": accuracy,
        "matched": matched,
        "total": len(entities),
        "details": details
    }


def classify_error(detail: Dict) -> str:
    """分类错误类型"""
    status = detail.get("status", "")

    if status == "exact_match":
        return "CORRECT"
    elif status == "alias_match":
        return "ACCEPTABLE"
    elif status == "pinyin_error":
        return "PINYIN_FORMAT"
    elif status == "missing":
        return "MISSING_ENTITY"
    else:
        return "UNKNOWN"


def evaluate_batch(testset: List[Dict], translations: List[str], gazetteer: Dict) -> Dict:
    """批量评测"""
    results = []
    total_accuracy = 0
    error_counts = {}

    for i, item in enumerate(testset):
        source = item["source"]
        translation = translations[i] if i < len(translations) else ""

        result = check_translation(source, translation, gazetteer)
        result["id"] = item.get("id", str(i))
        result["source"] = source
        result["translation"] = translation

        total_accuracy += result["accuracy"]

        # 统计错误类型
        for detail in result["details"]:
            error_type = classify_error(detail)
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        results.append(result)

    avg_accuracy = total_accuracy / len(testset) if testset else 0

    return {
        "total_samples": len(testset),
        "average_accuracy": avg_accuracy,
        "error_distribution": error_counts,
        "results": results
    }


def generate_report(eval_result: Dict) -> str:
    """生成评测报告"""
    report = []
    report.append("=" * 60)
    report.append("地名翻译评测报告")
    report.append("=" * 60)
    report.append(f"\n总样本数: {eval_result['total_samples']}")
    report.append(f"平均准确率: {eval_result['average_accuracy']:.2%}")
    report.append("\n错误类型分布:")
    for error_type, count in sorted(eval_result["error_distribution"].items()):
        report.append(f"  - {error_type}: {count}")

    report.append("\n" + "-" * 60)
    report.append("详细结果:")
    report.append("-" * 60)

    for result in eval_result["results"]:
        report.append(f"\n[{result['id']}] 准确率: {result['accuracy']:.2%}")
        report.append(f"原文: {result['source']}")
        report.append(f"译文: {result['translation']}")

        for detail in result["details"]:
            status = classify_error(detail)
            if status != "CORRECT":
                report.append(f"  ⚠️ {detail['zh']} → {detail.get('en_found', '[缺失]')} (标准: {detail['en_standard']}) [{status}]")
            else:
                report.append(f"  ✓ {detail['zh']} → {detail['en_standard']}")

    return "\n".join(report)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="地名翻译评测工具")
    parser.add_argument("--gazetteer", "-g", default="~/.openclaw/workspace/translation-eval/data/gazetteer", help="地名库目录")
    parser.add_argument("--testset", "-t", default="~/.openclaw/workspace/translation-eval/data/testset.json", help="测试集文件")
    parser.add_argument("--translations", "-T", help="翻译结果文件")
    parser.add_argument("--output", "-o", help="输出报告文件")

    args = parser.parse_args()

    # 加载地名库
    gazetteer_dir = Path(args.gazetteer).expanduser()
    gazetteer = load_gazetteer(str(gazetteer_dir))
    print(f"已加载地名库: {len(gazetteer['all_zh'])} 个中文地名, {len(gazetteer['all_en'])} 个英文地名")

    # 加载测试集
    testset_file = Path(args.testset).expanduser()
    with open(testset_file, 'r', encoding='utf-8') as f:
        testset_data = json.load(f)
    testset = testset_data.get("testset", [])
    print(f"已加载测试集: {len(testset)} 条")

    # 如果提供了翻译结果
    if args.translations:
        trans_file = Path(args.translations).expanduser()
        with open(trans_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
    else:
        # 使用空翻译进行测试
        translations = [""] * len(testset)

    # 执行评测
    eval_result = evaluate_batch(testset, translations, gazetteer)

    # 生成报告
    report = generate_report(eval_result)
    print(report)

    # 保存报告
    if args.output:
        output_file = Path(args.output).expanduser()
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存至: {output_file}")

    return eval_result


if __name__ == "__main__":
    main()
