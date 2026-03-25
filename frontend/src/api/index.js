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
  async queryStream(question, onChunk, onComplete, onError) {
    try {
      const token = localStorage.getItem('token')
      const headers = {
        'Content-Type': 'application/json'
      }
      if (token) {
        headers.Authorization = `Bearer ${token}`
      }

      const response = await fetch('/api/query', {
        method: 'POST',
        headers,
        body: JSON.stringify({ question, use_multi_agent: false })
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
              onComplete(type)
            } else {
              onChunk(data.content || '', type)
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
      params: { force_reload: forceReload }
    })
  },

  getMemorySummary() {
    return api.get('/memory/summary')
  },

  getKnowledgeStats() {
    return api.get('/knowledge/stats')
  },

  clearWorkingMemory() {
    return api.post('/memory/clear')
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
