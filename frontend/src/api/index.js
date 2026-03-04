import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // 查询问答（流式）
  queryStream(question, onChunk, onComplete, onError) {
    const eventSource = new EventSource(`/api/query?question=${encodeURIComponent(question)}`)
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.error) {
          onError(new Error(data.error))
          eventSource.close()
          return
        }
        
        if (data.done) {
          onComplete()
          eventSource.close()
        } else {
          onChunk(data.content)
        }
      } catch (error) {
        onError(error)
        eventSource.close()
      }
    }
    
    eventSource.onerror = (error) => {
      onError(error)
      eventSource.close()
    }
    
    return eventSource
  },
  
  // 查询问答（非流式，兼容）
  query(question) {
    return api.post('/query/sync', { question })
  },
  
  // 加载知识库
  loadKnowledge(forceReload = false) {
    return api.post('/knowledge/load', null, {
      params: { force_reload: forceReload }
    })
  },
  
  // 获取记忆摘要
  getMemorySummary() {
    return api.get('/memory/summary')
  },
  
  // 获取知识库统计
  getKnowledgeStats() {
    return api.get('/knowledge/stats')
  },
  
  // 清空工作记忆
  clearWorkingMemory() {
    return api.post('/memory/clear')
  },
  
  // 获取对话历史
  getChatHistory() {
    return api.get('/chat/history')
  }
}
