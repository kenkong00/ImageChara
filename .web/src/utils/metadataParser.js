export const parseImageMetadata = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    
    reader.onload = function(event) {
      const arrayBuffer = event.target.result;
      
      try {
        // 尝试从图片中提取真实的元数据
        const metadata = extractRealMetadata(arrayBuffer, file.name);
        resolve(metadata);
      } catch (error) {
        console.error('Error parsing metadata:', error);
        // 解析失败时返回默认值
        resolve({
          prompt: '',
          negative_prompt: '',
          seed: '',
          steps: '',
          cfg: '',
          sampler_name: '',
          model: '',
          workflow: 'Error parsing metadata',
          chara_raw: null
        });
      }
    };
    
    reader.onerror = function() {
      resolve({
        prompt: '',
        negative_prompt: '',
        seed: '',
        steps: '',
        cfg: '',
        sampler_name: '',
        model: '',
        workflow: 'Error reading file',
        chara_raw: null
      });
    };
    
    reader.readAsArrayBuffer(file);
  });
}

function extractRealMetadata(arrayBuffer, filename) {
  const uint8Array = new Uint8Array(arrayBuffer);
  
  // 初始化结果对象（包含chara_raw字段）
  let result = {
    prompt: '',
    negative_prompt: '',
    seed: '',
    steps: '',
    cfg: '',
    sampler_name: '',
    model: '',
    workflow: '',
    chara_raw: null
  };
  
  // 检查是否是WebP格式
  if (uint8Array[0] === 0x52 && uint8Array[1] === 0x49 && 
      uint8Array[2] === 0x46 && uint8Array[3] === 0x46) {
    Object.assign(result, parseWebPMetadata(uint8Array));
  }
  
  // 检查是否是PNG格式
  else if (uint8Array[0] === 0x89 && uint8Array[1] === 0x50 && 
           uint8Array[2] === 0x4E && uint8Array[3] === 0x47) {
    Object.assign(result, parsePNGMetadata(uint8Array));
  }
  
  // 检查是否是JPEG格式
  else if (uint8Array[0] === 0xFF && uint8Array[1] === 0xD8) {
    Object.assign(result, parseJPEGMetadata(uint8Array));
  }
  
  // 尝试提取角色数据（适用于所有格式）
  result.chara_raw = extractCharacterData(uint8Array);
  
  return result;
}

function parseWebPMetadata(uint8Array) {
  let exifData = null;
  
  // WebP格式：查找EXIF chunk
  for (let i = 12; i < uint8Array.length - 4; i++) {
    // 查找 "EXIF" 标记
    if (uint8Array[i] === 0x45 && uint8Array[i+1] === 0x58 &&
        uint8Array[i+2] === 0x49 && uint8Array[i+3] === 0x46) {
      const chunkSize = (uint8Array[i+7] << 24) | (uint8Array[i+6] << 16) | 
                        (uint8Array[i+5] << 8) | uint8Array[i+4];
      exifData = uint8Array.slice(i + 8, i + 8 + chunkSize);
      break;
    }
  }
  
  if (!exifData) {
    return {
      prompt: '',
      negative_prompt: '',
      seed: '',
      steps: '',
      cfg: '',
      sampler_name: '',
      model: '',
      workflow: 'No EXIF data found in WebP'
    };
  }
  
  return parseEXIFData(exifData);
}

function parsePNGMetadata(uint8Array) {
  let textChunks = [];
  let exifB64Data = null;
  let i = 8; // 跳过PNG签名
  
  while (i < uint8Array.length) {
    const length = (uint8Array[i] << 24) | (uint8Array[i+1] << 16) | 
                   (uint8Array[i+2] << 8) | uint8Array[i+3];
    
    if (i + 12 + length > uint8Array.length) break;
    
    const type = String.fromCharCode(...uint8Array.slice(i+4, i+8));
    
    if (type === 'tEXt' || type === 'iTXt' || type === 'zTXt') {
      const data = uint8Array.slice(i + 8, i + 8 + length);
      textChunks.push({ type, data });
      
      // 检查是否是exif_b64字段
      const text = decodeTextChunk(data);
      const nullIndex = text.indexOf('\0');
      if (nullIndex > 0) {
        const keyword = text.substring(0, nullIndex).toLowerCase();
        const value = text.substring(nullIndex + 1);
        
        if (keyword === 'exif_b64') {
          exifB64Data = value;
        }
      }
    }
    
    if (type === 'IEND') break;
    i += 12 + length; // 4(length) + 4(type) + length + 4(CRC)
  }
  
  // 优先处理exif_b64字段（base64编码的EXIF数据）
  if (exifB64Data) {
    try {
      // 解码base64
      const binaryString = atob(exifB64Data);
      const bytes = new Uint8Array(binaryString.length);
      for (let j = 0; j < binaryString.length; j++) {
        bytes[j] = binaryString.charCodeAt(j);
      }
      
      // 解析EXIF数据
      return parseEXIFData(bytes);
    } catch (error) {
      console.error('Error decoding exif_b64:', error);
    }
  }
  
  // 查找parameters或prompt字段
  for (const chunk of textChunks) {
    const text = decodeTextChunk(chunk.data);
    if (chunk.type === 'tEXt' || chunk.type === 'iTXt') {
      const nullIndex = text.indexOf('\0');
      if (nullIndex > 0) {
        const keyword = text.substring(0, nullIndex).toLowerCase();
        const value = text.substring(nullIndex + 1);
        
        if (keyword === 'parameters') {
          return parseParametersText(value);
        }
        if (keyword === 'prompt') {
          // 检查是否是ComfyUI Workflow JSON格式
          try {
            const workflowData = JSON.parse(value);
            return parseComfyUIWorkflow(workflowData);
          } catch (e) {
            // 如果不是JSON，直接返回文本
            return { prompt: value, negative_prompt: '', seed: '', steps: '', cfg: '', sampler_name: '', model: '', workflow: value };
          }
        }
      }
    }
  }
  
  return {
    prompt: '',
    negative_prompt: '',
    seed: '',
    steps: '',
    cfg: '',
    sampler_name: '',
    model: '',
    workflow: 'No metadata found in PNG'
  };
}

