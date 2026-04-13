from PIL import Image
from parsers import MetadataParser

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\Event Horizon XL v3.0\Image00106.png'

print(f"测试PNG图片解析: {img_path}")
print("=" * 60)

# 创建解析器实例
parser = MetadataParser()

# 打开图片并解析
with Image.open(img_path) as img:
    print("图片元数据字段:", list(img.info.keys()))
    print()
    
    metadata = parser.parse(img)
    
    print("解析结果:")
    print("-" * 40)
    print(f"Prompt: {metadata['prompt'][:200]}..." if len(metadata['prompt']) > 200 else f"Prompt: {metadata['prompt']}")
    print(f"Negative Prompt: {metadata['negative_prompt'][:100]}..." if len(metadata['negative_prompt']) > 100 else f"Negative Prompt: {metadata['negative_prompt']}")
    print(f"Seed: {metadata['seed']}")
    print(f"Steps: {metadata['steps']}")
    print(f"CFG: {metadata['cfg']}")
    print(f"Sampler: {metadata['sampler_name']}")
    print(f"Model: {metadata['model']}")
    print()
    
    if metadata.get('workflow'):
        workflow_preview = metadata['workflow'][:300] if len(metadata['workflow']) > 300 else metadata['workflow']
        print(f"Workflow: {workflow_preview}...")

print("\n" + "=" * 60)

# 检查是否成功提取了prompt
if metadata['prompt'] and len(metadata['prompt']) > 10:
    print("✓ 成功识别元数据!")
else:
    print("✗ 未能正确识别元数据")
    print("\n可能的原因:")
    print("1. exif_b64解码失败")
    print("2. UNICODE格式解析错误")
    print("3. 编码检测失败")
