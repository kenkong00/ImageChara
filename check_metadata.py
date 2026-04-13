from PIL import Image
import json
import base64
import re

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\Juggernaut XL Ragnarok_by_RunDiffusion\00020-13691895.webp'

print(f"查看图片: {img_path}")
print("=" * 50)

with Image.open(img_path) as img:
    print(f"图片格式: {img.format}")
    print(f"图片尺寸: {img.size}")
    print(f"图片模式: {img.mode}")
    print()
    print("元数据字段:")
    print("-" * 30)
    
    # 打印所有元数据字段
    for key, value in img.info.items():
        print(f"字段: {key}")
        if isinstance(value, bytes):
            # 尝试解码字节数据
            try:
                decoded = value.decode('utf-8')
                print(f"  值: {decoded[:500]}..." if len(decoded) > 500 else f"  值: {decoded}")
            except:
                # 尝试base64解码
                try:
                    decoded = base64.b64decode(value)
                    decoded_str = decoded.decode('utf-8')
                    print(f"  Base64解码后: {decoded_str[:500]}..." if len(decoded_str) > 500 else f"  Base64解码后: {decoded_str}")
                except:
                    # 尝试其他编码
                    encodings = ['utf-16', 'utf-16-be', 'utf-16-le', 'latin-1']
                    for encoding in encodings:
                        try:
                            decoded = value.decode(encoding, errors='ignore')
                            # 过滤非打印字符
                            filtered = ''.join(c for c in decoded if c.isprintable() or c in '\n\t')
                            if filtered.strip():
                                print(f"  {encoding}解码后: {filtered[:500]}..." if len(filtered) > 500 else f"  {encoding}解码后: {filtered}")
                                break
                        except:
                            continue
                    else:
                        print(f"  值: (二进制数据, 长度: {len(value)} bytes)")
        else:
            print(f"  值: {value}")
        print()
    
    # 特别处理exif数据
    if 'exif' in img.info:
        print("详细分析EXIF数据:")
        print("-" * 30)
        exif_data = img.info['exif']
        
        # 尝试各种编码
        encodings = ['utf-8', 'utf-16', 'utf-16-be', 'utf-16-le', 'latin-1']
        for encoding in encodings:
            try:
                exif_str = exif_data.decode(encoding, errors='ignore')
                # 过滤非打印字符
                exif_str = ''.join(c for c in exif_str if c.isprintable() or c in '\n\t')
                if exif_str.strip():
                    print(f"使用 {encoding} 编码:")
                    print(f"{exif_str[:1000]}..." if len(exif_str) > 1000 else exif_str)
                    print()
                    
                    # 尝试提取prompt
                    prompt_match = re.search(r'prompt[:=]\s*(.+)', exif_str, re.IGNORECASE)
                    if prompt_match:
                        print(f"找到Prompt: {prompt_match.group(1).strip()[:200]}...")
                    
                    # 尝试提取negative prompt
                    negative_match = re.search(r'negative[:=]\s*(.+)', exif_str, re.IGNORECASE)
                    if negative_match:
                        print(f"找到Negative Prompt: {negative_match.group(1).strip()[:200]}...")
                    print()
            except:
                pass
    
    print("=" * 50)
    print("解析完成!")
