from PIL import Image
import base64
import json

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\test\108331306 - 副本.png'

print(f"检查中文显示问题: {img_path}")
print("=" * 60)

with Image.open(img_path) as img:
    print(f"格式: {img.format} | 尺寸: {img.size}")
    print(f"元数据字段: {list(img.info.keys())}")
    
    for key, value in img.info.items():
        print(f"\n{'='*50}")
        print(f"字段: [{key}] | 类型: {type(value).__name__}")
        
        if isinstance(value, str):
            # 检查是否是base64
            if len(value) > 100:
                try:
                    decoded = base64.b64decode(value)
                    text = decoded.decode('utf-8')
                    
                    # 尝试解析JSON
                    try:
                        data = json.loads(text)
                        print(f"\n✓ 是有效的JSON数据")
                        print(f"\n原始JSON (前1500字符):")
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:1500])
                        
                        # 检查中文字符
                        json_str = json.dumps(data, ensure_ascii=False)
                        chinese_count = sum(1 for c in json_str if '\u4e00' <= c <= '\u9fff')
                        if chinese_count > 0:
                            print(f"\n★ 包含中文字符: {chinese_count} 个")
                    except:
                        # 不是JSON，直接显示文本
                        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
                        print(f"\n文本内容 (前800字符):")
                        print(text[:800])
                        if chinese_count > 0:
                            print(f"\n★ 包含中文字符: {chinese_count} 个")
                except Exception as e:
                    print(f"Base64解码失败: {e}")
                    print(f"\n原始值前300字符:")
                    print(value[:300])
            else:
                chinese_count = sum(1 for c in value if '\u4e00' <= c <= '\u9fff')
                print(f"\n值: {value[:500]}")
                if chinese_count > 0:
                    print(f"\n★ 包含中文字符: {chinese_count} 个")

# 测试解析器
from parsers import MetadataParser
parser = MetadataParser()

with Image.open(img_path) as img:
    metadata = parser.parse(img)
    
    print("\n" + "=" * 60)
    print("Python解析器结果:")
    print("-"*40)
    
    print(f"\nPrompt长度: {len(metadata['prompt'])}")
    if metadata['prompt']:
        print(f"\nPrompt内容 (前500字符):")
        print(metadata['prompt'][:500])
        
        chinese_count = sum(1 for c in metadata['prompt'] if '\u4e00' <= c <= '\u9fff')
        if chinese_count > 0:
            print(f"\n✅ Python端识别到中文: {chinese_count} 个字符")
        else:
            print(f"\n❌ Python端未检测到中文")
    
    print(f"\n其他字段:")
    print(f"  Seed: {metadata['seed']}")
    print(f"  Steps: {metadata['steps']}")
    print(f"  Model: {metadata['model']}")
