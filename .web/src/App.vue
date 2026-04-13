<template>
  <div class="app">
    <header class="app-header">
      <h1>图灵注 ImageChara</h1>
      <p>AI角色信息注入与图片元数据工具</p>
    </header>
    
    <main class="app-main">
      <div class="file-list-panel">
        <h2>文件列表</h2>
        <div class="file-actions">
          <button @click="uploadFiles" class="btn">选择文件</button>
          <button @click="clearFiles" class="btn">清空</button>
        </div>
        <ul class="file-list">
          <li v-for="(file, index) in files" :key="index" @click="loadImage(file)" :class="['file-item', { 'file-item-active': index === selectedIndex }]">
            <span class="file-name">{{ file.name }}</span>
            <button @click.stop="removeFile(index)" class="btn btn-danger">删除</button>
          </li>
        </ul>
      </div>
      
      <div class="preview-panel">
        <h2>图片预览</h2>
        <div class="preview-container" @drop="onDrop" @dragover.prevent>
          <img v-if="currentImage" :src="currentImage" alt="Preview" class="preview-image" />
          <div v-else class="drop-placeholder">
            <p>拖拽图片到此处</p>
            <p>或点击选择文件</p>
          </div>
        </div>
      </div>
      
      <div class="metadata-panel">
        <h2>元数据</h2>
        
        <!-- Tab导航 -->
        <div class="tab-navigation" v-if="metadata && !loading">
          <button 
            v-for="(tab, index) in tabs" 
            :key="index"
            :class="['tab-btn', { 'tab-active': activeTab === index }]"
            @click="activeTab = index"
            :disabled="tab.disabled"
          >
            {{ tab.icon }} {{ tab.label }}
            <span v-if="tab.badge" class="badge">{{ tab.badge }}</span>
          </button>
        </div>
        
        <div v-if="loading" class="metadata-loading">
          <p>正在解析元数据...</p>
        </div>
        
        <!-- Tab 0: 提示词 -->
        <div v-else-if="metadata && activeTab === 0" class="metadata-content tab-content">
          <div class="section">
            <h3>✨ 提示词</h3>
            <pre class="prompt-text">{{ metadata.prompt || '无提示词数据' }}</pre>
            <button v-if="metadata.prompt" @click="copyPrompt" class="copy-btn" :class="{ 'copy-success': copySuccess }">
              {{ copySuccess ? '已复制 ✓' : '复制' }}
            </button>
          </div>
          
          <div class="section" v-if="metadata.negative_prompt">
            <h3>🚫 反向提示词</h3>
            <pre class="negative-prompt-text">{{ metadata.negative_prompt }}</pre>
          </div>
        </div>
        
        <!-- Tab 1: 参数 -->
        <div v-else-if="metadata && activeTab === 1" class="metadata-content tab-content">
          <div class="params-grid">
            <div class="param-card" v-if="metadata.seed">
              <span class="param-label">Seed</span>
              <span class="param-value">{{ metadata.seed }}</span>
            </div>
            <div class="param-card" v-if="metadata.steps">
              <span class="param-label">Steps</span>
              <span class="param-value">{{ metadata.steps }}</span>
            </div>
            <div class="param-card" v-if="metadata.cfg">
              <span class="param-label">CFG</span>
              <span class="param-value">{{ metadata.cfg }}</span>
            </div>
            <div class="param-card" v-if="metadata.sampler_name">
              <span class="param-label">Sampler</span>
              <span class="param-value">{{ metadata.sampler_name }}</span>
            </div>
            <div class="param-card" v-if="metadata.model">
              <span class="param-label">Model</span>
              <span class="param-value model-name">{{ metadata.model }}</span>
            </div>
          </div>
          
          <div class="section" v-if="metadata.workflow">
            <h3>🔧 Workflow</h3>
            <pre class="workflow-text">{{ metadata.workflow.substring(0, 1000) }}{{ metadata.workflow.length > 1000 ? '\n... (截断)' : '' }}</pre>
          </div>
        </div>
        
        <!-- Tab 2: 角色信息 -->
        <div v-else-if="metadata && activeTab === 2" class="metadata-content tab-content character-tab">
          <div v-if="editingChara" class="chara-edit-form">
            <h3>📝 编辑角色信息</h3>
            <div class="chara-edit-field">
              <label>名称</label>
              <input type="text" class="chara-edit-input" :value="editCharaData?.name" @input="updateCharaField('name', $event.target.value)" placeholder="输入角色名称" />
            </div>
            <div class="chara-edit-field">
              <label>描述</label>
              <textarea class="chara-edit-textarea" :value="editCharaData?.description" @input="updateCharaField('description', $event.target.value)" placeholder="输入角色描述" rows="4"></textarea>
            </div>
            <div class="section" v-if="editCharaData">
              <h4>🏷️ 自定义属性</h4>
              <div class="attr-row" v-for="(value, key) in getCharacterAttributes(editCharaData)" :key="key">
                <span class="attr-key">{{ key }}</span>
                <input type="text" class="attr-edit-input" :value="value" @input="updateCharaField(key, $event.target.value)" />
                <button @click="removeCharaAttribute(key)" class="btn btn-danger attr-remove-btn">删除</button>
              </div>
              <div class="attr-row attr-add-row">
                <input type="text" class="attr-edit-input" v-model="newAttrKey" placeholder="键名" />
                <input type="text" class="attr-edit-input" v-model="newAttrValue" placeholder="值" />
                <button @click="addCharaAttribute" class="btn attr-add-btn">+ 添加</button>
              </div>
            </div>
            <div class="save-status" :class="saveStatus" v-if="saveStatus">
              <span v-if="saveStatus === 'saving'">⏳ 正在保存...</span>
              <span v-else-if="saveStatus === 'success'">✅ 已保存</span>
              <span v-else-if="saveStatus === 'error'">❌ 保存失败，请重试</span>
            </div>
            <div class="chara-edit-actions">
              <button @click="cancelEditChara" class="btn cancel-btn">取消</button>
              <button @click="saveCharaDirect" class="btn save-btn save-direct-btn" :disabled="saveStatus === 'saving'">
                {{ saveStatus === 'saving' ? '保存中...' : '💾 直接保存' }}
              </button>
              <button @click="saveCharaAs" class="btn save-btn save-as-btn" :disabled="saveStatus === 'saving'">
                {{ saveStatus === 'saving' ? '保存中...' : '📋 另存为' }}
              </button>
            </div>
          </div>

          <div v-else-if="metadata.chara_raw" class="character-info">
            <div class="character-header" v-if="metadata.chara_raw.name">
              <h3 class="character-name">🎭 {{ metadata.chara_raw.name }}</h3>
            </div>
            <div class="section" v-if="metadata.chara_raw.description">
              <h4>📖 描述</h4>
              <div class="character-description">{{ formatDescription(metadata.chara_raw.description) }}</div>
            </div>
            <div class="character-attributes">
              <div class="attr-item" v-for="(value, key) in getCharacterAttributes(metadata.chara_raw)" :key="key">
                <span class="attr-key">{{ formatAttributeName(key) }}</span>
                <span class="attr-value">{{ value }}</span>
              </div>
            </div>
            <div class="section" v-if="metadata.chara_raw.data && hasDataContent(metadata.chara_raw.data)">
              <h4>📂 扩展数据</h4>
              <div class="data-fields">
                <div class="data-item" v-for="(value, key) in getDataFields(metadata.chara_raw.data)" :key="key">
                  <span class="data-key">{{ key }}</span>
                  <span class="data-value">{{ Array.isArray(value) ? value.length + ' 项' : value }}</span>
                </div>
              </div>
            </div>
            <div class="section raw-json-section">
              <button @click="showRawJson = !showRawJson" class="toggle-btn">
                {{ showRawJson ? '▼' : '▶' }} 查看原始JSON
              </button>
              <pre v-if="showRawJson" class="raw-json">{{ JSON.stringify(metadata.chara_raw, null, 2) }}</pre>
            </div>
            <div class="chara-edit-actions chara-readonly-actions">
              <button @click="startEditChara" class="btn edit-btn">✏️ 编辑角色信息</button>
            </div>
          </div>

          <div v-else class="no-character">
            <p>📭 此图片不包含角色信息</p>
            <p class="hint">提示：使用本工具可以为图片注入AI角色数据</p>
            <button @click="startEditChara" class="btn edit-btn" style="margin-top:1rem;">➕ 添加角色信息</button>
          </div>
        </div>
        
        <div v-else class="metadata-placeholder">
          <p>选择图片查看元数据</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { parseImageMetadata } from './utils/metadataParser.js'
