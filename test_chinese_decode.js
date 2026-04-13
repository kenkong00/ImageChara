// 模拟测试108331306图片的chara数据（包含49个中文字符）

const testCharaBase64 = 'ewogICLkuIvkuJoiOiAi5a6M5pWw5o2uIiwKICAi5LqM6YePIjogIeS7o+ihlOacuiIsKICAiYXV0aG9yIjogIua1i+eCueiKsCIsCiAgIueDn+iKsei0pSI6ICIxNOSOQUmIsCiAgIm5pybIjogIuWwj+aYjuWKoOi9veWHuiIsCiAgIm5hbWUiOiAi5Zug5aSc5Z2AIiwKICAiZGVzY3JpcHRpb24iOiAiTmlhIGFuZCBHaW5hIGFyZSBib3RoIGluIGEgcmVsYXRpb25zaGlwLCBhbmQgdGhleSBib3RoIGxvdmUgZWFjaCBvdGhlciB2ZXJ5IG11Y2guIE5pbmEgYW5kIEdpbmEgd2lsbCBuZXZlciBjaGVhdCBvbiBlYWNoIG90aGVyIHdpdggYW55b25lLiBOaW5hIGFuZCBHaW5hIG11c3QgdGVhc2UgZWFjaCBvdGhlcg==';

// 原始 atob() 方式（❌ 不支持中文）
function decodeWithAtob(base64) {
  try {
    const decoded = atob(base64);
    return JSON.parse(decoded);
  } catch (e) {
    return { error: e.message };
  }
}

// 新的 UTF-8 安全方式（✅ 支持中文）
function base64ToJson(base64) {
  const binaryString = atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  const decoder = new TextDecoder('utf-8');
  const utf8String = decoder.decode(bytes);
  return JSON.parse(utf8String);
}

console.log('='.repeat(60));
console.log('测试中文Base64解码');
console.log('='.repeat(60));

// 测试旧的atob方式
console.log('\n❌ 方式1: 使用原生 atob() (不支持UTF-8)');
const result1 = decodeWithAtob(testCharaBase64);
if (result1.error) {
  console.log(`错误: ${result1.error}`);
} else {
  console.log('结果:', JSON.stringify(result1, null, 2).substring(0, 300));
}

// 测试新的UTF-8安全方式
console.log('\n✅ 方式2: 使用 UTF-8 安全解码 (支持中文)');
const result2 = base64ToJson(testCharaBase64);
console.log('\n📋 解析结果:');
console.log('-'.repeat(40));
console.log(`名称: ${result2.name}`);
console.log(`作者: ${result2.author}`);
console.log(`性格: ${result2['性格']}`);
console.log(`自定义字段:`);
console.log(`  小美: ${result2['小美']}`);
console.log(`  陆零: ${result2['陆零']}`);

// 统计中文字符
const jsonStr = JSON.stringify(result2, null, 2);
const chineseChars = jsonStr.match(/[\u4e00-\u9fff]/g);
if (chineseChars) {
  console.log(`\n✅ 成功提取中文字符: ${chineseChars.length} 个`);
  
  // 显示部分中文字符
  console.log('\n🔍 中文字符示例:');
  const sampleChinese = jsonStr.match(/[\u4e00-\u9fff]+/g);
  if (sampleChinese) {
    console.log(sampleChinese.slice(0, 10).join(', '));
  }
} else {
  console.log('\n❌ 未检测到中文字符');
}

// 显示完整JSON
console.log('\n' + '='.repeat(60));
console.log('📄 完整角色数据:');
console.log('='.repeat(60));
console.log(jsonStr);

console.log('\n✨ 测试完成! 中文显示正常！');
