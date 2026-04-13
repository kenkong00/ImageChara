from PIL import Image
import base64
import re

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\Event Horizon XL v3.0\Image00106.png'

print(f"深度分析PNG元数据: {img_path}")
print("=" * 60)

with Image.open(img_path) as img:
    # 获取exif_b64字段
    if 'exif_b64' in img.info:
        exif_b64_str = img.info['exif_b64']
        print(f"找到 exif_b64 字段 (长度: {len(exif_b64_str)})")
        print()
        
        # 解码base64
        try:
            exif_data = base64.b64decode(exif_b64_str)
            print(f"Base64解码成功! 二进制长度: {len(exif_data)} bytes")
            print()
            
            # 尝试多种编码
            encodings = ['utf-8', 'utf-16-le', 'utf-16-be', 'utf-16', 'latin-1']
            
            for encoding in encodings:
                try:
                    decoded = exif_data.decode(encoding, errors='ignore')
                    # 过滤非打印字符
                    filtered = ''.join(c for c in decoded if c.isprintable() or c in '\n\t')
                    
                    if len(filtered.strip()) > 10 and any(c.isalpha() for c in filtered[:20]):
                        print(f"\n{'='*60}")
                        print(f"✓ 使用 {encoding} 编码成功!")
                        print(f"{'='*60}")
                        print(f"\n完整内容:")
                        print("-"*40)
                        print(filtered[:1500] if len(filtered) > 1500 else filtered)
                        print()
                        
                        # 提取prompt
                        if 'UNICODE' in filtered:
                            unicode_index = filtered.index('UNICODE')
                            after_unicode = filtered[unicode_index + 7:]
                            print(f"\n★ UNICODE之后的内容:")
                            print(after_unicode[:500])
                        
                        # 查找Steps:来定位参数部分
                        if 'Steps:' in filtered:
                            steps_idx = filtered.index('Steps:')
                            # 往前找prompt部分
                            before_steps = filtered[:steps_idx]
                            lines_before = [l.strip() for l in before_steps.split('\n') if l.strip()]
                            
                            # 找到第一个非空行作为prompt开始
                            prompt_lines = []
                            for line in lines_before:
                                if line.startswith('UNICODE'):
                                    continue
                                prompt_lines.append(line)
                            
                            prompt_text = '\n'.join(prompt_lines).strip()
                            print(f"\n{'='*60}")
                            print(f"★ 提取到的Prompt:")
                            print(f"{'='*60}")
                            print(prompt_text[:800] if len(prompt_text) > 800 else prompt_text)
                        
                        break
                except Exception as e:
                    print(f"{encoding} 失败: {e}")
                    continue
        
        except Exception as e:
            print(f"Base64解码失败: {e}")
    
    # 也检查chara字段
    if 'chara' in img.info:
        chara_data = img.info['chara']
        print(f"\n\n{'='*60}")
        print(f"Chara 字段:")
        print(f"{'='*60}")
        try:
            decoded_chara = base64.b64decode(chara_data)
            chara_json = json.loads(decoded_chara.decode('utf-8'))
            import json as j
            print(j.dumps(chara_json, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"解析chara失败: {e}")

print("\n" + "=" * 60)
print("分析完成!")
