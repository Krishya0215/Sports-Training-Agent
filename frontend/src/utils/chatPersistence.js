/**
 * 聊天持久化存储服务
 * 使用 IndexedDB 存储聊天消息，支持跨页面恢复
 */

const DB_NAME = 'SportsTrainingChatDB'
const STORE_NAME = 'messages'
const STREAMING_STATE_STORE = 'streamingState'
const DB_VERSION = 3

let dbInstance = null

/**
 * 初始化 IndexedDB
 */
async function initDB() {
  if (dbInstance) return dbInstance

  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      dbInstance = request.result
      resolve(dbInstance)
    }

    request.onupgradeneeded = (event) => {
      const db = event.target.result

      // 消息存储
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const messageStore = db.createObjectStore(STORE_NAME, { keyPath: 'id' })
        messageStore.createIndex('userId', 'userId')
        messageStore.createIndex('conversationId', 'conversationId')
        messageStore.createIndex('timestamp', 'timestamp')
      }

      // 流式状态存储 - 用于跟踪正在进行的生成
      if (!db.objectStoreNames.contains(STREAMING_STATE_STORE)) {
        const stateStore = db.createObjectStore(STREAMING_STATE_STORE, { keyPath: 'id' })
        stateStore.createIndex('userId', 'userId')
      }
    }
  })
}

/**
 * 生成唯一 ID
 */
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 保存消息
 */
export async function saveMessage(message) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite')
    const store = transaction.objectStore(STORE_NAME)

    // 确保有 ID
    if (!message.id) {
      message.id = generateId()
    }

    const request = store.put(message)
    request.onsuccess = () => resolve(message)
    request.onerror = () => reject(request.error)
  })
}

/**
 * 获取用户的所有消息
 */
export async function getUserMessages(userId) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readonly')
    const store = transaction.objectStore(STORE_NAME)
    const index = store.index('userId')
    const request = index.getAll(userId)

    request.onsuccess = () => {
      const messages = request.result.sort((a, b) =>
        new Date(a.timestamp) - new Date(b.timestamp)
      )
      resolve(messages)
    }
    request.onerror = () => reject(request.error)
  })
}

/**
 * 获取对话消息
 */
export async function getConversationMessages(conversationId) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readonly')
    const store = transaction.objectStore(STORE_NAME)
    const index = store.index('conversationId')
    const request = index.getAll(conversationId)

    request.onsuccess = () => {
      const messages = request.result.sort((a, b) =>
        new Date(a.timestamp) - new Date(b.timestamp)
      )
      resolve(messages)
    }
    request.onerror = () => reject(request.error)
  })
}

/**
 * 删除消息
 */
export async function deleteMessage(messageId) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite')
    const store = transaction.objectStore(STORE_NAME)
    const request = store.delete(messageId)
    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

/**
 * 清除用户所有消息
 */
export async function clearUserMessages(userId) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite')
    const store = transaction.objectStore(STORE_NAME)
    const index = store.index('userId')
    const request = index.openCursor()

    request.onsuccess = (event) => {
      const cursor = event.target.result
      if (cursor) {
        cursor.delete()
        cursor.continue()
      } else {
        resolve()
      }
    }
    request.onerror = () => reject(request.error)
  })
}

/**
 * 保存流式生成状态
 */
export async function saveStreamingState(state) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STREAMING_STATE_STORE], 'readwrite')
    const store = transaction.objectStore(STREAMING_STATE_STORE)

    const stateData = {
      id: state.id || `streaming-${state.userId}`,
      ...state,
      updatedAt: new Date().toISOString()
    }

    const request = store.put(stateData)
    request.onsuccess = () => resolve(stateData)
    request.onerror = () => reject(request.error)
  })
}

/**
 * 获取流式生成状态
 */
export async function getStreamingState(userId) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STREAMING_STATE_STORE], 'readonly')
    const store = transaction.objectStore(STREAMING_STATE_STORE)
    const index = store.index('userId')
    const request = index.get(userId)

    request.onsuccess = () => resolve(request.result || null)
    request.onerror = () => reject(request.error)
  })
}

/**
 * 清除流式生成状态
 */
export async function clearStreamingState(userId) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STREAMING_STATE_STORE], 'readwrite')
    const store = transaction.objectStore(STREAMING_STATE_STORE)
    const request = store.delete(`streaming-${userId}`)

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

/**
 * 检查是否有未完成的生成
 */
export async function hasIncompleteGeneration(userId) {
  const state = await getStreamingState(userId)
  if (!state) return false

  // 检查是否在5分钟内（超过5分钟视为过期）
  const updatedAt = new Date(state.updatedAt)
  const now = new Date()
  const diffMinutes = (now - updatedAt) / (1000 * 60)

  if (diffMinutes > 5) {
    await clearStreamingState(userId)
    return false
  }

  return !state.completed
}

/**
 * 批量保存消息
 */
export async function saveMessagesBatch(messages) {
  const db = await initDB()
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], 'readwrite')
    const store = transaction.objectStore(STORE_NAME)

    let completed = 0
    const total = messages.length

    messages.forEach(message => {
      if (!message.id) {
        message.id = generateId()
      }
      const request = store.put(message)
      request.onsuccess = () => {
        completed++
        if (completed === total) resolve(messages)
      }
      request.onerror = () => reject(request.error)
    })

    if (total === 0) resolve([])
  })
}

/**
 * 导出聊天历史
 */
export async function exportChatHistory(userId) {
  const messages = await getUserMessages(userId)
  return {
    userId,
    exportedAt: new Date().toISOString(),
    messages
  }
}

// 导出服务
export const chatPersistence = {
  saveMessage,
  getUserMessages,
  getConversationMessages,
  deleteMessage,
  clearUserMessages,
  saveStreamingState,
  getStreamingState,
  clearStreamingState,
  hasIncompleteGeneration,
  saveMessagesBatch,
  exportChatHistory
}

export default chatPersistence