import { injectCharacterToPNG } from './utils/metadataWriter.js'

const files = ref([])
const fileHandles = ref([])
const currentImage = ref(null)
const metadata = ref(null)
const selectedIndex = ref(-1)
const loading = ref(false)
const activeTab = ref(0)
const showRawJson = ref(false)
const copySuccess = ref(false)
const editingChara = ref(false)
const editCharaData = ref(null)
const saveStatus = ref('')
const newAttrKey = ref('')
const newAttrValue = ref('')

// Tab配置
const tabs = computed(() => {
  const baseTabs = [
    { icon: '✨', label: '提示词', disabled: false },
    { icon: '⚙️', label: '参数', disabled: false },
    { icon: '🎭', label: '角色', disabled: !metadata.value?.chara_raw }
  ]
  
  // 如果有角色数据，显示badge
  if (metadata.value?.chara_raw?.name) {
    baseTabs[2].badge = '✓'
  }
  
  return baseTabs
})

const uploadFiles = async () => {
  if ('showOpenFilePicker' in window) {
    try {
      const handles = await window.showOpenFilePicker({
        multiple: true,
        types: [{ description: '图片文件', accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] } }]
      })
      for (const handle of handles) {
        const file = await handle.getFile()
        files.value.push(file)
        fileHandles.value.push(handle)
      }
      if (handles.length > 0) {
        loadImage(files.value[files.value.length - handles.length])
      }
      return
    } catch (e) {
      if (e.name === 'AbortError') return
    }
  }
  const input = document.createElement('input')
  input.type = 'file'
  input.multiple = true
  input.accept = 'image/*'
  input.onchange = (e) => {
    const selectedFiles = Array.from(e.target.files)
    selectedFiles.forEach(file => {
      files.value.push(file)
      fileHandles.value.push(null)
    })
    if (selectedFiles.length > 0) {
      loadImage(selectedFiles[0])
    }
  }
  input.click()
}

