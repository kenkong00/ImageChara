from PIL import Image
from parsers import MetadataParser

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\Juggernaut XL Ragnarok_by_RunDiffusion\00020-13691895.webp'

print(f"测试解析器: {img_path}")
print("=" * 50)

# 创建解析器实例
parser = MetadataParser()

# 打开图片并解析
with Image.open(img_path) as img:
    metadata = parser.parse(img)
    
    print("解析结果:")
    print("-" * 30)
    print(f"Prompt: {metadata['prompt']}")
    print(f"Negative Prompt: {metadata['negative_prompt']}")
    print(f"Seed: {metadata['seed']}")
    print(f"Steps: {metadata['steps']}")
    print(f"CFG: {metadata['cfg']}")
    print(f"Sampler: {metadata['sampler_name']}")
    print(f"Model: {metadata['model']}")
    print()
    print(f"Workflow: {metadata['workflow'][:200]}..." if len(metadata['workflow']) > 200 else f"Workflow: {metadata['workflow']}")

print("=" * 50)
print("测试完成!")
