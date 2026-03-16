#!/usr/bin/env python3
"""
多模型翻译评测实验脚本
对比多个 Qwen 模型在酒旅地名翻译任务上的表现
使用 requests 直接调用阿里云百炼 API
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys
import requests

# 添加 evals 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "evals"))

from gazetteer_match import load_gazetteer, check_translation, classify_error


# 实验配置
MODELS = [
    {
        "name": "qwen-mt-plus",
        "description": "Qwen-MT Plus (专业翻译模型)",
        "type": "translation"
    },
    {
        "name": "qwen-mt-lite",
        "description": "Qwen-MT Lite (轻量翻译模型)",
        "type": "translation"
    },
    {
        "name": "qwen-max",
        "description": "Qwen Max (最强通用模型)",
        "type": "general"
    },
    {
        "name": "qwen-plus",
        "description": "Qwen Plus (通用推荐模型)",
        "type": "general"
    },
    {
        "name": "qwen-turbo",
        "description": "Qwen Turbo (快速通用模型)",
        "type": "general"
    }
]

# 增强 Prompt
ENHANCED_PROMPT = """你是一位酒旅领域资深翻译专家，精通中英地名翻译规范。

## 任务
将以下中文翻译为英文

## 地名翻译规则
1. **优先使用官方/通用译名**
   - 故宫 → The Forbidden City (非 Gugong)
   - 外滩 → The Bund (非 Waitan)
   - 长城 → The Great Wall (非 Changcheng)
   - 兵马俑 → Terracotta Warriors (非 Bingmayong)

2. **拼音格式规范**
   - 音节分隔：Xi'an (非 Xian)，Bao'an (非 Baoan)
   - 大小写：Tian'anmen Square

3. **完整名称**
   - 深圳宝安国际机场 → Shenzhen Bao'an International Airport
   - 广州白云机场 → Guangzhou Baiyun International Airport

原文：{source_text}

