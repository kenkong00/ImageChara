from PIL import Image
import base64
import json

# 图片路径
img_path = r'g:\AI code\trae\comfyui出图查看器\.temp\test\108331306 - 副本.png'

print("提取真实Base64数据用于前端测试")
print("=" * 60)

with Image.open(img_path) as img:
    if 'chara' in img.info:
        chara_b64 = img.info['chara']
        print(f"✓ 获取到chara字段 (长度: {len(chara_b64)})")
        
        # 保存为JS文件
        js_content = f'''// 真实的chara Base64数据（来自108331306.png）
const testCharaBase64 = '{chara_b64}';

// 原始 atob() 方式（❌ 不支持中文）
function decodeWithAtob(base64) {{
  try {{
    const decoded = atob(base64);
    return JSON.parse(decoded);
  }} catch (e) {{
    return {{ error: e.message }};
  }}
}}

// 新的 UTF-8 安全方式（✅ 支持中文）
function base64ToJson(base64) {{
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {{
    bytes[i] = binaryString.charCodeAt(i);
  }}
  const decoder = new TextDecoder('utf-8');
  const utf8String = decoder.decode(bytes);
  return JSON.parse(utf8String);
}}

console.log('='.repeat(60));
console.log('测试真实中文Base64解码 (108331306.png)');
console.log('='.repeat(60));

// 测试旧的atob方式
console.log('\\n❌ 方式1: 使用原生 atob()');
const result1 = decodeWithAtob(testCharaBase64);
if (result1.error) {{
  console.log(`错误: ${{result1.error}}`);
}} else {{
  console.log('结果:', JSON.stringify(result1).substring(0, 200));
}}

// 测试新的UTF-8安全方式
console.log('\\n✅ 方式2: 使用 UTF-8 安全解码');
const result2 = base64ToJson(testCharaBase64);

console.log('\\n📋 角色信息:');
console.log('-'.repeat(40));
console.log(`名称: ${{result2.name}}`);
if (result2.author) console.log(`作者: ${{result2.author}}`);
if (result2['性格']) console.log(`性格: ${{result2['性格']}}`);

// 显示自定义中文字段
const chineseFields = Object.keys(result2).filter(key => 
  /[\\u4e00-\\u9fff]/.test(key)
);
if (chineseFields.length > 0) {{
  console.log(`\\n🇨🇳 自定义中文字段 (${{chineseFields.length}}个):`);
  for (const field of chineseFields) {{
    console.log(`  ${{field}}: ${{result2[field]}}`);
  }}
}}

// 统计中文字符
const jsonStr = JSON.stringify(result2, null, 2);
const chineseChars = jsonStr.match(/[\\u4e00-\\u9fff]/g);
if (chineseChars) {{
  console.log(`\\n✅ 成功提取中文字符: ${{chineseChars.length}} 个`);
}} else {{
  console.log('\\n❌ 未检测到中文');
}}

// 显示描述（通常包含详细中文）
if (result2.description) {{
  console.log('\\n📖 描述 (前300字符):');
  console.log(result2.description.substring(0, 300));
}}

console.log('\\n' + '='.repeat(60));
console.log('✨ 中文显示测试完成！');
'''
        
        with open('test_real_chara.js', 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print("✓ 已生成测试文件: test_real_chara.js")
        print("\n请运行: node test_real_chara.js")
