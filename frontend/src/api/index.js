import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => {
    if (response.data === undefined || response.data === null) {
      console.warn('API returned empty response body')
      return {}
    }
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
    }
    return Promise.reject(error)
  }
)

export default {
  /**
   * 发起流式查询请求
   * 支持两种接口：
   * 1. 旧接口: queryStream(question, onChunk, onComplete, onError, options)
   * 2. 新接口: queryStream(question, handlers, onComplete, onError, options)
   *    handlers = { thinking: fn, answer: fn, scheduler: fn, progress_log: fn }
   */
  async queryStream(question, onChunkOrHandlers, onComplete, onError, options = {}) {
    // 检测是否使用新接口（handlers 对象）
    const isHandlersObject = typeof onChunkOrHandlers === 'object' && onChunkOrHandlers !== null

    // 统一处理函数
    const handleChunk = (chunk, type, data) => {
      if (isHandlersObject) {
        // 新接口：根据 type 调用对应的 handler
        const handler = onChunkOrHandlers[type]
        if (handler) {
          handler(chunk, data)
        }
      } else {
        // 旧接口：直接调用 onChunk
        onChunkOrHandlers(chunk, type, data)
      }
    }

    try {
      const token = localStorage.getItem('token')
      const headers = {
        'Content-Type': 'application/json'
      }
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }

      const requestBody = {
        question,
        use_multi_agent: Boolean(options.useMultiAgent),
        user_profile: options.userProfile || null,
        conversation_id: options.conversationId || null
      }

      // 添加附件参数
      if (options.attachments && options.attachments.length > 0) {
        requestBody.attachments = options.attachments.map(a => String(a.assetId))
      }

      const response = await fetch('/api/query', {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      if (!response.body) {
        throw new Error('Empty response stream')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let answerCompleted = false

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        while (true) {
          const eventEnd = buffer.indexOf('\n\n')
          if (eventEnd === -1) break

          const rawEvent = buffer.slice(0, eventEnd)
          buffer = buffer.slice(eventEnd + 2)

          const dataLines = rawEvent
            .split(/\r?\n/)
            .filter((line) => line.startsWith('data:'))
          if (!dataLines.length) continue

          const payload = dataLines.map((line) => line.slice(5).trimStart()).join('\n')

          try {
            const data = JSON.parse(payload)
            if (data.error) {
              onError(new Error(data.error))
              return
            }

            const type = data.type || 'answer'
            if (data.done) {
              if (type === 'answer') answerCompleted = true
              onComplete(type, data)
            } else {
              handleChunk(data.content || '', type, data)
            }
          } catch (_e) {
            continue
          }
        }
      }

      if (!answerCompleted) {
        onComplete('answer')
      }
    } catch (error) {
      onError(error)
    }
  },

  query(question) {
    return api.post('/query/sync', { question })
  },

  loadKnowledge(forceReload = false) {
    return api.post('/knowledge/load', null, {
      params: { force_reload: forceReload },
      timeout: 0  // 知识库加载不限超时（含 OCR 处理可能超过 10 分钟）
    })
  },

  getMemorySummary() {
    return api.get('/memory/summary')
  },

  getMemoryDashboard() {
    return api.get('/memory/dashboard')
  },

  getSemanticMemory(category) {
    return api.get('/memory/semantic', {
      params: category ? { category } : {}
    })
  },

  getMemoryEpisodes(params = {}) {
    return api.get('/memory/episodes', { params })
  },

  initializeProfile(profile) {
    return api.post('/profile/init', profile)
  },

  getMyProfile() {
    return api.get('/profile/me')
  },

  updateMyProfile(profile) {
    return api.put('/profile/me', profile)
  },

  getKnowledgeStats() {
    return api.get('/knowledge/stats')
  },

  getKnowledgeDocuments() {
    return api.get('/knowledge/documents')
  },

  uploadKnowledgeDocument(file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/knowledge/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 0  // 文件上传不设超时限制
    })
  },

  deleteKnowledgeDocument(docId) {
    return api.delete(`/knowledge/documents/${docId}`)
  },

  clearWorkingMemory() {
    return api.post('/memory/clear')
  },

  changePassword(currentPassword, newPassword) {
    return api.put('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  uploadAvatar(formData) {
    return api.post('/auth/upload-avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  getChatHistory() {
    return api.get('/chat/history')
  },

  get(url, config) {
    return api.get(url, config)
  },

  post(url, data, config) {
    return api.post(url, data, config)
  },

  put(url, data, config) {
    return api.put(url, data, config)
  },

  delete(url, config) {
    return api.delete(url, config)
  }
}
