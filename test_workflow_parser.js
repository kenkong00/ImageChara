// 模拟测试ComfyUI Workflow JSON解析（对应k_00055_.png的实际数据）

// 这是实际的workflow数据片段（从图片中提取）
const testWorkflowJSON = {
  "80": {
    "inputs": {
      "clip_name": "qwen_3_4b.safetensors",
      "type": "lumina2",
      "device": "default"
    },
    "class_type": "CLIPLoader",
    "_meta": {"title": "加载CLIP"}
  },
  "82": {
    "inputs": {
      "samples": ["138", 0],
      "vae": ["86", 0]
    },
    "class_type": "VAEDecode",
    "_meta": {"title": "VAE解码"}
  },
  "106": {
    "inputs": {
      "text": "照片呈现出胶片质感，将逼真的纹理和完美的肌肤细节与电影般的暗黑、忧郁和高对比度戏剧效果完美融合。\n\n韩国女性朴智妍，女，25岁，花艺师，心形脸，眼角微微上扬，瞳孔为深黑色，唇色自然粉嫩，发色是冷棕色，锁骨发带有自然弧度的卷度，皮肤通透白皙。身穿奶白色灯芯绒圆领上衣，外搭淡粉色短款羊羔毛外套，下身搭配米白色棉质百褶长裙",
      "clip": ["80", 0]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {"title": "CLIP文本编码"}
  },
  "130": {
    "inputs": {
      "seed": 302337477908913,
      "steps": 6,
      "cfg": 1,
      "sampler_name": "lcm",
      "scheduler": "normal",
      "denoise": 1,
      "model": ["129", 0],
      "positive": ["106", 0],
      "negative": ["107", 0],
      "latent_image": ["131", 0]
    },
    "class_type": "KSampler",
    "_meta": {"title": "K采样器"}
  },
  "129": {
    "inputs": {
      "ckpt_name": "redcraftMar0826LatestZib_fp8_zibDistilled.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {"title": "加载检查点"}
  }
};

// 解析函数（从前端代码复制）
function parseComfyUIWorkflow(workflowData) {
  let promptParts = [];
  let negativeParts = [];
  let seed = '';
  let steps = '';
  let cfg = '';
  let samplerName = '';
  let model = '';
  
  for (const nodeId in workflowData) {
    const node = workflowData[nodeId];
    const classType = node.class_type;
    const inputs = node.inputs || {};
    const meta = node._meta || {};
    const title = (meta.title || '').toLowerCase();
    
    if (classType === 'Text Multiline') {
      let text = inputs.text || '';
      if (Array.isArray(text)) text = text.join(' ');
      if (text) promptParts.push(text);
    }
    
    else if (classType === 'CLIPTextEncode') {
      let text = inputs.text || '';
      if (Array.isArray(text)) text = text.join(' ');
      if (text) {
        if (title.includes('negative')) {
          negativeParts.push(text);
        } else {
          promptParts.push(text);
        }
      }
    }
    
    else if (classType === 'CLIPTextEncodeSDXL' || classType === 'CLIPTextEncodeSDXLRefiner') {
      let textG = inputs.text_g || '';
      let textL = inputs.text_l || '';
      
      if (Array.isArray(textG)) textG = textG.join(' ');
      if (Array.isArray(textL)) textL = textL.join(' ');
      
      if (textG) promptParts.push(textG);
      if (textL) promptParts.push(textL);
    }
    
    else if (classType === 'KSampler' || classType === 'KSamplerAdvanced') {
      seed = String(inputs.seed || inputs.noise_seed || '');
      steps = String(inputs.steps || '');
      cfg = String(inputs.cfg || '');
      samplerName = String(inputs.sampler_name || '');
    }
    
    else if (classType === 'UNETLoader' || classType === 'CheckpointLoaderSimple') {
      let modelName = inputs.unet_name || inputs.ckpt_name || '';
      if (modelName) {
        if (Array.isArray(modelName)) modelName = modelName.toString();
        model = modelName.split('\\').pop().split('/').pop();
      }
    }
  }
  
  const prompt = promptParts.join('\n').trim();
  const negativePrompt = negativeParts.join('\n').trim();
  
  return {
    prompt,
    negative_prompt: negativePrompt,
    seed,
    steps,
    cfg,
    sampler_name: samplerName,
    model,
    workflow: JSON.stringify(workflowData, null, 2)
  };
}

// 执行测试
console.log('='.repeat(60));
console.log('测试 ComfyUI Workflow JSON 解析（中文Prompt）');
console.log('='.repeat(60));

const result = parseComfyUIWorkflow(testWorkflowJSON);

console.log('\n✓ 解析结果:');
console.log('-'.repeat(40));
console.log(`Prompt长度: ${result.prompt.length} 字符`);
console.log(`\n📝 Prompt内容:`);
console.log(result.prompt.substring(0, 300) + (result.prompt.length > 300 ? '...' : ''));

console.log(`\n📊 参数:`);
console.log(`  Seed: ${result.seed}`);
console.log(`  Steps: ${result.steps}`);
console.log(`  CFG: ${result.cfg}`);
console.log(`  Sampler: ${result.sampler_name}`);
console.log(`  Model: ${result.model}`);

// 检查中文支持
const chineseChars = result.prompt.match(/[\u4e00-\u9fff]/g);
if (chineseChars) {
  console.log(`\n✅ 成功提取中文字符: ${chineseChars.length} 个`);
} else {
  console.log('\n❌ 未检测到中文字符');
}

console.log('\n' + '='.repeat(60));
