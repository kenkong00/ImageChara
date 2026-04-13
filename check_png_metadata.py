from PIL import Image
import json
import base64
import re

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\Event Horizon XL v3.0\Image00106.png'

print(f"查看图片: {img_path}")
print("=" * 60)

with Image.open(img_path) as img:
    print(f"图片格式: {img.format}")
    print(f"图片尺寸: {img.size}")
    print(f"图片模式: {img.mode}")
    print()
    print("所有元数据字段:")
    print("-" * 40)
    
    # 打印所有元数据字段
    for key, value in img.info.items():
        print(f"\n字段名: [{key}]")
        print(f"  类型: {type(value).__name__}")
        
        if isinstance(value, bytes):
            print(f"  长度: {len(value)} bytes")
            
            # 尝试多种解码方式
            encodings = ['utf-8', 'latin-1']
            for encoding in encodings:
                try:
                    decoded = value.decode(encoding, errors='ignore')
                    if decoded.strip():
                        filtered = ''.join(c for c in decoded if c.isprintable() or c in '\n\t')
                        if len(filtered.strip()) > 5:
                            print(f"\n  === {encoding} 解码结果 ===")
                            if len(filtered) > 500:
                                print(f"  {filtered[:500]}...")
                            else:
                                print(f"  {filtered}")
                            
                            # 检查是否是JSON
                            try:
                                json_data = json.loads(decoded)
                                print(f"\n  ✓ 是有效的JSON数据")
                                if isinstance(json_data, dict):
                                    print(f"  JSON键: {list(json_data.keys())[:10]}")
                                    for k, v in list(json_data.items())[:3]:
                                        if isinstance(v, str) and len(v) > 100:
                                            print(f"  {k}: {v[:100]}...")
                                        else:
                                            print(f"  {k}: {v}")
                            except:
                                pass
                            
                            # 检查是否包含prompt关键词
                            if 'prompt' in filtered.lower():
                                prompt_match = re.search(r'(?:^|\n)([^\n]+(?:prompt|Prompt)[^\n]*)', filtered)
                                if prompt_match:
                                    print(f"\n  ★ 找到Prompt相关内容: {prompt_match.group(1)[:200]}")
                    break
                except Exception as e:
                    continue
        elif isinstance(value, str):
            print(f"\n  值: {value[:500]}..." if len(value) > 500 else f"  值: {value}")
    
    print("\n" + "=" * 60)
    print("详细分析完成!")
