#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 完全重写Chat.vue文件，修复所有编码问题

content = '''<template>
  <div class="chat-page">
    <Navbar />

    <div class="chat-shell">
      <aside class="sidebar card">
        <div class="sidebar-head">
          <div>
            <p class="sidebar-eyebrow">AI Coach</p>
            <h2>Chat History</h2>
          </div>
          <div class="sidebar-actions">
            <button class="icon-btn" type="button" @click="newChat">+</button>
          </div>
        </div>

        <div class="history-list">
          <article
            v-for="(chat, index) in chatHistory"
            :key="`${chat.timestamp}-${index}`"
            class="history-item"
            :class="{ active: currentChat === index }"
          >
            <button type="button" class="history-main" @click="loadChatHistory(index)">
              <strong>{{ shorten(chat.question) }}</strong>
              <span>{{ formatTime(chat.timestamp) }}</span>
            </button>
            <button
              type="button"
              class="history-delete"
              title="Delete chat"
              aria-label="Delete chat"
              @click.stop="deleteChatHistory(index)"
            >
              Delete
            </button>
          </article>
          <p v-if="!chatHistory.length" class="empty-copy">No chat history yet.</p>
        </div>
      </aside>

      <section class="main card">
        <header class="main-head">
          <div>
            <p class="main-eyebrow">AI 教练</p>
            <h1>{{ currentChat !== null ? `对话 #${currentChat + 1}` : '开始新对话' }}</h1>
          </div>
          <button v-if="messages.length" type="button" class="btn btn-secondary" @click="newChat">
            新建对话
          </button>
        </header>

        <div ref="messagesContainer" class="messages">
          <div v-if="!messages.length" class="empty-state">
            <div class="empty-badge">AI</div>
            <h3>Start chatting with the AI coach</h3>
            <p>Ask about training goals, recovery, or planning and the AI coach will help.</p>
            <div class="quick-suggestions">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion"
                type="button"
                class="suggestion-chip"
                @click="sendMessage(suggestion)"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>

          <template v-else>
            <article
              v-for="(message, index) in messages"
              :key="`${message.timestamp}-${index}`"
              class="message-row"
              :class="message.role"
            >
              <div class="avatar">{{ message.role === 'user' ? '我' : 'AI' }}</div>
              <div class="message-card">
                <p v-if="message.content" class="message-text">{{ message.content }}</p>

                <div v-if="message.planCard" class="plan-card">
                  <div class="plan-card-head">
                    <div>
                      <p class="plan-tag">AI 生成计划</p>
                      <h3>{{ message.planCard.title }}</h3>
                      <p class="plan-subtitle">{{ message.planCard.subtitle }}</p>
                    </div>
                    <span class="plan-badge">1 个月</span>
                  </div>
                  <div class="plan-meta">
                    <span>{{ message.planCard.weeklyDays }}</span>
                    <span>{{ message.planCard.duration }}</span>
                    <span>{{ message.planCard.intensity }}</span>
                  </div>
                  <p class="plan-summary">{{ message.planCard.summary }}</p>
                  <div class="plan-actions">
                    <button type="button" class="btn btn-primary" @click="viewPlanDetails(message.planCard.planId)">
                      查看详情
                    </button>
                  </div>
                </div>

                <time class="message-time">{{ formatTime(message.timestamp) }}</time>
              </div>
            </article>
          </template>
        </div>

        <div class="quick-actions">
          <button type="button" class="quick-btn" @click="quickAction('我想生成一份运动训练计划')">生成计划</button>
          <button type="button" class="quick-btn" @click="quickAction('我今天适合练什么？')">今日训练</button>
          <button type="button" class="quick-btn" @click="quickAction('帮我安排恢复建议')">恢复建议</button>
          <button type="button" class="quick-btn" @click="quickAction('帮我分析训练进度')">进度分析</button>
        </div>

        <footer class="input-bar">
          <textarea
            ref="inputRef"
            v-model="inputMessage"
            rows="1"
            placeholder="输入你想问AI 教练的问题.."
            @keydown.enter.prevent="handleEnter"
          />
          <button type="button" class="send-btn" :disabled="loading || !inputMessage.trim()" @click="sendMessage()">
            发送
          </button>
        </footer>
      </section>
    </div>

    <div v-if="showPlanPreviewModal" class="modal-mask" @click.self="closePlanPreviewModal">
      <div class="modal-card plan-modal">
        <button type="button" class="modal-close" @click="closePlanPreviewModal">✕</button>
        <template v-if="previewPlan">
          <div class="plan-modal-head">
            <div>
              <p class="plan-tag">AI 生成计划</p>
              <h2>{{ previewPlan.title }}</h2>
              <p class="modal-copy">{{ previewPlan.goal || 'AI generated training plan' }}</p>
            </div>
            <div class="plan-meta">
              <span>{{ previewPlan.metadata?.weekly_days || 'TBD' }}</span>
              <span>{{ previewPlan.metadata?.daily_duration || 'TBD' }}</span>
              <span>{{ previewPlan.metadata?.intensity || 'TBD' }}</span>
            </div>
          </div>

          <section class="modal-section">
            <h3>计划详情</h3>
            <pre>{{ previewPlan.content }}</pre>
          </section>

          <section class="modal-section">
            <h3>Select training days</h3>
            <p class="modal-copy">Choose the weekdays you want to train on for this plan.</p>
            <div class="weekday-grid">
              <button
                v-for="day in weekdayOptions"
                :key="day"
                type="button"
                class="weekday-chip"
                :class="{ active: previewWeekdays.includes(day) }"
                @click="togglePreviewWeekday(day)"
              >
                {{ day }}
              </button>
            </div>
          </section>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closePlanPreviewModal">Cancel</button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!previewWeekdays.length || planPreviewLoading"
              @click="savePreviewWeekdays"
            >
              Save
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const router = useRouter()
const route = useRoute()

const CHAT_HISTORY_STORAGE_KEY = 'sports-training-chat-history'
const ACTIVE_PLAN_KEY = 'sports-training-active-plan-id'
const PENDING_PROMPT_KEY = 'pendingTrainingPrompt'

const suggestions = [
  '我想生成一份运动训练计划',
  '帮我安排今天的训练内容',
  '我最近恢复不太好，怎么办？',
  '帮我分析一下训练节奏'
]

const weekdayOptions = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const messages = ref([])
const chatHistory = ref([])
const currentChat = ref(null)
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)
const pendingPlanContext = ref(null)

const showPlanPreviewModal = ref(false)
const previewPlan = ref(null)
const previewWeekdays = ref([])
const planPreviewLoading = ref(false)

const shorten = (text = '') => (text.length > 22 ? `${text.slice(0, 22)}...` : text)

const formatTime = (value) => {
  if (!value) return ''
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getToday = () => new Date().toISOString().split('T')[0]

const addDays = (dateString, days) => {
  const date = new Date(dateString)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

const normalizeMessage = (message = {}) => ({
  role: message.role || 'assistant',
  content: message.content || '',
  timestamp: message.timestamp ? new Date(message.timestamp) : new Date(),
  planCard: message.planCard || null,
  planQuestionnaire: Boolean(message.planQuestionnaire)
})

const normalizeChatHistory = (history = []) =>
  history.map((item) => ({
    ...item,
    timestamp: item.timestamp ? new Date(item.timestamp) : new Date(),
    conversation: Array.isArray(item.conversation) ? item.conversation.map(normalizeMessage) : []
  }))

const saveChatHistoryToLocal = () => {
  try {
    localStorage.setItem(CHAT_HISTORY_STORAGE_KEY, JSON.stringify(chatHistory.value))
  } catch (error) {
    console.error('保存聊天记录失败:', error)
  }
}

const loadChatHistoryFromLocal = () => {
  try {
    const raw = localStorage.getItem(CHAT_HISTORY_STORAGE_KEY)
    if (!raw) return []
    return normalizeChatHistory(JSON.parse(raw))
  } catch (error) {
    console.error('读取本地聊天记录失败:', error)
    return []
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const newChat = () => {
  messages.value = []
  currentChat.value = null
}

const deleteChatHistory = (index) => {
  if (!window.confirm('确定删除这条对话记录吗？')) return

  chatHistory.value.splice(index, 1)

  if (currentChat.value === index) {
    messages.value = []
    currentChat.value = null
    return
  }

  if (currentChat.value !== null && currentChat.value > index) {
    currentChat.value -= 1
  }
}

const loadChatHistory = (index) => {
  currentChat.value = index
  const chat = chatHistory.value[index]
  messages.value = (chat?.conversation || []).map(normalizeMessage)
  scrollToBottom()
}

const buildPlanTitle = (planContext = null) => {
  const goal = planContext?.questionnaire?.goal || 'AI Training Plan'
  return `${goal}`
}

const buildPlanPayloadFromMessage = (message, planContext = null) => {
  const questionnaire = planContext?.questionnaire || {}
  const content = message?.content || ''
  const startDate = getToday()

  return {
    title: buildPlanTitle(planContext),
    content,
    created_from_ai: true,
    goal: questionnaire.goal || 'AI 教练推荐',
    start_date: startDate,
    end_date: addDays(startDate, 29),
    metadata: questionnaire,
    source_prompt: planContext?.prompt || '',
    ai_response: content,
    selected_weekdays: []
  }
}

const createPlanCardMessage = (savedPlan, planContext = null) => {
  const questionnaire = planContext?.questionnaire || savedPlan?.metadata || {}
  const summary = (savedPlan?.content || '').slice(0, 150)

  return normalizeMessage({
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    planCard: {
      planId: savedPlan.id,
      title: savedPlan.title,
      subtitle: questionnaire.goal || 'AI generated plan',
      weeklyDays: questionnaire.weekly_days || 'TBD',
      duration: questionnaire.daily_duration || 'TBD',
      intensity: questionnaire.intensity || 'TBD',
      summary: summary || 'Plan generated by AI coach.'
    }
  })
}

const createPlanFromAiResponse = async (message, planContext = null) => {
  const response = await api.post('/training/plans', buildPlanPayloadFromMessage(message, planContext))
  if (!response?.plan?.id) {
    throw new Error('训练计划生成失败')
  }
  return response.plan
}

const extractAnswer = (response) => response?.answer || response?.content || response?.response || '我已经收到你的问题，但暂时没有生成有效回复。'

const buildBriefAdvice = (content = '') => {
  const normalized = String(content).replace(/\\s+/g, ' ').trim()
  if (!normalized) return '我已经根据你的情况整理出一份运动建议，并生成了对应训练计划。'

  const firstSentence = normalized.split(/(?<=[。！？，、；])/)[0]?.trim() || normalized
  const brief = firstSentence.length > 72 ? `${firstSentence.slice(0, 72)}...` : firstSentence
  return `综合建议：${brief}`
}

const updateCurrentConversation = (question, assistantMessage) => {
  if (currentChat.value !== null && chatHistory.value[currentChat.value]) {
    const target = chatHistory.value[currentChat.value]
    target.conversation.push(
      normalizeMessage({ role: 'user', content: question, timestamp: new Date() }),
      assistantMessage
    )
    target.question = question
    target.answer = assistantMessage.content
    target.timestamp = new Date()
    return
  }

  chatHistory.value.unshift({
    question,
    answer: assistantMessage.content,
    timestamp: new Date(),
    conversation: [
      normalizeMessage({ role: 'user', content: question, timestamp: new Date() }),
      assistantMessage
    ]
  })
  currentChat.value = 0
}

const sendMessage = async (text = null, options = {}) => {
  const question = text || inputMessage.value.trim()
  const planContext = options.planContext || pendingPlanContext.value
  if (!question || loading.value) return

  messages.value.push(normalizeMessage({ role: 'user', content: question, timestamp: new Date() }))
  inputMessage.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const response = await api.query(question)
    const assistantMessage = normalizeMessage({
      role: 'assistant',
      content: extractAnswer(response),
      timestamp: new Date()
    })
    if (planContext) {
      const savedPlan = await createPlanFromAiResponse(assistantMessage, planContext)
      const planCardMessage = createPlanCardMessage(savedPlan, planContext)
      assistantMessage.content = buildBriefAdvice(assistantMessage.content)
      assistantMessage.planCard = planCardMessage.planCard
      pendingPlanContext.value = null
      sessionStorage.removeItem(PENDING_PROMPT_KEY)
    }

    messages.value.push(assistantMessage)
    updateCurrentConversation(question, assistantMessage)
    await scrollToBottom()
  } catch (error) {
    console.error('发送消息失败', error)
    messages.value.push(
      normalizeMessage({
        role: 'assistant',
        content: '消息发送失败，请稍后重试。',
        timestamp: new Date()
      })
    )
  } finally {
    loading.value = false
  }
}

const generatePlan = async (message) => {
  try {
    const savedPlan = await createPlanFromAiResponse(message)
    const planCardMessage = createPlanCardMessage(savedPlan)
    message.content = buildBriefAdvice(message.content)
    message.planCard = planCardMessage.planCard
    if (currentChat.value !== null && chatHistory.value[currentChat.value]) {
      const conversation = chatHistory.value[currentChat.value].conversation || []
      const target = conversation.find((item) => item.timestamp?.getTime?.() === message.timestamp?.getTime?.())
      if (target) {
        target.content = message.content
        target.planCard = message.planCard
      }
      chatHistory.value[currentChat.value].timestamp = new Date()
    }
    await scrollToBottom()
  } catch (error) {
    console.error('训练计划生成失败:', error)
    window.alert('训练计划生成失败，请稍后重试。')
  }
}

const normalizePreviewPlan = (plan) => ({
  ...plan,
  metadata: plan?.metadata || {},
  selected_weekdays: Array.isArray(plan?.selected_weekdays) ? plan.selected_weekdays : []
})

const closePlanPreviewModal = () => {
  showPlanPreviewModal.value = false
  previewPlan.value = null
  previewWeekdays.value = []
}

const viewPlanDetails = async (planId) => {
  planPreviewLoading.value = true
  try {
    const response = await api.get(`/training/plans/${planId}`)
    previewPlan.value = normalizePreviewPlan(response)
    previewWeekdays.value = [...previewPlan.value.selected_weekdays]
    showPlanPreviewModal.value = true
  } catch (error) {
    console.error('读取训练计划详情失败:', error)
    window.alert('训练计划详情加载失败，请稍后重试。')
  } finally {
    planPreviewLoading.value = false
  }
}

const togglePreviewWeekday = (day) => {
  previewWeekdays.value = previewWeekdays.value.includes(day)
    ? previewWeekdays.value.filter((item) => item !== day)
    : [...previewWeekdays.value, day]
}

const savePreviewWeekdays = async () => {
  if (!previewPlan.value || !previewWeekdays.value.length) return

  planPreviewLoading.value = true
  try {
    await api.put(`/training/plans/${previewPlan.value.id}`, {
      selected_weekdays: [...previewWeekdays.value]
    })
    localStorage.setItem(ACTIVE_PLAN_KEY, String(previewPlan.value.id))
    closePlanPreviewModal()
    router.push({ name: 'TrainingPlan' })
  } catch (error) {
    console.error('保存训练日失败', error)
    window.alert('保存训练日失败，请稍后重试。')
  } finally {
    planPreviewLoading.value = false
  }
}

const quickAction = (action) => {
  if (action === '我想生成一份运动训练计划') {
    router.push({ name: 'TrainingQuestionnaire' })
    return
  }

  inputMessage.value = action
  nextTick(() => inputRef.value?.focus())
}

const handleEnter = (event) => {
  if (!event.shiftKey) {
    sendMessage()
  }
}

const loadPendingPrompt = () => {
  try {
    const raw = sessionStorage.getItem(PENDING_PROMPT_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (error) {
    console.error('读取待发送训练prompt失败:', error)
    return null
  }
}

onMounted(async () => {
  const localHistory = loadChatHistoryFromLocal()
  if (localHistory.length) {
    chatHistory.value = localHistory
  } else {
    try {
      const response = await api.getChatHistory()
      chatHistory.value = normalizeChatHistory(response?.history || [])
    } catch (error) {
      console.error('读取聊天历史失败:', error)
    }
  }

  if (route.query.autoPlan === '1') {
    const pendingPrompt = loadPendingPrompt()
    if (pendingPrompt?.prompt) {
      pendingPlanContext.value = pendingPrompt
      await sendMessage(pendingPrompt.prompt, { planContext: pendingPrompt })
      router.replace({ name: 'Chat' })
    }
  }
})

watch(
  chatHistory,
  () => {
    saveChatHistoryToLocal()
  },
  { deep: true }
)
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(52, 199, 89, 0.16), transparent 24%),
    linear-gradient(180deg, #f5fbf8 0%, #edf5f1 100%);
}

.chat-shell {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 16px 40px;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 24px;
}

.card {
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(23, 63, 52, 0.08);
  border-radius: 28px;
  box-shadow: 0 24px 60px rgba(20, 61, 48, 0.08);
  backdrop-filter: blur(14px);
}

.sidebar {
  padding: 22px 18px;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 132px);
}

.sidebar-head,
.main-head,
.plan-card-head,
.plan-modal-head,
.modal-actions,
.sidebar-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.sidebar-head,
.main-head,
.plan-card-head,
.plan-modal-head {
  align-items: flex-start;
}

.sidebar-eyebrow,
.main-eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #34a36c;
}

.sidebar h2,
.main-head h1,
.plan-card h3,
.plan-modal h2 {
  margin: 0;
  color: #16362d;
}

.sidebar-actions {
  justify-content: flex-end;
}

.icon-btn,
.btn,
.suggestion-chip,
.quick-btn,
.send-btn,
.history-main,
.history-delete,
.inline-plan-btn,
.weekday-chip {
  border: none;
  cursor: pointer;
  font: inherit;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: #eef6f1;
  color: #23483c;
}

.icon-btn.danger {
  background: rgba(239, 68, 68, 0.12);
  color: #d63e4c;
}

.history-list {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: auto;
}

.history-item {
  padding: 14px;
  border-radius: 18px;
  background: #f6faf8;
  color: #29483f;
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.history-main {
  flex: 1;
  padding: 0;
  text-align: left;
  background: transparent;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.history-delete {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.12);
  color: #d63e4c;
  font-size: 12px;
  font-weight: 600;
}

.history-item.active {
  background: linear-gradient(135deg, rgba(52, 199, 89, 0.18), rgba(52, 199, 89, 0.08));
}

.history-main span,
.empty-copy,
.message-time,
.plan-subtitle,
.modal-copy {
  color: #6f857d;
  font-size: 13px;
}

.main {
  min-height: calc(100vh - 132px);
  display: flex;
  flex-direction: column;
  padding: 24px;
}

.messages {
  flex: 1;
  overflow: auto;
  padding-right: 4px;
}

.empty-state {
  min-height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 14px;
}

.empty-badge {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34c759, #1d8f56);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 800;
}

.quick-suggestions,
.quick-actions,
.plan-meta,
.weekday-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.suggestion-chip,
.quick-btn,
.plan-meta span,
.weekday-chip {
  padding: 10px 14px;
  border-radius: 999px;
  background: #eef6f1;
  color: #285647;
  font-weight: 600;
}

.message-row {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}

.message-row.user {
  grid-template-columns: minmax(0, 1fr) 44px;
}

.message-row.user .avatar {
  order: 2;
}

.message-row.user .message-card {
  order: 1;
  background: linear-gradient(135deg, #173f34, #225949);
  color: #fff;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #e9f7ef;
  color: #1d5b43;
  display: grid;
  place-items: center;
  font-weight: 800;
}

.message-card {
  background: #f8fbfa;
  border-radius: 24px;
  padding: 18px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.message-text,
.plan-summary {
  margin: 0;
  line-height: 1.7;
  white-space: pre-wrap;
}

.inline-plan-btn {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(52, 199, 89, 0.14);
  color: #20814f;
  font-weight: 700;
}

.plan-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.plan-tag {
  margin: 0 0 8px;
  color: #34a36c;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.plan-badge {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(52, 199, 89, 0.12);
  color: #249059;
  font-weight: 700;
}

.plan-actions {
  display: flex;
  justify-content: flex-start;
}

.quick-actions {
  margin-top: 18px;
}

.input-bar {
  margin-top: 20px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: end;
}

.input-bar textarea {
  min-height: 56px;
  max-height: 180px;
  resize: vertical;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px solid rgba(23, 63, 52, 0.12);
  background: #f8fbfa;
  font: inherit;
  color: #16362d;
}

.send-btn,
.btn {
  padding: 12px 18px;
  border-radius: 16px;
  font-weight: 700;
}

.btn-primary,
.send-btn {
  background: linear-gradient(135deg, #34c759, #24945a);
  color: #fff;
  box-shadow: 0 14px 28px rgba(52, 199, 89, 0.22);
}

.btn-secondary {
  background: #eef6f1;
  color: #2d5f4e;
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(12, 24, 20, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 40;
}

.modal-card {
  width: min(920px, 100%);
  max-height: 88vh;
  overflow: auto;
  position: relative;
  border-radius: 30px;
  background: linear-gradient(180deg, #ffffff, #f4fbf7);
  box-shadow: 0 28px 70px rgba(12, 24, 20, 0.22);
}

.plan-modal {
  padding: 32px;
}

.modal-close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #eef4f1;
  color: #36584d;
  font-size: 24px;
  cursor: pointer;
}

.modal-section {
  margin-top: 20px;
  padding: 22px;
  border-radius: 24px;
  background: #fff;
  border: 1px solid rgba(23, 63, 52, 0.08);
}

.modal-section h3 {
  margin: 0 0 12px;
}

.modal-section pre {
  margin: 0;
  white-space: pre-wrap;
  line-height: 1.7;
  font-family: inherit;
  color: #21463b;
}

.weekday-grid {
  margin-top: 14px;
}

.weekday-chip.active {
  background: linear-gradient(135deg, #34c759, #24945a);
  color: #fff;
}

.modal-actions {
  margin-top: 22px;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .chat-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    min-height: auto;
  }

  .main {
    min-height: auto;
  }
}

@media (max-width: 720px) {
  .chat-shell,
  .main,
  .plan-modal {
    padding-left: 14px;
    padding-right: 14px;
  }

  .main-head,
  .plan-modal-head,
  .modal-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .input-bar {
    grid-template-columns: 1fr;
  }
}
</style>
'''

with open(r'd:\Graduation Project\运动训练问答Agent\frontend\src\views\Chat.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('✓ Chat.vue 已完全重写并修复所有错误！')
