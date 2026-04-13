from PIL import Image
import base64
import json

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\啊啊啊\k_00055_.png'

print(f"分析中文Prompt的PNG: {img_path}")
print("=" * 60)

with Image.open(img_path) as img:
    print(f"格式: {img.format} | 尺寸: {img.size} | 模式: {img.mode}")
    print(f"\n元数据字段: {list(img.info.keys())}")
    
    for key, value in img.info.items():
        print(f"\n{'='*50}")
        print(f"字段: [{key}]")
        print(f"类型: {type(value).__name__} | 长度: {len(str(value))}")
        
        if isinstance(value, str):
            # 尝试base64解码（如果是exif_b64）
            if key == 'exif_b64':
                try:
                    decoded_bytes = base64.b64decode(value)
                    print(f"\nBase64解码成功! 二进制长度: {len(decoded_bytes)} bytes")
                    
                    # 尝试多种编码
                    for encoding in ['utf-8', 'utf-16-le', 'utf-16-be', 'gbk', 'gb2312', 'latin-1']:
                        try:
                            text = decoded_bytes.decode(encoding, errors='ignore')
                            if len(text.strip()) > 5:
                                print(f"\n--- {encoding} 编码 ---")
                                # 显示前800字符
                                preview = text[:800] if len(text) > 800 else text
                                print(preview)
                                
                                # 检查是否包含中文
                                chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
                                if chinese_chars > 0:
                                    print(f"\n★ 发现中文字符: {chinese_chars} 个")
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"Base64解码失败: {e}")
            else:
                print(f"\n值: {value[:500]}..." if len(value) > 500 else f"\n值: {value}")

print("\n" + "=" * 60)

# 测试解析器
from parsers import MetadataParser
parser = MetadataParser()

with Image.open(img_path) as img:
    metadata = parser.parse(img)
    
    print("\n解析器结果:")
    print("-"*40)
    print(f"Prompt: {metadata['prompt'][:300]}..." if len(metadata['prompt']) > 300 else f"Prompt: {metadata['prompt']}")
    print(f"Seed: {metadata['seed']}")
    print(f"Steps: {metadata['steps']}")
    print(f"Model: {metadata['model']}")
    
    if metadata['prompt']:
        # 检查是否包含中文
        chinese_count = sum(1 for c in metadata['prompt'] if '\u4e00' <= c <= '\u9fff')
        if chinese_count > 0:
            print(f"\n✓ Prompt包含中文 ({chinese_count}个字符)")
        else:
            print(f"\n✗ Prompt不包含中文")
