const CRC32_TABLE = new Uint32Array(256)
for (let i = 0; i < 256; i++) {
  let crc = i
  for (let j = 0; j < 8; j++) {
    crc = (crc & 1) ? (0xEDB88320 ^ (crc >>> 1)) : (crc >>> 1)
  }
  CRC32_TABLE[i] = crc
}

function crc32(data) {
  let crc = 0xFFFFFFFF
  for (let i = 0; i < data.length; i++) {
    crc = CRC32_TABLE[(crc ^ data[i]) & 0xFF] ^ (crc >>> 8)
  }
  return (crc ^ 0xFFFFFFFF) >>> 0
}

function jsonToBase64(obj) {
  const jsonStr = JSON.stringify(obj)
  const encoder = new TextEncoder()
  const bytes = encoder.encode(jsonStr)
  const binaryString = String.fromCharCode(...bytes)
  return btoa(binaryString)
}

function buildTextChunk(keyword, value) {
  const keywordBytes = new TextEncoder().encode(keyword)
  const valueBytes = new TextEncoder().encode(value)
  const data = new Uint8Array(keywordBytes.length + 1 + valueBytes.length)
  data.set(keywordBytes, 0)
  data[keywordBytes.length] = 0
  data.set(valueBytes, keywordBytes.length + 1)

  const length = new Uint8Array(4)
  length[0] = (data.length >> 24) & 0xFF
  length[1] = (data.length >> 16) & 0xFF
  length[2] = (data.length >> 8) & 0xFF
  length[3] = data.length & 0xFF

  const type = new TextEncoder().encode('tEXt')
  const crcData = new Uint8Array(4 + data.length)
  crcData.set(type, 0)
  crcData.set(data, 4)
  const crcValue = crc32(crcData)
  const crcBytes = new Uint8Array(4)
  crcBytes[0] = (crcValue >> 24) & 0xFF
  crcBytes[1] = (crcValue >> 16) & 0xFF
  crcBytes[2] = (crcValue >> 8) & 0xFF
  crcBytes[3] = crcValue & 0xFF

  const chunk = new Uint8Array(12 + data.length)
  chunk.set(length, 0)
  chunk.set(type, 4)
  chunk.set(data, 8)
  chunk.set(crcBytes, 8 + data.length)
  return chunk
}

export function injectCharacterToPNG(uint8Array, charaData) {
  if (!uint8Array || uint8Array.length < 8) throw new Error('Invalid PNG data')
  if (uint8Array[0] !== 0x89 || uint8Array[1] !== 0x50 ||
      uint8Array[2] !== 0x4E || uint8Array[3] !== 0x47) {
    throw new Error('Not a PNG file')
  }

  const base64Value = jsonToBase64(charaData)
  const newChunk = buildTextChunk('chara', base64Value)

  const chunks = []
  let i = 8
  let charaFound = false

  while (i < uint8Array.length) {
    if (i + 8 > uint8Array.length) break
    const chunkLen = (uint8Array[i] << 24) | (uint8Array[i+1] << 16) |
                      (uint8Array[i+2] << 8) | uint8Array[i+3]
    const type = String.fromCharCode(uint8Array[i+4], uint8Array[i+5], uint8Array[i+6], uint8Array[i+7])
    const totalSize = 12 + chunkLen

    if (i + totalSize > uint8Array.length) break

    if (type === 'IEND') {
      chunks.push(newChunk)
      chunks.push(uint8Array.slice(i, i + totalSize))
      break
    }

    if (type === 'tEXt' && !charaFound) {
      const dataStart = i + 8
      const chunkData = uint8Array.slice(dataStart, dataStart + chunkLen)
      const text = new TextDecoder('utf-8').decode(chunkData)
      const nullIdx = text.indexOf('\0')
      if (nullIdx > 0) {
        const keyword = text.substring(0, nullIdx).toLowerCase()
        if (keyword === 'chara') {
          charaFound = true
          chunks.push(newChunk)
          i += totalSize
          continue
        }
      }
    }

    chunks.push(uint8Array.slice(i, i + totalSize))
    i += totalSize
  }

  const totalLength = 8 + chunks.reduce((sum, c) => sum + c.length, 0)
  const result = new Uint8Array(totalLength)
  result.set(uint8Array.slice(0, 8), 0)
  let offset = 8
  for (const chunk of chunks) {
    result.set(chunk, offset)
    offset += chunk.length
  }

  return result
}
