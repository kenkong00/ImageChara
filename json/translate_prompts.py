import json
import re
from googletrans import Translator

input_file = r"g:\AI code\trae\comfyui出图查看器\json\moody_v7_prompts_export_cleaned 翻译.json"
output_file = r"g:\AI code\trae\comfyui出图查看器\json\moody_v7_prompts_export_cleaned 翻译完成.json"

# 初始化翻译器
translator = Translator()

# 检查是否包含中文字符
def contains_chinese(text):
    return bool(re.search(r'[\u4e00-\u9fff]', text))

# 翻译文本
def translate_text(text):
    # 处理 <lora:xxx> 标签，保留不翻译
    lora_pattern = re.compile(r'<lora:[^>]+>')
    lora_matches = lora_pattern.findall(text)
    
    # 临时替换 lora 标签
    temp_text = text
    for i, match in enumerate(lora_matches):
        temp_text = temp_text.replace(match, f"__LORA_{i}__")
    
    # 翻译文本
    try:
        # 分段处理长文本
        max_length = 5000
        segments = []
        for i in range(0, len(temp_text), max_length):
            segments.append(temp_text[i:i+max_length])
        
        translated = ""
        for segment in segments:
            result = translator.translate(segment, dest='zh-cn')
            translated += result.text
    except Exception as e:
        print(f"Translation error: {e}")
        translated = temp_text
    
    # 恢复 lora 标签
    for i, match in enumerate(lora_matches):
        translated = translated.replace(f"__LORA_{i}__", match)
    
    return translated

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
translated_count = 0
skipped_count = 0

print(f"Processing {total} items...")

for i, item in enumerate(data):
    if i % 10 == 0:
        print(f"Processing item {i}/{total}...")
    
    prompt = item.get("prompt", "")
    
    if not prompt:
        skipped_count += 1
        continue
    
    if not contains_chinese(prompt):
        # 全英文，翻译
        translated = translate_text(prompt)
        item["prompt"] = translated
        translated_count += 1
    else:
        # 包含中文，检查是否需要部分翻译
        # 简单处理：如果大部分是英文，还是翻译
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', prompt))
        total_chars = len(prompt)
        if chinese_chars / total_chars < 0.3:
            # 中文少于30%，翻译
            translated = translate_text(prompt)
            item["prompt"] = translated
            translated_count += 1
        else:
            # 中文较多，跳过
            skipped_count += 1

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n=== Summary ===")
print(f"Total items: {total}")
print(f"Translated: {translated_count}")
print(f"Skipped (already Chinese): {skipped_count}")
print(f"\nOutput saved to: {output_file}")
