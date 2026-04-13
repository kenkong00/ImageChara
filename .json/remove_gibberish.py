import json
import re

input_file = r"g:\AI code\trae\comfyui出图查看器\json\黑兽9_prompts_export_cleaned.json"
output_file = r"g:\AI code\trae\comfyui出图查看器\json\黑兽9_prompts_export_cleaned_final.json"

# 检测乱码的函数
def is_gibberish(text):
    # 检查特殊字符比例
    # 只保留字母、数字、中文、空格和常见标点
    normal_chars = re.findall(r'[\w\s\u4e00-\u9fff\.,!\?;:"\'\(\)\[\]\{\}]', text)
    if len(normal_chars) < len(text) * 0.5:  # 正常字符少于50%
        return True
    
    # 检查可打印字符比例
    printable_chars = re.findall(r'[\x20-\x7E\u4e00-\u9fff]', text)
    if len(printable_chars) < len(text) * 0.6:  # 可打印字符少于60%
        return True
    
    # 检查是否包含明显的乱码特征
    if re.search(r'[\x00-\x1F\x7F-\x9F]', text):  # 控制字符
        return True
    
    # 检查是否有过多的连续特殊字符
    if re.search(r'[^\w\s\u4e00-\u9fff]{10,}', text):  # 连续10个以上特殊字符
        return True
    
    return False

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

total = len(data)
kept = 0
deleted = 0

final_result = []

for item in data:
    prompt = item.get("prompt", "")
    item_id = item.get("id", "unknown")
    
    if not prompt or prompt.strip() == "None":
        deleted += 1
        continue
    
    if re.fullmatch(r'\d+\s*\d*', prompt.strip()):
        deleted += 1
        continue
    
    if len(prompt) < 100 and "Exif" in prompt:
        deleted += 1
        continue
    
    if is_gibberish(prompt):
        deleted += 1
        print(f"  Deleted gibberish: {item_id}")
        continue
    
    final_result.append(item)
    kept += 1

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(final_result, f, ensure_ascii=False, indent=2)

print(f"\n=== Summary ===")
print(f"Total entries: {total}")
print(f"Kept: {len(final_result)}")
print(f"Deleted: {total - len(final_result)}")
print(f"\nOutput saved to: {output_file}")
