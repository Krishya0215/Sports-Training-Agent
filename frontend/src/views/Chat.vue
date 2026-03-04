<template>
  <div class="chat-page">
    <Navbar />
    
    <div class="chat-container">
      <div class="chat-sidebar card">
        <div class="sidebar-header">
          <h3>对话历史</h3>
          <div class="header-actions">
            <button class="icon-btn" @click="newChat" title="新建对话">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M9 3V15M3 9H15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
            <button class="icon-btn" @click="clearMemory" title="清空记忆">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M3 3L15 15M3 15L15 3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="chat-list">
          <div v-if="chatHistory.length === 0" class="empty-history">
            <p>暂无对话历史</p>
          </div>
          <div 
            v-for="(chat, index) in chatHistory" 
            :key="index"
            class="chat-item"
            :class="{ active: currentChat === index }"
            @click="loadChatHistory(index)"
          >
            <div class="chat-item-title">{{ chat.question.substring(0, 30) }}{{ chat.question.length > 30 ? '...' : '' }}</div>
            <div class="chat-item-time">{{ formatTime(chat.timestamp) }}</div>
          </div>
        </div>
      </div>
      
      <div class="chat-main">
        <div class="chat-header">
          <div class="header-info">
            <h2>{{ currentChat !== null ? `对话 #${currentChat + 1}` : '新对话' }}</h2>
            <div class="mode-toggle">
              <button 
                class="mode-btn" 
                :class="{ active: !useMultiAgent }"
                @click="useMultiAgent = false"
                title="单智能体模式"
              >
                🤖 单智能体
              </button>
              <button 
                class="mode-btn" 
                :class="{ active: useMultiAgent }"
                @click="useMultiAgent = true"
                title="多智能体协同模式"
              >
                👥 多智能体
              </button>
            </div>
          </div>
          <button v-if="messages.length > 0" class="btn btn-secondary" @click="newChat">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2V14M2 8H14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            新建对话
          </button>
        </div>
        
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">💬</div>
            <h3>开始对话</h3>
            <p>向我提问关于运动训练的任何问题</p>
            
            <div class="suggestions">
              <button 
                v-for="(suggestion, index) in suggestions" 
                :key="index"
                class="suggestion-btn"
                @click="sendMessage(suggestion)"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>
          
          <div v-else class="messages">
            <div 
              v-for="(message, index) in messages" 
              :key="index"
              class="message"
              :class="message.role"
            >
              <div class="message-avatar">
                <svg v-if="message.role === 'user'" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <circle cx="10" cy="7" r="3"/>
                  <path d="M4 18C4 14.6863 6.68629 12 10 12C13.3137 12 16 14.6863 16 18"/>
                </svg>
                <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <circle cx="10" cy="10" r="8"/>
                  <circle cx="7" cy="9" r="1.5" fill="white"/>
                  <circle cx="13" cy="9" r="1.5" fill="white"/>
                  <path d="M7 13C7 13 8.5 14.5 10 14.5C11.5 14.5 13 13 13 13" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="message-content">
                <div class="message-text" :class="{ streaming: message.streaming }">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="input-container">
          <div class="input-wrapper">
            <textarea
              v-model="inputMessage"
              @keydown.enter.prevent="handleEnter"
              placeholder="输入您的问题..."
              rows="1"
              ref="inputRef"
            ></textarea>
            <button 
              class="send-btn"
              :disabled="!inputMessage.trim() || loading"
              @click="sendMessage()"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M18 2L9 11M18 2L12 18L9 11M18 2L2 8L9 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)
const chatHistory = ref([])
const currentChat = ref(null)
const useMultiAgent = ref(false)  // 多智能体模式开关

const suggestions = [
  '什么是有氧运动？',
  '如何进行力量训练？',
  '运动后如何拉伸？',
  '减肥应该做什么运动？'
]

