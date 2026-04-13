from PIL import Image
import base64
import json

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\test\[booru.plus]+pygmalion2011 - 副本 (2).png'

print(f"分析角色数据图片: {img_path}")
print("=" * 60)

with Image.open(img_path) as img:
    print(f"格式: {img.format} | 尺寸: {img.size} | 模式: {img.mode}")
    print(f"\n元数据字段: {list(img.info.keys())}")
    
    for key, value in img.info.items():
        print(f"\n{'='*50}")
        print(f"字段: [{key}]")
        
        if isinstance(value, str):
            # 检查是否是base64编码
            if len(value) > 100 and key in ['chara', 'character']:
                try:
                    decoded = base64.b64decode(value)
                    chara_json = json.loads(decoded.decode('utf-8'))
                    print(f"\n✓ 发现角色数据 (Base64解码成功)")
                    print(f"\n📋 角色信息:")
                    print(json.dumps(chara_json, indent=2, ensure_ascii=False)[:1500])
                except Exception as e:
                    print(f"Base64解码失败: {e}")
                    print(f"\n原始值前200字符: {value[:200]}")
            else:
                print(f"\n值: {value[:500]}..." if len(value) > 500 else f"\n值: {value}")

print("\n" + "=" * 60)

# 测试当前解析器
from parsers import MetadataParser
parser = MetadataParser()

with Image.open(img_path) as img:
    metadata = parser.parse(img)
    
    print("\n解析器结果:")
    print("-"*40)
    
    if metadata.get('chara_raw'):
        print("✓ 角色数据已识别!")
        chara = metadata['chara_raw']
        print(f"\n角色字段: {list(chara.keys())}")
        
        for k, v in chara.items():
            if k != 'data' and v:
                val_str = str(v)[:100] + '...' if len(str(v)) > 100 else str(v)
                print(f"  {k}: {val_str}")
        
        if 'data' in chara and isinstance(chara['data'], dict):
            data = chara['data']
            if data:
                print(f"\n  [data] 子字段:")
                for dk, dv in data.items():
                    if dv:
                        dv_str = str(dv)[:80] + '...' if len(str(dv)) > 80 else str(dv)
                        print(f"    {dk}: {dv_str}")
    else:
        print("✗ 未识别到角色数据")
        print(f"可用键: {list(metadata.keys())}")