const clearFiles = () => {
  files.value = []
  fileHandles.value = []
  currentImage.value = null
  metadata.value = null
  selectedIndex.value = -1
  activeTab.value = 0
}

const removeFile = (index) => {
  files.value.splice(index, 1)
  fileHandles.value.splice(index, 1)
  if (selectedIndex.value === index) {
    if (files.value.length > 0) {
      const newIndex = Math.min(index, files.value.length - 1)
      loadImage(files.value[newIndex])
    } else {
      currentImage.value = null
      metadata.value = null
      selectedIndex.value = -1
    }
  } else if (selectedIndex.value > index) {
    selectedIndex.value--
  }
}

const loadImage = async (file) => {
  const index = files.value.findIndex(f => f.name === file.name && f.lastModified === file.lastModified)
  if (index !== -1) {
    selectedIndex.value = index
  }
  
  loading.value = true
  showRawJson.value = false
  
  try {
    const reader = new FileReader()
    reader.onload = async (e) => {
      currentImage.value = e.target.result
      // 解析真实的元数据
      metadata.value = await parseImageMetadata(file)
      
      // 如果有角色数据，自动切换到角色Tab
      if (metadata.value.chara_raw) {
        activeTab.value = 2
      } else {
        activeTab.value = 0
      }
      
      loading.value = false
    }
    reader.readAsDataURL(file)
  } catch (error) {
    console.error('加载图片失败:', error)
    loading.value = false
  }
}

const onDrop = (e) => {
  e.preventDefault()
  const droppedFiles = Array.from(e.dataTransfer.files)
  droppedFiles.forEach(file => {
    files.value.push(file)
    fileHandles.value.push(null)
  })
  if (droppedFiles.length > 0) {
    loadImage(droppedFiles[0])
  }
}

