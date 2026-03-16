#!/usr/bin/env python3
"""
使用 NLLB 模型进行中英翻译
"""

import os
# 设置 HuggingFace 镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import json
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from pathlib import Path
import time

def load_model():
    """加载 NLLB 模型"""
    model_name = "facebook/nllb-200-distilled-600M"
    print(f"正在加载模型: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    # 检查是否有 GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"使用设备: {device}")
    model = model.to(device)
    
    return tokenizer, model, device

def translate(text, tokenizer, model, device, src_lang="zho_Hans", tgt_lang="eng_Latn"):
    """翻译文本"""
    # 设置源语言
    tokenizer.src_lang = src_lang
    
    # 编码
    encoded = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
    encoded = {k: v.to(device) for k, v in encoded.items()}
    
    # 获取目标语言的 token id
    tgt_lang_id = tokenizer.convert_tokens_to_ids(tgt_lang)
    
    # 生成翻译
    generated_tokens = model.generate(
        **encoded,
        forced_bos_token_id=tgt_lang_id,
        max_length=512,
        num_beams=5,
        early_stopping=True
    )
    
    # 解码
    translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    return translation

def main():
    # 加载模型
    tokenizer, model, device = load_model()
    
    # 加载测试数据
    testset_path = Path("data/testset.json")
    with open(testset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    testset = data["testset"]
    print(f"加载了 {len(testset)} 条测试数据")
    
    # 翻译
    translations = []
    start_time = time.time()
    
    for i, item in enumerate(testset):
        source = item["source"]
        print(f"\n[{i+1}/{len(testset)}] 翻译中...")
        print(f"原文: {source}")
        
        translation = translate(source, tokenizer, model, device)
        print(f"译文: {translation}")
        
        translations.append({
            "id": item["id"],
            "source": source,
            "translation": translation,
            "entities": item.get("entities", [])
        })
    
    elapsed_time = time.time() - start_time
    print(f"\n翻译完成! 总耗时: {elapsed_time:.2f} 秒")
    print(f"平均每条: {elapsed_time/len(testset):.2f} 秒")
    
    # 保存结果
    output_path = Path("reports/nllb_translations.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "model": "facebook/nllb-200-distilled-600M",
            "total": len(translations),
            "elapsed_time": elapsed_time,
            "translations": translations
        }, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存至: {output_path}")
    
    # 提取纯翻译文本用于评测
    translations_only = [t["translation"] for t in translations]
    translations_path = Path("reports/nllb_translations_only.json")
    with open(translations_path, 'w', encoding='utf-8') as f:
        json.dump(translations_only, f, ensure_ascii=False, indent=2)
    
    print(f"纯翻译结果已保存至: {translations_path}")

if __name__ == "__main__":
    main()