function parseJPEGMetadata(uint8Array) {
  let exifOffset = -1;
  
  // 查找APP1标记（EXIF）
  for (let i = 0; i < uint8Array.length - 1; i++) {
    if (uint8Array[i] === 0xFF && uint8Array[i+1] === 0xE1) {
      const segmentLength = (uint8Array[i+2] << 8) | uint8Array[i+3];
      exifOffset = i + 4;
      break;
    }
  }
  
  if (exifOffset === -1) {
    return {
      prompt: '',
      negative_prompt: '',
      seed: '',
      steps: '',
      cfg: '',
      sampler_name: '',
      model: '',
      workflow: 'No EXIF data found in JPEG'
    };
  }
  
  // 跳过 "Exif\0\0" 头部
  const exifData = uint8Array.slice(exifOffset + 6);
  return parseEXIFData(exifData);
}

function parseEXIFData(exifData) {
  try {
    // 将字节数组转换为字符串
    let exifString = '';
    const encodings = ['utf-8', 'utf-16be', 'utf-16le', 'latin1'];
    
    for (const encoding of encodings) {
      try {
        const decoder = new TextDecoder(encoding);
        exifString = decoder.decode(exifData);
        
        // 过滤非打印字符
        exifString = exifString.replace(/[^\x20-\x7E\n\t]/g, '');
        
        if (exifString.length > 10 && /[a-zA-Z]/.test(exifString)) {
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!exifString || exifString.length < 5) {
      return {
        prompt: '',
        negative_prompt: '',
        seed: '',
        steps: '',
        cfg: '',
        sampler_name: '',
        model: '',
        workflow: 'Unable to decode EXIF data'
      };
    }
    
    // 检查是否有UNICODE标记
    const unicodeIndex = exifString.indexOf('UNICODE');
    if (unicodeIndex !== -1) {
      exifString = exifString.substring(unicodeIndex + 7);
    }
    
    // 解析参数文本格式
    return parseParametersText(exifString);
  } catch (error) {
    console.error('Error parsing EXIF:', error);
    return {
      prompt: '',
      negative_prompt: '',
      seed: '',
      steps: '',
      cfg: '',
      sampler_name: '',
      model: '',
      workflow: 'Error parsing EXIF: ' + error.message
    };
  }
}

function parseParametersText(text) {
  const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
  
  let promptLines = [];
  let negativePrompt = '';
  let seed = '';
  let steps = '';
  let cfg = '';
  let samplerName = '';
  let model = '';
  let currentSection = 'prompt';
  
  for (const line of lines) {
    if (line.startsWith('Negative prompt:')) {
      currentSection = 'negative';
      negativePrompt = line.substring('Negative prompt:'.length).trim();
    } else if (line.startsWith('Steps:')) {
      currentSection = 'params';
      const parts = line.split(',');
      for (const part of parts) {
        const trimmed = part.trim();
        if (trimmed.startsWith('Steps:')) steps = trimmed.substring('Steps:'.length).trim();
        else if (trimmed.startsWith('CFG scale:')) cfg = trimmed.substring('CFG scale:'.length).trim();
        else if (trimmed.startsWith('Sampler:')) samplerName = trimmed.substring('Sampler:'.length).trim();
        else if (trimmed.startsWith('Seed:')) seed = trimmed.substring('Seed:'.length).trim();
        else if (trimmed.startsWith('Model:')) model = trimmed.substring('Model:'.length).trim();
      }
    } else if (line.startsWith('Workflow:')) {
      currentSection = 'workflow';
    } else if (currentSection === 'prompt') {
      promptLines.push(line);
    }
  }
  
  const prompt = promptLines.join('\n').trim();
  const workflow = lines.join('\n');
  
  return {
    prompt,
    negative_prompt: negativePrompt,
    seed,
    steps,
    cfg,
    sampler_name: samplerName,
    model,
    workflow
  };
}

function decodeTextChunk(data) {
  try {
    // 尝试UTF-8解码
    const decoder = new TextDecoder('utf-8');
    return decoder.decode(data);
  } catch (e) {
    try {
      // 回退到Latin-1
      const decoder = new TextDecoder('latin-1');
      return decoder.decode(data);
    } catch (e2) {
      return '';
    }
  }
}

function parseComfyUIWorkflow(workflowData) {
  let promptParts = [];
  let negativeParts = [];
  let seed = '';
  let steps = '';
  let cfg = '';
  let samplerName = '';
  let model = '';
  
  // 遍历所有节点
  for (const nodeId in workflowData) {
    const node = workflowData[nodeId];
    const classType = node.class_type;
    const inputs = node.inputs || {};
    const meta = node._meta || {};
    const title = (meta.title || '').toLowerCase();
    
    // 提取文本节点
    if (classType === 'Text Multiline') {
      let text = inputs.text || '';
      if (Array.isArray(text)) text = text.join(' ');
      if (text) promptParts.push(text);
    }
    
    // 提取CLIP文本编码节点
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
    
    // 提取SDXL文本编码节点
    else if (classType === 'CLIPTextEncodeSDXL' || classType === 'CLIPTextEncodeSDXLRefiner') {
      let textG = inputs.text_g || '';
      let textL = inputs.text_l || '';
      
      if (Array.isArray(textG)) textG = textG.join(' ');
      if (Array.isArray(textL)) textL = textL.join(' ');
      
      if (textG) promptParts.push(textG);
      if (textL) promptParts.push(textL);
    }
    
    // 提取采样器参数
    else if (classType === 'KSampler' || classType === 'KSamplerAdvanced') {
      seed = String(inputs.seed || inputs.noise_seed || '');
      steps = String(inputs.steps || '');
      cfg = String(inputs.cfg || '');
      samplerName = String(inputs.sampler_name || '');
    }
    
    // 提取模型信息
    else if (classType === 'UNETLoader' || classType === 'CheckpointLoaderSimple') {
      let modelName = inputs.unet_name || inputs.ckpt_name || '';
      if (modelName) {
        if (Array.isArray(modelName)) modelName = modelName.toString();
        // 提取文件名（去掉路径）
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

function extractCharacterData(uint8Array) {
  // 检查是否是PNG格式
  if (uint8Array[0] === 0x89 && uint8Array[1] === 0x50 && 
      uint8Array[2] === 0x4E && uint8Array[3] === 0x47) {
    return extractCharacterFromPNG(uint8Array);
  }
  
  // 其他格式暂不支持角色数据提取
  return null;
}

function extractCharacterFromPNG(uint8Array) {
  let i = 8; // 跳过PNG签名
  
  while (i < uint8Array.length) {
    const length = (uint8Array[i] << 24) | (uint8Array[i+1] << 16) | 
                   (uint8Array[i+2] << 8) | uint8Array[i+3];
    
    if (i + 12 + length > uint8Array.length) break;
    
    const type = String.fromCharCode(...uint8Array.slice(i+4, i+8));
    
    if (type === 'tEXt' || type === 'iTXt') {
      const data = uint8Array.slice(i + 8, i + 8 + length);
      const text = decodeTextChunk(data);
      const nullIndex = text.indexOf('\0');
      
      if (nullIndex > 0) {
        const keyword = text.substring(0, nullIndex).toLowerCase();
        const value = text.substring(nullIndex + 1);
        
        // 查找chara字段（角色数据）
        if (keyword === 'chara') {
          try {
            // 使用UTF-8安全的Base64解码（支持中文）
            const charaData = base64ToJson(value);
            return charaData;
          } catch (error) {
            console.error('Error parsing character data:', error);
            return null;
          }
        }
      }
    }
    
    if (type === 'IEND') break;
    i += 12 + length;
  }
  
  return null;
}

/**
 * UTF-8安全的Base64解码函数
 * 解决JavaScript原生atob()不支持中文的问题
 * @param {string} base64String - Base64编码的字符串
 * @returns {Object} - 解码后的JSON对象
 */
function base64ToJson(base64String) {
  // 步骤1: 使用atob解码为二进制字符串（Latin1编码）
  const binaryString = atob(base64String);
  
  // 步骤2: 转换为字节数组
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  
  // 步骤3: 使用TextDecoder正确解码UTF-8
  const decoder = new TextDecoder('utf-8');
  const utf8String = decoder.decode(bytes);
  
  // 步骤4: 解析JSON
  return JSON.parse(utf8String);
}

/**
 * UTF-8安全的Base64解码（返回字符串）
 * 用于exif_b64等包含中文的二进制数据
 * @param {string} base64String - Base64编码的字符串  
 * @returns {Uint8Array} - 解码后的字节数组
 */
function base64ToBytes(base64String) {
  const binaryString = atob(base64String);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}