const copyPrompt = async () => {
  if (!metadata.value?.prompt) return
  try {
    await navigator.clipboard.writeText(metadata.value.prompt)
    copySuccess.value = true
    setTimeout(() => { copySuccess.value = false }, 2000)
  } catch (err) {
    console.error('复制失败:', err)
  }
}

const startEditChara = () => {
  if (metadata.value?.chara_raw) {
    editCharaData.value = JSON.parse(JSON.stringify(metadata.value.chara_raw))
  } else {
    editCharaData.value = { name: '', description: '' }
  }
  editingChara.value = true
  saveStatus.value = ''
  newAttrKey.value = ''
  newAttrValue.value = ''
}

const cancelEditChara = () => {
  editingChara.value = false
  editCharaData.value = null
  saveStatus.value = ''
}

const updateCharaField = (key, value) => {
  if (editCharaData.value) {
    editCharaData.value[key] = value
  }
}

const addCharaAttribute = () => {
  const key = newAttrKey.value.trim()
  const value = newAttrValue.value.trim()
  if (!key || !editCharaData.value) return
  editCharaData.value[key] = value
  newAttrKey.value = ''
  newAttrValue.value = ''
}

const removeCharaAttribute = (key) => {
  if (editCharaData.value && key in editCharaData.value) {
    delete editCharaData.value[key]
  }
}

const getModifiedPngBlob = async () => {
  const response = await fetch(currentImage.value)
  const arrayBuffer = await response.arrayBuffer()
  const uint8Array = new Uint8Array(arrayBuffer)
  const modifiedPng = injectCharacterToPNG(uint8Array, editCharaData.value)
  return new Blob([modifiedPng], { type: 'image/png' })
}

const saveCharaDirect = async () => {
  if (!editCharaData.value || !currentImage.value) return
  saveStatus.value = 'saving'
  try {
    const blob = await getModifiedPngBlob()
    const handle = fileHandles.value[selectedIndex.value]
    if (handle) {
      const writable = await handle.createWritable()
      await writable.write(blob)
      await writable.close()
    } else {
      const originalName = files.value[selectedIndex.value]?.name || 'image.png'
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = originalName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
    saveStatus.value = 'success'
    setTimeout(() => { saveStatus.value = '' }, 2000)
    editingChara.value = false
  } catch (err) {
    console.error('保存失败:', err)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = '' }, 3000)
  }
}