直接输出译文："""


def call_api(api_key: str, model: str, messages: list, extra_body: dict = None) -> str:
    """调用阿里云百炼 API"""
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1
    }

    # 添加额外参数（如翻译选项）
    if extra_body:
        payload.update(extra_body)

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print(f"API 调用错误: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"响应内容: {e.response.text}")
        return f"[ERROR: {str(e)}]"


def translate_text(api_key: str, model: str, text: str, is_translation_model: bool = False) -> str:
    """调用模型进行翻译"""
    if is_translation_model:
        # Qwen-MT 模型使用翻译专用参数
        extra_body = {
            "translation_options": {
                "source_lang": "zh",
                "target_lang": "en"
            }
        }
        messages = [{"role": "user", "content": text}]
        return call_api(api_key, model, messages, extra_body)
    else:
        # 通用模型使用 Prompt
        prompt = ENHANCED_PROMPT.format(source_text=text)
        messages = [{"role": "user", "content": prompt}]
        return call_api(api_key, model, messages)


def run_experiment(
    testset: List[Dict],
    gazetteer: Dict,
    model_config: Dict,
    api_key: str,
    output_dir: Path
) -> Dict:
    """运行单个模型的实验"""
    model_name = model_config["name"]
    is_translation_model = model_config["type"] == "translation"

    print(f"\n{'='*60}")
    print(f"测试模型: {model_config['description']}")
    print(f"{'='*60}")

    translations = []
    results = []
    total_accuracy = 0
    error_counts = {}
    latencies = []

    for i, item in enumerate(testset):
        source = item["source"]

        # 计时
        start_time = time.time()
        translation = translate_text(api_key, model_name, source, is_translation_model)
        latency = time.time() - start_time
        latencies.append(latency)

        translations.append(translation)

        # 评测
        eval_result = check_translation(source, translation, gazetteer)
        total_accuracy += eval_result["accuracy"]

        # 统计错误
        for detail in eval_result["details"]:
            error_type = classify_error(detail)
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        result = {
            "id": item.get("id", str(i)),
            "source": source,
            "translation": translation,
            "accuracy": eval_result["accuracy"],
            "details": eval_result["details"]
        }
        results.append(result)

        # 进度显示
        if (i + 1) % 10 == 0:
            print(f"  已完成: {i+1}/{len(testset)}, 当前准确率: {total_accuracy/(i+1):.2%}")

    avg_accuracy = total_accuracy / len(testset)
    avg_latency = sum(latencies) / len(latencies)

    # 统计总地名数
    total_entities = sum(len(r["details"]) for r in results)

    experiment_result = {
        "model": model_name,
        "model_description": model_config["description"],
        "model_type": model_config["type"],
        "timestamp": datetime.now().isoformat(),
        "total_samples": len(testset),
        "total_entities": total_entities,
        "accuracy": avg_accuracy,
        "avg_latency": avg_latency,
        "error_distribution": error_counts,
        "results": results
    }

    # 保存详细结果
    result_file = output_dir / f"translations_{model_name}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(experiment_result, f, ensure_ascii=False, indent=2)
    print(f"结果已保存: {result_file}")

    return experiment_result


def generate_comparison_report(all_results: List[Dict], output_dir: Path) -> str:
    """生成对比报告"""
    report = []
    report.append("# 酒旅地名翻译多模型对比实验报告")
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n---\n")

    # 实验概述
    report.append("## 实验概述")
    report.append(f"- 测试样本数: {all_results[0]['total_samples']} 条")
    report.append(f"- 地名实体数: {all_results[0]['total_entities']} 个")
    report.append(f"- 测试模型数: {len(all_results)} 个")
    report.append(f"- 评测维度: 地名翻译准确性\n")

    # 结果汇总表
    report.append("## 结果汇总")
    report.append("\n| 模型 | 类型 | 准确率 | 平均延迟 | 错误数 |")
    report.append("|------|------|--------|----------|--------|")

    # 按准确率排序
    sorted_results = sorted(all_results, key=lambda x: x["accuracy"], reverse=True)

    for r in sorted_results:
        error_count = sum(v for k, v in r["error_distribution"].items() if k != "CORRECT")
        report.append(f"| {r['model_description']} | {r['model_type']} | {r['accuracy']:.2%} | {r['avg_latency']:.2f}s | {error_count} |")

    # 详细分析
    report.append("\n## 详细分析\n")

    for r in sorted_results:
        report.append(f"### {r['model_description']}")
        report.append(f"\n**整体表现**: 准确率 {r['accuracy']:.2%}")
        report.append(f"\n**错误分布**:")
        for error_type, count in sorted(r["error_distribution"].items()):
            report.append(f"- {error_type}: {count}")

        # 展示部分错误案例
        error_cases = [res for res in r["results"] if res["accuracy"] < 1.0][:5]
        if error_cases:
            report.append(f"\n**典型错误案例**:")
            for case in error_cases[:3]:
                report.append(f"\n原文: {case['source']}")
                report.append(f"译文: {case['translation']}")
                for detail in case["details"]:
                    if detail.get("status") != "exact_match":
                        en_found = detail.get('en_found', '[缺失]')
                        report.append(f"  - {detail['zh']} → {en_found} (标准: {detail['en_standard']})")
        report.append("")

    # 结论
    report.append("## 结论与建议\n")

    best_model = sorted_results[0]
    report.append(f"1. **最佳模型**: {best_model['model_description']}，准确率 {best_model['accuracy']:.2%}")

    # 专业翻译模型 vs 通用模型对比
    translation_models = [r for r in sorted_results if r["model_type"] == "translation"]
    general_models = [r for r in sorted_results if r["model_type"] == "general"]

    if translation_models and general_models:
        avg_trans = sum(r["accuracy"] for r in translation_models) / len(translation_models)
        avg_general = sum(r["accuracy"] for r in general_models) / len(general_models)
        diff = avg_trans - avg_general

        if diff > 0:
            report.append(f"2. **专业翻译模型表现更优**: Qwen-MT 系列平均准确率 {avg_trans:.2%}，通用模型平均 {avg_general:.2%}，差距 {diff:.2%}")
        else:
            report.append(f"2. **通用模型表现更优**: 通用模型平均准确率 {avg_general:.2%}，Qwen-MT 系列平均 {avg_trans:.2%}，差距 {-diff:.2%}")

    # 常见错误分析
    report.append("\n3. **常见错误类型**:")
    all_errors = {}
    for r in all_results:
        for error_type, count in r["error_distribution"].items():
            if error_type != "CORRECT":
                all_errors[error_type] = all_errors.get(error_type, 0) + count

    for error_type, count in sorted(all_errors.items(), key=lambda x: -x[1]):
        report.append(f"   - {error_type}: {count} 次")

    report.append("\n---")
    report.append("\n*本报告由 Qoder 自动生成*")

    return "\n".join(report)


def main():
    """主函数"""
    # 获取 API Key
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("错误: 请设置 DASHSCOPE_API_KEY 环境变量")
        sys.exit(1)

    # 配置路径
    project_dir = Path(__file__).parent
    data_dir = project_dir / "data"
    output_dir = project_dir / "reports"
    output_dir.mkdir(exist_ok=True)

    # 加载测试集
    testset_file = data_dir / "testset.json"
    with open(testset_file, "r", encoding="utf-8") as f:
        testset_data = json.load(f)
    testset = testset_data.get("testset", [])
    print(f"已加载测试集: {len(testset)} 条")

    # 加载地名库
    gazetteer = load_gazetteer(str(data_dir / "gazetteer"))
    print(f"已加载地名库: {len(gazetteer['all_zh'])} 个中文地名")

    # 运行所有模型实验
    all_results = []

    for model_config in MODELS:
        try:
            result = run_experiment(
                testset=testset,
                gazetteer=gazetteer,
                model_config=model_config,
                api_key=api_key,
                output_dir=output_dir
            )
            all_results.append(result)
            print(f"\n{model_config['description']} 准确率: {result['accuracy']:.2%}\n")
        except Exception as e:
            print(f"模型 {model_config['name']} 测试失败: {e}")
            import traceback
            traceback.print_exc()
            continue

    # 生成对比报告
    if all_results:
        report = generate_comparison_report(all_results, output_dir)

        # 保存报告
        report_file = output_dir / "experiment_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n实验报告已保存: {report_file}")

        # 同时输出到控制台
        print("\n" + "="*60)
        print(report)

    # 保存汇总数据
    summary = {
        "timestamp": datetime.now().isoformat(),
        "models_tested": len(all_results),
        "results": [
            {
                "model": r["model"],
                "accuracy": r["accuracy"],
                "avg_latency": r["avg_latency"],
                "error_distribution": r["error_distribution"]
            }
            for r in all_results
        ]
    }

    summary_file = output_dir / "experiment_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"汇总数据已保存: {summary_file}")


if __name__ == "__main__":
    main()
