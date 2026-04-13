import json
import re

input_file = r"g:\AI code\trae\comfyui出图查看器\json\黑兽9_prompts_export_cleaned.json"
output_file = r"g:\AI code\trae\comfyui出图查看器\json\黑兽9_prompts_export_cleaned_final.json"

# 常见英文单词列表（简单版本）
common_words = {
    'the', 'and', 'is', 'in', 'to', 'of', 'for', 'with', 'on', 'at',
    'by', 'from', 'as', 'are', 'was', 'were', 'been', 'being', 'have',
    'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
    'can', 'may', 'might', 'must', 'shall', 'he', 'she', 'it', 'they',
    'i', 'you', 'we', 'him', 'her', 'them', 'his', 'hers', 'theirs',
    'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom',
    'whose', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
    'every', 'few', 'more', 'most', 'some', 'such', 'no', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'up', 'down', 'in',
    'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
    'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should',
    'now'
}

# 检测乱码的函数
def is_gibberish(text):
    # 检查是否包含中文
    has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
    if has_chinese:
        return False
    
    # 检查是否包含有意义的英文单词
    words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    meaningful_words = [word for word in words if word in common_words]
    
    # 如果没有有意义的英文单词，就是乱码
    if not meaningful_words:
        return True
    
    # 检查特殊字符比例
    special_chars = re.findall(r'[^\w\s\.,!\?;:"\'\(\)\[\]\{\}]', text)
    special_ratio = len(special_chars) / len(text) if text else 0
    
    # 如果特殊字符比例过高，也是乱码
    if special_ratio > 0.4:
        return True
    
    return False

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

processed_data = []
deleted_count = 0

for item in data:
    prompt = item.get("prompt", "")
    
    # 检查是否为空或None
    if not prompt or prompt.strip() == "None":
        deleted_count += 1
        continue
    
    # 检查是否为短数字
    if re.fullmatch(r'\d+\s*\d*', prompt.strip()):
        deleted_count += 1
        continue
    
    # 检查是否为短Exif元数据
    if len(prompt) < 100 and "Exif" in prompt:
        deleted_count += 1
        continue
    
    # 检查是否为乱码
    if is_gibberish(prompt):
        deleted_count += 1
        continue
    
    # 保留有效内容
    processed_data.append(item)

print(f"Total items: {len(data)}")
print(f"Deleted items: {deleted_count}")
print(f"Kept items: {len(processed_data)}")

# 保存处理后的数据
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=2)

print(f"\nProcessed data saved to: {output_file}")