const saveCharaAs = async () => {
  if (!editCharaData.value || !currentImage.value) return
  saveStatus.value = 'saving'
  try {
    const blob = await getModifiedPngBlob()
    const originalName = files.value[selectedIndex.value]?.name || 'image'
    const baseName = originalName.replace(/\.[^.]+$/, '')
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${baseName}_chara.png`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    saveStatus.value = 'success'
    setTimeout(() => { saveStatus.value = '' }, 2000)
    editingChara.value = false
  } catch (err) {
    console.error('另存为失败:', err)
    saveStatus.value = 'error'
    setTimeout(() => { saveStatus.value = '' }, 3000)
  }
}

// 格式化描述文本（处理换行和特殊字符）
const formatDescription = (text) => {
  if (!text) return ''
  return text.replace(/\r\n/g, '<br>').replace(/\n/g, '<br>')
}

// 获取角色属性（排除description和data）
const getCharacterAttributes = (charaData) => {
  const attrs = {}
  for (const [key, value] of Object.entries(charaData)) {
    if (key !== 'description' && key !== 'data' && key !== 'name' && value) {
      attrs[key] = value
    }
  }
  return attrs
}

// 格式化属性名称（下划线转空格，首字母大写）
const formatAttributeName = (key) => {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
}

// 获取data字段内容
const getDataFields = (data) => {
  if (!data || typeof data !== 'object') return {}
  const fields = {}
  for (const [key, value] of Object.entries(data)) {
    if (value && !(Array.isArray(value) && value.length === 0)) {
      fields[key] = value
    }
  }
  return fields
}

// 检查data是否有有效内容
const hasDataContent = (data) => {
  if (!data) return false
  return Object.values(data).some(v => v && !(Array.isArray(v) && v.length === 0))
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #1e1e2e;
  color: #cdd6f4;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.app-header {
  text-align: center;
  padding: 2rem;
  background: #2a2a3e;
  border-bottom: 1px solid #45475a;
}

.app-header h1 {
  margin: 0;
  color: #89b4fa;
  font-size: 2rem;
}

.app-header p {
  margin: 0.5rem 0 0 0;
  color: #a6adc8;
}

.app-main {
  display: grid;
  grid-template-columns: 300px 1fr 450px;
  gap: 1rem;
  padding: 1rem;
  min-height: calc(100vh - 120px);
}

.file-list-panel,
.preview-panel,
.metadata-panel {
  background: #2a2a3e;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #45475a;
}

.file-list-panel h2,
.preview-panel h2,
.metadata-panel h2 {
  margin-top: 0;
  color: #89b4fa;
  border-bottom: 1px solid #45475a;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.file-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  background: #45475a;
  color: #cdd6f4;
  border: 1px solid #585b70;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn:hover {
  background: #585b70;
}

.btn-danger {
  background: #f38ba8;
  color: #1e1e2e;
  border: none;
  padding: 0.25rem 0.5rem;
  font-size: 0.8rem;
  width: 50px;
  flex-shrink: 0;
  text-align: center;
}

.btn-danger:hover {
  background: #f5a9c0;
}

.file-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  border-bottom: 1px solid #45475a;
  cursor: pointer;
  transition: background 0.2s;
  gap: 0.5rem;
}

.file-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.9rem;
  line-height: 1.4;
}

.file-item:hover {
  background: rgba(137, 180, 250, 0.1);
}

.file-item:active {
  background: rgba(137, 180, 250, 0.2);
}

.file-item-active {
  background: rgba(137, 180, 250, 0.15);
  border-left: 3px solid #89b4fa;
}

.preview-container {
  width: 100%;
  height: 400px;
  border: 2px dashed #45475a;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s;
}

.preview-container:hover {
  border-color: #89b4fa;
}

.preview-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.drop-placeholder {
  text-align: center;
  color: #6c7086;
}

/* Tab导航样式 */
.tab-navigation {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 2px solid #45475a;
  padding-bottom: 0.5rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  color: #a6adc8;
  border: none;
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  font-weight: 500;
}

.tab-btn:hover:not(:disabled) {
  background: rgba(137, 180, 250, 0.1);
  color: #89b4fa;
}

.tab-btn.tab-active {
  background: rgba(137, 180, 250, 0.15);
  color: #89b4fa;
  border-bottom: 2px solid #89b4fa;
  margin-bottom: -2px;
}

.tab-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.badge {
  background: #a6e3a1;
  color: #1e1e2e;
  padding: 0.1rem 0.4rem;
  border-radius: 10px;
  font-size: 0.75rem;
  margin-left: 0.3rem;
  font-weight: bold;
}

/* Tab内容 */
.metadata-content {
  max-height: calc(100vh - 280px);
  overflow-y: auto;
}

.tab-content {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.section {
  margin-bottom: 1.5rem;
}

.section h3 {
  color: #74c7ec;
  margin: 1rem 0 0.5rem 0;
  font-size: 1.1rem;
}

.section h4 {
  color: #89b4fa;
  margin: 0.8rem 0 0.5rem 0;
  font-size: 1rem;
}

.prompt-text {
  background: #181825;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
  font-family: 'Consolas', monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
  min-height: 80px;
  color: #a6e3a1;
  border-left: 3px solid #a6e3a1;
}

.copy-btn {
  margin-top: 0.5rem;
  padding: 0.4rem 1rem;
  background: #45475a;
  color: #cdd6f4;
  border: 1px solid #585b70;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: #585b70;
  border-color: #89b4fa;
}

.copy-btn.copy-success {
  background: #a6e3a1;
  color: #1e1e2e;
  border-color: #a6e3a1;
}

.negative-prompt-text {
  background: #181825;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
  font-family: 'Consolas', monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
  min-height: 60px;
  color: #f38ba8;
  border-left: 3px solid #f38ba8;
}

/* 参数网格 */
.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.param-card {
  background: #181825;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #45475a;
  transition: all 0.2s;
}

.param-card:hover {
  border-color: #89b4fa;
  transform: translateY(-2px);
}

.param-label {
  display: block;
  color: #6c7086;
  font-size: 0.85rem;
  margin-bottom: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.param-value {
  display: block;
  color: #cdd6f4;
  font-size: 1.1rem;
  font-weight: 600;
  word-break: break-all;
}

.model-name {
  color: #f9e2af;
  font-size: 0.95rem;
}

.workflow-text {
  background: #181825;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
  font-family: 'Consolas', monospace;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.4;
  max-height: 300px;
  color: #a6adc8;
}

/* 角色信息样式 */
.character-tab {
  padding: 0.5rem;
}

.character-info {
  animation: slideIn 0.4s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-20px); }
  to { opacity: 1; transform: translateX(0); }
}

.character-header {
  text-align: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(137, 180, 250, 0.1), rgba(243, 139, 168, 0.1));
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid rgba(137, 180, 250, 0.3);
}

.character-name {
  color: #89b4fa;
  font-size: 1.8rem;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.character-description {
  background: #181825;
  padding: 1rem;
  border-radius: 6px;
  line-height: 1.7;
  color: #cdd6f4;
  border-left: 3px solid #cba6f7;
  font-size: 0.95rem;
  max-height: 300px;
  overflow-y: auto;
}

.character-attributes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.8rem;
  margin: 1rem 0;
}

.attr-item {
  background: #181825;
  padding: 0.8rem;
  border-radius: 6px;
  border: 1px solid #45475a;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.attr-key {
  color: #89b4fa;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.attr-value {
  color: #cdd6f4;
  font-size: 0.95rem;
  word-break: break-word;
}

.data-fields {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  max-height: 200px;
  overflow-y: auto;
  padding-right: 0.3rem;
}

.data-item {
  background: rgba(166, 227, 161, 0.08);
  padding: 0.5rem 0.6rem;
  border-radius: 4px;
  border: 1px solid rgba(166, 227, 161, 0.2);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  align-items: stretch;
}

.data-key {
  color: #a6e3a1;
  font-size: 0.8rem;
  font-weight: 600;
  flex-shrink: 0;
}

.data-value {
  color: #a6adc8;
  font-size: 0.8rem;
  line-height: 1.4;
  max-height: 80px;
  overflow-y: auto;
  word-break: break-all;
  white-space: pre-wrap;
}

.raw-json-section {
  margin-top: 1.5rem;
}

.toggle-btn {
  width: 100%;
  padding: 0.7rem;
  background: #45475a;
  color: #89b4fa;
  border: 1px solid #585b70;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 600;
}

.toggle-btn:hover {
  background: #585b70;
  border-color: #89b4fa;
}

.raw-json {
  background: #11111b;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin-top: 0.8rem;
  font-family: 'Consolas', monospace;
  font-size: 0.8rem;
  line-height: 1.5;
  max-height: 400px;
  overflow-y: auto;
  color: #a6adc8;
  border: 1px solid #45475a;
}

.no-character {
  text-align: center;
  padding: 3rem 2rem;
  color: #6c7086;
}

.no-character p:first-child {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.hint {
  font-size: 0.9rem;
  color: #585b70;
  font-style: italic;
}

.chara-edit-form {
  animation: slideIn 0.3s ease-out;
}

.chara-edit-form h3 {
  color: #cba6f7;
  margin-bottom: 1rem;
}

.chara-edit-field {
  margin-bottom: 1rem;
}

.chara-edit-field label {
  display: block;
  color: #89b4fa;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.chara-edit-input {
  width: 100%;
  padding: 0.6rem 0.8rem;
  background: #181825;
  color: #cdd6f4;
  border: 1px solid #45475a;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.chara-edit-input:focus {
  border-color: #89b4fa;
}

.chara-edit-textarea {
  width: 100%;
  padding: 0.6rem 0.8rem;
  background: #181825;
  color: #cdd6f4;
  border: 1px solid #45475a;
  border-radius: 6px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
  box-sizing: border-box;
}

.chara-edit-textarea:focus {
  border-color: #89b4fa;
}

.attr-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  background: #181825;
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  border: 1px solid #45475a;
}

.attr-row .attr-key {
  min-width: 80px;
  text-transform: none;
  letter-spacing: normal;
  white-space: nowrap;
}

.attr-edit-input {
  flex: 1;
  padding: 0.35rem 0.6rem;
  background: #11111b;
  color: #cdd6f4;
  border: 1px solid #585b70;
  border-radius: 4px;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s;
}

.attr-edit-input:focus {
  border-color: #89b4fa;
}

.attr-remove-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.attr-add-row {
  border-style: dashed;
  opacity: 0.7;
}

.attr-add-btn {
  padding: 0.35rem 0.7rem;
  font-size: 0.8rem;
  background: #45475a;
  color: #a6e3a1;
  border: 1px dashed #a6e3a1;
  flex-shrink: 0;
}

.attr-add-btn:hover {
  background: rgba(166, 227, 161, 0.15);
}

.save-status {
  text-align: center;
  padding: 0.6rem;
  border-radius: 6px;
  margin: 0.8rem 0;
  font-weight: 500;
  animation: fadeIn 0.3s ease-in;
}

.save-status.saving {
  background: rgba(137, 180, 250, 0.15);
  color: #89b4fa;
  border: 1px solid rgba(137, 180, 250, 0.3);
}

.save-status.success {
  background: rgba(166, 227, 161, 0.15);
  color: #a6e3a1;
  border: 1px solid rgba(166, 227, 161, 0.3);
}

.save-status.error {
  background: rgba(243, 139, 168, 0.15);
  color: #f38ba8;
  border: 1px solid rgba(243, 139, 168, 0.3);
}

.chara-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.8rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #45475a;
}

.chara-readonly-actions {
  justify-content: center;
  border-top: none;
  margin-top: 1rem;
  padding-top: 0;
}

.edit-btn {
  background: linear-gradient(135deg, #45475a, #585b70);
  color: #cba6f7;
  border: 1px solid #cba6f7;
  font-weight: 600;
  padding: 0.6rem 1.5rem;
  transition: all 0.2s;
}

.edit-btn:hover {
  background: rgba(203, 166, 247, 0.15);
  box-shadow: 0 0 12px rgba(203, 166, 247, 0.2);
}

.cancel-btn {
  background: transparent;
  color: #6c7068;
  border: 1px solid #585b70;
}

.cancel-btn:hover {
  background: rgba(108, 112, 134, 0.15);
  color: #a6adc8;
}

.save-btn {
  background: linear-gradient(135deg, #a6e3a1, #94e2d5);
  color: #1e1e2e;
  border: none;
  font-weight: 700;
  padding: 0.6rem 1.5rem;
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  box-shadow: 0 0 16px rgba(166, 227, 161, 0.4);
  transform: translateY(-1px);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-direct-btn {
  background: linear-gradient(135deg, #89b4fa, #74c7ec);
}

.save-direct-btn:hover:not(:disabled) {
  box-shadow: 0 0 16px rgba(137, 180, 250, 0.4);
}

.save-as-btn {
  background: linear-gradient(135deg, #a6e3a1, #94e2d5);
}

.save-as-btn:hover:not(:disabled) {
  box-shadow: 0 0 16px rgba(166, 227, 161, 0.4);
}

.metadata-loading {
  text-align: center;
  color: #89b4fa;
  padding: 2rem;
  font-style: italic;
}

.metadata-placeholder {
  text-align: center;
  color: #6c7086;
  padding: 2rem;
}

@media (max-width: 1400px) {
  .app-main {
    grid-template-columns: 250px 1fr 400px;
  }
}

@media (max-width: 1200px) {
  .app-main {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
  }
  
  .metadata-panel {
    max-width: 100%;
  }
}
</style>