const sendMessage = async (text = null) => {
  const content = text || inputMessage.value.trim()
  if (!content || loading.value) return
  
  console.log('发送消息:', content)
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content,
    timestamp: new Date()
  })
  
  inputMessage.value = ''
  loading.value = true
  
  await nextTick()
  scrollToBottom()
  
  // 添加助手消息占位符
  const assistantMessageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: '正在思考...',
    timestamp: new Date(),
    streaming: true
  })
  
  try {
    console.log('正在调用API（流式）...')
    
    let fullAnswer = ''
    let isFirstChunk = true
    
    // 使用fetch实现SSE
    const response = await fetch('/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        question: content,
        use_multi_agent: useMultiAgent.value,
        user_profile: {
          fitness_level: '中级',
          goals: ['健康', '增强体质']
        }
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            
            if (data.error) {
              throw new Error(data.error)
            }
            
            if (data.done) {
              // 流式传输完成
              messages.value[assistantMessageIndex].streaming = false
              console.log('流式传输完成')
            } else if (data.content) {
              // 第一次接收到数据时，清空"正在思考..."
              if (isFirstChunk) {
                messages.value[assistantMessageIndex].content = ''
                isFirstChunk = false
              }
              
              // 追加内容
              fullAnswer += data.content
              messages.value[assistantMessageIndex].content = fullAnswer
              await nextTick()
              scrollToBottom()
            }
          } catch (e) {
            console.error('解析数据失败:', e)
          }
        }
      }
    }
    
    // 确保chatHistory是数组
    if (!Array.isArray(chatHistory.value)) {
      chatHistory.value = []
    }
    
    // 如果是在历史对话中继续提问，更新该对话
    if (currentChat.value !== null) {
      // 更新历史记录中的对话，添加新的问答
      const chat = chatHistory.value[currentChat.value]
      if (!chat.conversation) {
        chat.conversation = [
          { role: 'user', content: chat.question, timestamp: chat.timestamp },
          { role: 'assistant', content: chat.answer, timestamp: chat.timestamp }
        ]
      }
      chat.conversation.push(
        { role: 'user', content: content, timestamp: new Date() },
        { role: 'assistant', content: fullAnswer, timestamp: new Date() }
      )
      // 保持第一个问题作为标题，只更新最后的回答和时间戳
      chat.answer = fullAnswer
      chat.timestamp = new Date()
    } else {
      // 添加新的对话到历史记录
      const historyItem = {
        question: content,  // 第一个问题作为标题
        answer: fullAnswer,
        timestamp: new Date(),
        conversation: [
          { role: 'user', content: content, timestamp: new Date() },
          { role: 'assistant', content: fullAnswer, timestamp: new Date() }
        ]
      }
      
      chatHistory.value.unshift(historyItem)
      // 设置当前对话为新创建的对话
      currentChat.value = 0
    }
    
    console.log('添加到历史记录')
    console.log('当前历史记录数量:', chatHistory.value.length)
    
    console.log('API响应完成')
    
  } catch (error) {
    console.error('发送消息失败:', error)
    
    let errorMessage = '抱歉，处理您的问题时出现错误。'
    
    if (error.code === 'ECONNABORTED') {
      errorMessage = '请求超时，请检查网络连接。'
    } else if (error.message) {
      errorMessage = `错误: ${error.message}`
    } else if (error.response) {
      errorMessage = `服务器错误: ${error.response.status} - ${error.response.data?.detail || error.response.statusText}`
    } else if (error.request) {
      errorMessage = '无法连接到后端服务，请确保后端已启动（http://localhost:8000）'
    }
    
    messages.value[assistantMessageIndex].content = errorMessage
    messages.value[assistantMessageIndex].streaming = false
    
  } finally {
    loading.value = false
    await nextTick()
    scrollToBottom()
  }
}

const handleEnter = (e) => {
  if (!e.shiftKey) {
    sendMessage()
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const clearMemory = async () => {
  if (confirm('确定要清空对话记忆吗？')) {
    try {
      await api.clearWorkingMemory()
      messages.value = []
      chatHistory.value = []
      currentChat.value = null
    } catch (error) {
      console.error('Failed to clear memory:', error)
    }
  }
}

const newChat = () => {
  if (messages.value.length > 0) {
    if (confirm('开始新对话将清空当前消息，是否继续？')) {
      messages.value = []
      currentChat.value = null
      console.log('开始新对话')
    }
  }
}

const loadChatHistory = (index) => {
  currentChat.value = index
  const chat = chatHistory.value[index]
  
  // 如果有完整的对话历史，加载它
  if (chat.conversation && Array.isArray(chat.conversation)) {
    messages.value = chat.conversation.map(msg => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    }))
  } else {
    // 兼容旧格式：只有一轮问答
    messages.value = [
      {
        role: 'user',
        content: chat.question,
        timestamp: new Date(chat.timestamp)
      },
      {
        role: 'assistant',
        content: chat.answer,
        timestamp: new Date(chat.timestamp),
        streaming: false
      }
    ]
  }
  
  console.log('加载历史对话:', chat)
  
  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
}

onMounted(async () => {
  try {
    const response = await api.getChatHistory()
    // API返回的是 { history: [...], total: ... }，需要取history字段
    chatHistory.value = response.history || []
    console.log('加载对话历史:', chatHistory.value.length, '条')
  } catch (error) {
    console.error('Failed to load chat history:', error)
    // 确保chatHistory始终是数组
    chatHistory.value = []
  }
})
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 24px;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 24px;
  height: calc(100vh - 80px);
}

.chat-sidebar {
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.header-actions {
  display: flex;
  gap: 8px;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
}

.empty-history {
  padding: 40px 20px;
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.chat-item {
  padding: 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.chat-item:hover {
  background: var(--color-bg);
}

.chat-item.active {
  background: var(--color-bg);
}

.chat-item-title {
  font-size: 14px;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  font-weight: 500;
}

.chat-item-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.chat-main {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.chat-header {
  padding: 20px 32px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-surface);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.mode-toggle {
  display: flex;
  gap: 8px;
  padding: 4px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.mode-btn {
  padding: 6px 12px;
  border: none;
  border-radius: calc(var(--radius-md) - 2px);
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.mode-btn:hover {
  color: var(--color-text-primary);
}

.mode-btn.active {
  background: var(--color-surface);
  color: var(--color-accent);
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chat-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.chat-badge {
  padding: 4px 12px;
  background: var(--color-bg);
  color: var(--color-text-secondary);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.chat-header .btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
}

.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin-bottom: 32px;
}

.suggestions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 600px;
}

.suggestion-btn {
  padding: 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.suggestion-btn:hover {
  border-color: var(--color-accent);
  background: var(--color-bg);
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message {
  display: flex;
  gap: 12px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: var(--color-accent);
  color: white;
}

.message.assistant .message-avatar {
  background: var(--color-text-primary);
  color: white;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: var(--color-bg);
  color: var(--color-text-primary);
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  position: relative;
}

.message.user .message-text {
  background: var(--color-accent);
  color: white;
}

/* 流式输出光标效果 */
.message-text.streaming::after {
  content: '▋';
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.message-time {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
  padding: 0 4px;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.input-container {
  padding: 20px 32px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.readonly-notice {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: 14px;
}

.readonly-notice svg {
  flex-shrink: 0;
  color: var(--color-accent);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  resize: none;
  max-height: 120px;
  font-family: inherit;
}

.send-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-accent);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
