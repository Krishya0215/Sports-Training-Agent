<template>
  <div class="chat-page">
    <Navbar />

    <div class="chat-shell">
      <aside class="sidebar card">
        <div class="sidebar-head">
          <div>
            <p class="sidebar-eyebrow">AI Coach</p>
            <h2>最近对话</h2>
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
          <!-- <button v-if="messages.length" type="button" class="btn btn-secondary" @click="newChat">
            新建对话
          </button> -->
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
                <!-- 显示思考过程（仅AI消息） -->
                <div v-if="message.role === 'assistant' && message.thinking" class="thinking-container">
                  <button 
                    type="button" 
                    class="thinking-toggle"
                    @click="message.isThinkingExpanded = !message.isThinkingExpanded"
                  >
                    <span class="thinking-icon">{{ message.isThinkingExpanded ? '▼' : '▶' }}</span>
                    <span class="thinking-label">🧠 教练的思考过程</span>
                  </button>
                  <div v-if="message.isThinkingExpanded" class="thinking-content">
                    <p v-for="(line, lineIndex) in message.thinking.split('\n')" 
                       :key="lineIndex"
                       class="thinking-line">
                      {{ line }}
                    </p>
                  </div>
                </div>

                <!-- 显示正常回复 -->
                <div v-if="message.content" class="message-text markdown-message" v-html="renderMarkdown(message.content)"></div>
                <p v-else-if="message.role === 'assistant' && loading" class="message-text loading">
                  <span class="loading-dots">●●●</span>
                </p>

                <div v-if="message.planCard" class="plan-card">
                  <div class="plan-card-head">
                    <div>
                      <p class="plan-tag">AI 生成计划</p>
                      <h3>{{ message.planCard.title }}</h3>
                      <p class="plan-subtitle">{{ message.planCard.subtitle }}</p>
                    </div>
                    <div class="plan-head-right">
                      <span class="plan-badge">1 个月</span>
                      <div class="plan-meta-icons">
                        <div class="meta-icon-item">
                          <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                          </svg>
                          <span>{{ message.planCard.weeklyDays }}天/周</span>
                        </div>
                        <div class="meta-icon-item">
                          <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
                          </svg>
                          <span>{{ message.planCard.duration }}分钟</span>
                        </div>
                        <div class="meta-icon-item">
                          <svg class="meta-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                          </svg>
                          <span>{{ message.planCard.intensity }}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="plan-summary-card">
                    <h4 class="summary-title">
                      <svg class="summary-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                      </svg>
                      计划概述
                    </h4>
                    <div class="summary-content">
                      <pre class="summary-text">{{ message.planCard.summary }}</pre>
                    </div>
                  </div>

                  <div class="plan-sections">
                    <div class="section-item">
                      <div class="section-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                      </div>
                      <div class="section-content">
                        <h5>周期安排</h5>
                        <p>1个月，分4个阶段，循序渐进</p>
                      </div>
                    </div>
                    <div class="section-item">
                      <div class="section-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                        </svg>
                      </div>
                      <div class="section-content">
                        <h5>训练结构</h5>
                        <p>每周{{ message.planCard.weeklyDays }}天，每次{{ message.planCard.duration }}分钟</p>
                      </div>
                    </div>
                    <div class="section-item">
                      <div class="section-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                      </div>
                      <div class="section-content">
                        <h5>适合人群</h5>
                        <p>{{ message.planCard.intensity }}强度，适合{{ message.planCard.subtitle.includes('减脂') ? '减脂塑形' : message.planCard.subtitle.includes('增肌') ? '增肌强化' : '健康提升' }}目标</p>
                      </div>
                    </div>
                  </div>

                  <div class="plan-actions">
                    <button type="button" class="btn btn-primary" @click="viewPlanDetails(message.planCard.planId)">
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                      查看详情
                    </button>
                    <div class="action-hint">点击查看完整训练计划和日历安排</div>
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
            <div class="markdown-message preview-markdown" v-html="renderMarkdown(previewPlan.content)"></div>
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

    <div v-if="showQuestionnaireModal" class="modal-mask" @click.self="closeQuestionnaireModal">
      <div class="modal-card questionnaire-modal">
        <button type="button" class="modal-close" @click="closeQuestionnaireModal">✕</button>
        
        <div class="questionnaire-header-modal">
          <div>
            <p class="coach-tag">AI 教练 · 卡卡</p>
            <h2>{{ currentQuestionnaireQuestion.title }}</h2>
            <p class="modal-copy">{{ currentQuestionnaireQuestion.subtitle }}</p>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${((questionnaireStepIndex + 1) / questionnaireQuestions.length) * 100}%` }"></div>
          </div>
        </div>

        <div class="questionnaire-content">
          <div class="options-grid">
            <button
              v-for="option in currentQuestionnaireQuestion.options"
              :key="option.value"
              class="option-card"
              :class="{ selected: currentQuestionnaireQuestion.answer === option.value }"
              @click="selectQuestionnaireOption(option.value)"
            >
              <span>{{ option.label }}</span>
            </button>
          </div>

          <div v-if="currentQuestionnaireQuestion.key === 'injury' && currentQuestionnaireQuestion.answer === 'other'" class="form-field">
            <label for="injury-detail-modal">请输入具体伤病情况</label>
            <textarea
              id="injury-detail-modal"
              v-model.trim="questionnaireData.injury_detail"
              rows="3"
              placeholder="例如：膝盖疼痛、腰部不适、肩部活动受限"
            />
          </div>
        </div>

        <div class="modal-actions">
          <button 
            type="button" 
            class="btn btn-secondary" 
            :disabled="questionnaireStepIndex === 0 || loading" 
            @click="prevQuestionnaireStep"
          >
            上一步
          </button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="!questionnaireCanProceed || loading"
            @click="nextQuestionnaireStep"
          >
            {{ questionnaireStepIndex === questionnaireQuestions.length - 1 ? (loading ? '正在生成...' : '生成计划') : '下一步' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
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

const showQuestionnaireModal = ref(false)
const questionnaireStepIndex = ref(0)
const questionnaireData = ref({
  goal: '',
  method: '',
  weekly_days: '',
  daily_duration: '',
  intensity: '',
  injury: '',
  injury_detail: ''
})

const questionnaireQuestions = [
  {
    key: 'goal',
    title: '你的训练目标是什么？',
    subtitle: '选择一个最符合你当前需求的目标',
    options: [
      { label: '全身减脂减重', value: '全身减脂减重' },
      { label: '局部塑形紧致', value: '局部塑形紧致' },
      { label: '增肌与线条提升', value: '增肌与线条提升' },
      { label: '改善体态与核心', value: '改善体态与核心' },
      { label: '保持身体健康', value: '保持身体健康' }
    ]
  },
  {
    key: 'method',
    title: '你更想采用哪种训练方式？',
    subtitle: '选择一个你最愿意坚持的主要训练方式',
    options: [
      { label: '户外跑步', value: '户外跑步' },
      { label: '燃脂 HIIT', value: '燃脂 HIIT' },
      { label: '跳绳', value: '跳绳' },
      { label: '健身操', value: '健身操' },
      { label: '瑜伽', value: '瑜伽' },
      { label: '舞蹈有氧', value: '舞蹈有氧' },
      { label: '椭圆机', value: '椭圆机' },
      { label: '跑步机', value: '跑步机' },
      { label: '室内走路', value: '室内走路' },
      { label: '动感单车', value: '动感单车' },
      { label: '划船机', value: '划船机' }
    ]
  },
  {
    key: 'weekly_days',
    title: '你每周能训练几天？',
    subtitle: '系统会根据这个频率安排一个月训练日程',
    options: [1, 2, 3, 4, 5, 6, 7].map((value) => ({
      label: `每周 ${value} 天`,
      value: String(value)
    }))
  },
  {
    key: 'daily_duration',
    title: '你每天能训练多长时间？',
    subtitle: '请选择一个你更容易长期坚持的时长',
    options: [10, 20, 30, 40, 60].map((value) => ({
      label: `${value} 分钟左右`,
      value: String(value)
    }))
  },
  {
    key: 'intensity',
    title: '你能接受的训练强度是？',
    subtitle: 'AI 会根据强度调整动作难度和恢复安排',
    options: [
      { label: 'K1 零基础', value: 'K1 零基础' },
      { label: 'K2-K3 中低强度', value: 'K2-K3 中低强度' },
      { label: 'K3-K4 中高强度', value: 'K3-K4 中高强度' },
      { label: 'K4-K5 高强度', value: 'K4-K5 高强度' }
    ]
  },
  {
    key: 'injury',
    title: '你是否存在伤病困扰？',
    subtitle: '如有不适，AI 会自动规避高风险动作',
    options: [
      { label: '不存在伤病困扰', value: '无伤病困扰' },
      { label: '膝盖', value: '膝盖' },
      { label: '腰部', value: '腰部' },
      { label: '肩部', value: '肩部' },
      { label: '手腕', value: '手腕' },
      { label: '其他情况', value: 'other' }
    ]
  }
]

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

// 清理Markdown格式符号
const removeMarkdownFormat = (text = '') => {
  if (!text || typeof text !== 'string') return text

  // 处理HTML实体
  let cleaned = text
    .replace(/&middot;|&bull;|&sdot;/g, '') // HTML项目符号
    .replace(/&nbsp;/g, ' ')              // 非换行空格
    .replace(/&[a-z]+;/g, '')             // 其他简单HTML实体

  // 处理Markdown表格：移除表格分隔符和表头分隔线，将表格转换为更易读的格式
  const lines = cleaned.split('\n')
  const processedLines = []
  let inTable = false
  let tableHeaders = []
  let tableRows = []

  for (let line of lines) {
    // 检测表格行：包含 | 且不是代码块
    if (line.includes('|') && !line.startsWith('    ') && !line.startsWith('\t')) {
      const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell !== '')

      // 检测表头分隔线（只包含 - 和 |）
      const isHeaderSeparator = /^[\s|]*[-:| ]+[\s|]*$/.test(line)

      if (!inTable) {
        inTable = true
        tableHeaders = cells
        tableRows = []
      } else if (isHeaderSeparator) {
        // 跳过表头分隔线
        continue
      } else {
        tableRows.push(cells)
      }

      // 如果这一行处理完了，继续下一行
      continue
    } else if (inTable) {
      // 表格结束，将表格转换为更易读的格式
      if (tableRows.length > 0) {
        // 简单格式：每行作为文本
        for (let row of tableRows) {
          let rowText = ''
          for (let i = 0; i < Math.min(tableHeaders.length, row.length); i++) {
            rowText += `${tableHeaders[i]}: ${row[i]}  `
          }
          processedLines.push(rowText.trim())
        }
      }
      inTable = false
      tableHeaders = []
      tableRows = []
    }

    // 非表格行，直接添加
    if (!inTable) {
      processedLines.push(line)
    }
  }

  // 处理最后可能剩余的表格
  if (inTable && tableRows.length > 0) {
    for (let row of tableRows) {
      let rowText = ''
      for (let i = 0; i < Math.min(tableHeaders.length, row.length); i++) {
        rowText += `${tableHeaders[i]}: ${row[i]}  `
      }
      processedLines.push(rowText.trim())
    }
  }

  cleaned = processedLines.join('\n')

  // 移除常见的Markdown格式符号
  cleaned = cleaned
    .replace(/\*\*(.*?)\*\*/g, '$1')      // 粗体 **text**
    .replace(/\*(.*?)\*/g, '$1')          // 斜体 *text*
    .replace(/__(.*?)__/g, '$1')          // 粗体 __text__
    .replace(/_(.*?)_/g, '$1')            // 斜体 _text_
    .replace(/~~(.*?)~~/g, '$1')          // 删除线 ~~text~~
    .replace(/`(.*?)`/g, '$1')            // 行内代码 `text`
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')   // 链接 [text](url)
    .replace(/^#+\s*/gm, '')              // 标题 # text
    .replace(/^-\s*/gm, '')               // 无序列表 - text
    .replace(/^\d+\.\s*/gm, '')           // 有序列表 1. text
    .replace(/^\s*[-*+]\s*/gm, '')        // 各种列表符号
    .replace(/^>\s*/gm, '')               // 引用块 > text
    .replace(/<br\s*\/?>/g, '\n')         // HTML换行 <br> 替换为换行
    .replace(/[-=*_]{3,}/g, '')           // 分隔线 --- === *** ___
    // 清理常见的Unicode符号（复选框、警告、项目符号等）
    .replace(/[✅❌⚠️🔹🗓️🌟📌💡🌿🛑📊🎯🌱💪😊📄📝🔍💬📋🎯🏥💡🚫✨🌞💦🏃‍♀️🏃‍♂️🧘‍♀️🧘‍♂️]/gu, '')
    .replace(/[▪•·∙◦●○◆◇■□▢▣▲△▶▷▼▽➤➢➔→]/g, '') // 各种项目符号
    .replace(/[·•]/g, '')                 // 中文常用的项目符号
    .replace(/[ 　]/g, ' ')               // 全角空格和中文空格
    .replace(/\|\s*/g, ' ')               // 表格分隔符 | 替换为空格（处理残留的）
    .replace(/\s*\|\s*/g, ' ')            // 表格分隔符 | 替换为空格（带空格的）
    .replace(/\*\*|__/g, '')               // 移除孤立的粗体标记
    .replace(/(^|\s)[*_](\s|$)/g, '$1$2')   // 移除前后有空格的单个*或_
    .replace(/\n{3,}/g, '\n\n')           // 多个换行符减少为两个
    .replace(/\s{2,}/g, ' ')              // 多个空格合并为一个
    .replace(/^\s+|\s+$/g, '')            // 去除首尾空格
    .trim()

  return cleaned
}

const escapeHtml = (text = '') =>
  String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const formatInlineMarkdown = (text = '') =>
  escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')

const renderMarkdown = (content = '') => {
  const lines = String(content || '').replace(/\r\n/g, '\n').split('\n')
  const html = []
  let inList = false
  let inParagraph = false

  const closeList = () => {
    if (inList) {
      html.push('</ul>')
      inList = false
    }
  }

  const closeParagraph = () => {
    if (inParagraph) {
      html.push('</p>')
      inParagraph = false
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()

    if (!line) {
      closeList()
      closeParagraph()
      continue
    }

    const headingMatch = line.match(/^(#{1,4})\s+(.+)$/)
    if (headingMatch) {
      closeList()
      closeParagraph()
      const level = Math.min(4, headingMatch[1].length)
      html.push(`<h${level}>${formatInlineMarkdown(headingMatch[2].trim())}</h${level}>`)
      continue
    }

    if (/^[-*]\s+/.test(line)) {
      closeParagraph()
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${formatInlineMarkdown(line.replace(/^[-*]\s+/, ''))}</li>`)
      continue
    }

    if (!inParagraph) {
      closeList()
      html.push('<p>')
      inParagraph = true
    } else {
      html.push('<br>')
    }

    html.push(formatInlineMarkdown(line))
  }

  closeList()
  closeParagraph()

  return html.join('')
}

const normalizeMessage = (message = {}) => ({
  role: message.role || 'assistant',
  content: message.content || '',
  thinking: removeMarkdownFormat(message.thinking || ''), // 清理思考过程（总是AI生成）
  isThinkingExpanded: message.isThinkingExpanded !== undefined ? message.isThinkingExpanded : false, // 思考过程是否展开
  timestamp: message.timestamp ? new Date(message.timestamp) : new Date(),
  planCard: message.planCard || null,
  planQuestionnaire: Boolean(message.planQuestionnaire)
})

const normalizeChatHistory = (history = []) =>
  history.map((item) => {
    // 确保conversation字段存在
    let conversation = []
    
    if (Array.isArray(item.conversation)) {
      conversation = item.conversation.map(normalizeMessage)
    } else if (item.question && item.answer) {
      // 如果没有conversation但有question和answer，自动从中构造对话
      conversation = [
        normalizeMessage({ 
          role: 'user', 
          content: item.question, 
          timestamp: item.timestamp 
        }),
        normalizeMessage({ 
          role: 'assistant', 
          content: item.answer,
          thinking: item.thinking || '', // 添加thinking
          timestamp: item.timestamp 
        })
      ]
    }
    
    return {
      ...item,
      timestamp: item.timestamp ? new Date(item.timestamp) : new Date(),
      conversation
    }
  })

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
  const content = savedPlan?.content || ''

  // 提取结构化的计划摘要
  const extractStructuredSummary = (text) => {
    if (!text) return '计划内容待生成。'

    // 清理Markdown格式
    const cleaned = removeMarkdownFormat(text)
    const lines = cleaned.split('\n').map(line => line.trim()).filter(line => line.length > 0)

    // 查找阶段标题（包含"第X周"、"阶段"等关键词）
    const phaseLines = lines.filter(line =>
      line.includes('第') && line.includes('周') ||
      line.includes('阶段') ||
      /^(第一周|第二周|第三周|第四周)/.test(line)
    )

    // 查找训练日内容（包含"训练日"、"Day"、"训练主题"等）
    const trainingDayLines = lines.filter(line =>
      line.includes('训练日') ||
      line.includes('训练主题') ||
      line.includes('训练时长') ||
      line.includes('训练内容')
    )

    // 构建结构化摘要
    let summary = ''

    if (phaseLines.length > 0) {
      // 添加阶段概述
      summary += `计划包含 ${phaseLines.length} 个训练阶段：\n`
      phaseLines.slice(0, 3).forEach((phase) => {
        summary += `• ${phase}\n`
      })
      if (phaseLines.length > 3) {
        summary += `• ... 等 ${phaseLines.length} 个阶段\n`
      }
    }

    if (trainingDayLines.length > 0) {
      summary += `\n包含 ${Math.min(trainingDayLines.length, 5)} 个训练日安排，涵盖：\n`
      // 提取训练主题关键词
      const themes = trainingDayLines.slice(0, 3).map(line => {
        // 尝试提取主题
        if (line.includes('训练主题')) {
          const match = line.match(/训练主题[:：]\s*(.+)/)
          return match ? match[1].slice(0, 20) : line.slice(0, 30)
        }
        return line.slice(0, 30)
      })
      themes.forEach(theme => {
        summary += `• ${theme}${theme.length >= 30 ? '...' : ''}\n`
      })
    }

    // 如果未提取到结构，使用前3行作为摘要
    if (!summary && lines.length > 0) {
      summary = lines.slice(0, 3).join('\n')
      if (summary.length > 120) {
        summary = summary.slice(0, 120) + '...'
      }
    }

    // 如果仍然为空，使用默认摘要
    if (!summary) {
      summary = '已为您生成个性化的训练计划，包含详细的阶段划分和每日训练安排。'
    }

    return summary.trim()
  }

  const summary = extractStructuredSummary(content)

  return normalizeMessage({
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    planCard: {
      planId: savedPlan.id,
      title: removeMarkdownFormat(savedPlan.title || ''),
      subtitle: removeMarkdownFormat(questionnaire.goal || 'AI generated plan'),
      weeklyDays: questionnaire.weekly_days || 'TBD',
      duration: questionnaire.daily_duration || 'TBD',
      intensity: questionnaire.intensity || 'TBD',
      summary: summary
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

// 检测内容是否为训练计划
const isTrainingPlanContent = (content = '') => {
  const cleanedText = removeMarkdownFormat(String(content)).toLowerCase()
  const trainingPlanKeywords = [
    '训练计划', '训练日', '每周', '第一周', '第二周', '第三周', '第四周',
    '训练内容', '训练目标', '恢复建议', '训练时长', '训练强度'
  ]
  return trainingPlanKeywords.some(keyword => cleanedText.includes(keyword.toLowerCase()))
}

// 从训练计划内容中提取简要总结
const extractTrainingSummary = (content = '') => {
  const cleanedText = removeMarkdownFormat(String(content)).trim()
  if (!cleanedText) return '已为您生成训练计划。'

  // 尝试提取第一句（到第一个句号、感叹号或问号为止）
  const firstSentenceMatch = cleanedText.match(/^[^。！？]+[。！？]/)
  if (firstSentenceMatch) {
    const firstSentence = firstSentenceMatch[0]
    // 如果第一句包含训练计划关键词，直接返回
    if (firstSentence.includes('训练计划') || firstSentence.includes('训练安排')) {
      return firstSentence
    }
    // 如果第一句太长（超过50字符），截断
    if (firstSentence.length > 50) {
      return firstSentence.slice(0, 50) + '...'
    }
    return firstSentence
  }

  // 如果没有找到完整的句子，检查是否包含训练计划相关内容
  if (cleanedText.includes('训练计划') || cleanedText.includes('训练安排') || isTrainingPlanContent(cleanedText)) {
    // 返回简短的默认消息
    return '已为您生成个性化的训练计划，请查看下方的训练计划卡片获取详细信息。'
  }

  // 否则取前80个字符作为简要总结
  return cleanedText.length > 80 ? cleanedText.slice(0, 80) + '...' : cleanedText
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
    // 添加助手消息占位符
    const assistantMessageIndex = messages.value.length
    messages.value.push(normalizeMessage({
      role: 'assistant',
      content: '',
      thinking: '',
      timestamp: new Date()
    }))
    
    // 流式接收思考过程和答案
    let thinkingContent = ''
    let answerContent = ''

    await api.queryStream(
      question,
      (chunk, type) => {
        if (type === 'thinking') {
          // 如果是第一次收到思考内容，自动展开思考过程
          if (thinkingContent === '') {
            messages.value[assistantMessageIndex].isThinkingExpanded = true
          }
          thinkingContent += chunk
          messages.value[assistantMessageIndex].thinking = removeMarkdownFormat(thinkingContent)
        } else if (type === 'answer') {
          answerContent += chunk
          messages.value[assistantMessageIndex].content = answerContent
        }
        scrollToBottom()
      },
      async (type) => {
        if (type !== 'answer') return
        // 流式完成
        const assistantMessage = normalizeMessage({
          role: 'assistant',
          content: answerContent,
          thinking: thinkingContent,
          isThinkingExpanded: messages.value[assistantMessageIndex]?.isThinkingExpanded || false,
          timestamp: new Date()
        })
        
        messages.value[assistantMessageIndex] = assistantMessage
        updateCurrentConversation(question, assistantMessage)
        
        // 如果存在planContext或者内容看起来像训练计划，则生成卡片
        if (planContext || isTrainingPlanContent(answerContent)) {
          // 异步处理plan生成，不阻塞消息流
          generatePlanAsync(assistantMessage, planContext || null)
        }
      },
      (error) => {
        // 移除占位符
        messages.value.splice(assistantMessageIndex, 1)
        console.error('发送消息失败', error)
        messages.value.push(
          normalizeMessage({
            role: 'assistant',
            content: '消息发送失败，请稍后重试。',
            timestamp: new Date()
          })
        )
      }
    )

    await scrollToBottom()
  } catch (error) {
    console.error('发送消息异常', error)
  } finally {
    loading.value = false
  }
}

// 异步处理plan生成，不阻塞消息流
const generatePlanAsync = async (message, planContext) => {
  try {
    const savedPlan = await createPlanFromAiResponse(message, planContext)
    const planCardMessage = createPlanCardMessage(savedPlan, planContext)

    // 创建更新后的消息对象 - 用简短总结替换完整训练计划文本，并添加卡片
    const updatedMessage = {
      ...message,
      content: extractTrainingSummary(message.content),
      planCard: planCardMessage.planCard
    }

    // 更新messages数组中的对应消息（确保响应式更新）
    const index = messages.value.findIndex((msg) => msg.timestamp?.getTime?.() === message.timestamp?.getTime?.())
    if (index !== -1) {
      // 使用splice确保响应式更新
      messages.value.splice(index, 1, updatedMessage)
    }

    pendingPlanContext.value = null
    sessionStorage.removeItem(PENDING_PROMPT_KEY)

    // 更新对话历史中的这条消息
    if (currentChat.value !== null && chatHistory.value[currentChat.value]) {
      const conversation = chatHistory.value[currentChat.value].conversation || []
      const idx = conversation.findIndex((item) => item.timestamp?.getTime?.() === message.timestamp?.getTime?.())
      if (idx >= 0) {
        conversation[idx] = updatedMessage
      }
    }
  } catch (error) {
    console.error('训练计划生成失败:', error)
  }
}

const generatePlan = async (message) => {
  try {
    const savedPlan = await createPlanFromAiResponse(message)
    const planCardMessage = createPlanCardMessage(savedPlan)

    // 创建更新后的消息对象 - 用简短总结替换完整训练计划文本，并添加卡片
    const updatedMessage = {
      ...message,
      content: extractTrainingSummary(message.content),
      planCard: planCardMessage.planCard
    }

    // 更新messages数组中的对应消息（确保响应式更新）
    const index = messages.value.findIndex((msg) => msg.timestamp?.getTime?.() === message.timestamp?.getTime?.())
    if (index !== -1) {
      messages.value.splice(index, 1, updatedMessage)
    }

    if (currentChat.value !== null && chatHistory.value[currentChat.value]) {
      const conversation = chatHistory.value[currentChat.value].conversation || []
      const target = conversation.find((item) => item.timestamp?.getTime?.() === message.timestamp?.getTime?.())
      if (target) {
        target.content = updatedMessage.content
        target.planCard = updatedMessage.planCard
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
    showQuestionnaireModal.value = true
    questionnaireStepIndex.value = 0
    return
  }

  inputMessage.value = action
  nextTick(() => inputRef.value?.focus())
}

const currentQuestionnaireQuestion = computed(() => {
  const question = questionnaireQuestions[questionnaireStepIndex.value]
  return {
    ...question,
    answer: questionnaireData.value[question.key]
  }
})

const questionnaireCanProceed = computed(() => {
  if (!currentQuestionnaireQuestion.value.answer) return false
  if (currentQuestionnaireQuestion.value.key === 'injury' && currentQuestionnaireQuestion.value.answer === 'other') {
    return Boolean(questionnaireData.value.injury_detail)
  }
  return true
})

const selectQuestionnaireOption = (value) => {
  questionnaireData.value[currentQuestionnaireQuestion.value.key] = value
}

const prevQuestionnaireStep = () => {
  if (questionnaireStepIndex.value > 0) questionnaireStepIndex.value -= 1
}

const buildTrainingPrompt = () => {
  const injuryText =
    questionnaireData.value.injury === 'other'
      ? `其他伤病：${questionnaireData.value.injury_detail}`
      : questionnaireData.value.injury

  return [
    '请你扮演专业 AI 运动教练，根据以下用户问卷信息生成一个 1 个月训练计划。',
    '输出格式要求：',
    '1. 先输出“计划标题”和“计划概述”两个部分。',
    '2. 训练主体必须按周展开，尽量细化到完整 4 周；每周下再按训练日展开。',
    '3. 每个训练日都必须明确写出：训练主题、建议时长、训练重点、恢复建议。',
    '4. 如果用户有伤病困扰，必须主动规避高风险动作，并在对应训练日中写出替代方案或调整建议。',
    '5. 保持结构化输出，标题清晰，便于后续按卡片和训练日详情解析。',
    '6. 不要只给原则性建议，必须给出可执行的每日安排。',
    '',
    '请严格遵循下面的标准 Markdown 输出骨架：',
    '# 计划标题',
    '',
    '## 计划概述',
    '这里写目标、周期、每周频次、强度和注意事项。',
    '',
    '## 第1周',
    '',
    '### 训练日1',
    '- 训练主题：',
    '- 建议时长：',
    '- 训练重点：',
    '- 恢复建议：',
    '- 替代方案：如无伤病风险不用写',
    '',
    '### 训练日2',
    '- 训练主题：',
    '- 建议时长：',
    '- 训练重点：',
    '- 恢复建议：',
    '- 替代方案：如无伤病风险不用写',
    '',
    '## 第2周',
    '...',
    '',
    '用户信息：',
    `- 训练目标：${questionnaireData.value.goal}`,
    `- 偏好训练方式：${questionnaireData.value.method}`,
    `- 每周训练天数：${questionnaireData.value.weekly_days} 天`,
    `- 单次训练时长：${questionnaireData.value.daily_duration} 分钟`,
    `- 可接受强度：${questionnaireData.value.intensity}`,
    `- 伤病情况：${injuryText}`
  ].join('\n')
}

const nextQuestionnaireStep = async () => {
  if (!questionnaireCanProceed.value || loading.value) return

  if (questionnaireStepIndex.value < questionnaireQuestions.length - 1) {
    questionnaireStepIndex.value += 1
    return
  }

  // 生成训练计划
  const prompt = buildTrainingPrompt()
  pendingPlanContext.value = {
    prompt,
    questionnaire: { ...questionnaireData.value },
    createdAt: new Date().toISOString()
  }

  // 关闭问卷弹窗
  showQuestionnaireModal.value = false

  // 发送消息生成计划
  await sendMessage(prompt, { planContext: pendingPlanContext.value })
}

const closeQuestionnaireModal = () => {
  showQuestionnaireModal.value = false
  questionnaireStepIndex.value = 0
  questionnaireData.value = {
    goal: '',
    method: '',
    weekly_days: '',
    daily_duration: '',
    intensity: '',
    injury: '',
    injury_detail: ''
  }
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
  background: var(--color-bg);
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
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 28px;
  box-shadow: 0 24px 60px var(--color-shadow);
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
  color: var(--color-accent);
}

.sidebar h2,
.main-head h1,
.plan-card h3,
.plan-modal h2 {
  margin: 0;
  color: var(--color-text-primary);
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
  background: var(--color-bg);
  color: var(--color-text-primary);
}

.icon-btn.danger {
  background: rgba(239, 68, 68, 0.12);
  color: #0056b3;
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
  background: var(--color-bg);
  color: var(--color-text-primary);
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
  color: #0056b3;
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
  color: var(--color-text-secondary);
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
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-hover));
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
  background: var(--color-bg);
  color: var(--color-text-primary);
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
  background: linear-gradient(135deg, #0d2b50, var(--color-accent));
  color: #fff;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-bg);
  color: var(--color-text-primary);
  display: grid;
  place-items: center;
  font-weight: 800;
}

.message-card {
  background: var(--color-bg);
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

.markdown-message {
  white-space: normal;
}

.markdown-message :deep(h1),
.markdown-message :deep(h2),
.markdown-message :deep(h3),
.markdown-message :deep(h4) {
  margin: 0 0 12px;
  line-height: 1.3;
  color: var(--color-text-primary);
}

.markdown-message :deep(h1) {
  font-size: 28px;
}

.markdown-message :deep(h2) {
  font-size: 22px;
  margin-top: 22px;
}

.markdown-message :deep(h3) {
  font-size: 18px;
  margin-top: 18px;
}

.markdown-message :deep(h4) {
  font-size: 15px;
  margin-top: 12px;
}

.markdown-message :deep(p) {
  margin: 0 0 12px;
}

.markdown-message :deep(ul) {
  margin: 0 0 12px;
  padding-left: 20px;
}

.markdown-message :deep(li) {
  margin: 0 0 8px;
}

.markdown-message :deep(code) {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(0, 113, 227, 0.08);
  font-size: 13px;
}

.inline-plan-btn {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(52, 199, 89, 0.14);
  color: var(--color-accent);
  font-weight: 700;
}

.plan-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.plan-tag {
  margin: 0 0 8px;
  color: var(--color-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.plan-badge {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(52, 199, 89, 0.12);
  color: var(--color-accent);
  font-weight: 700;
}

.plan-head-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.plan-meta-icons {
  display: flex;
  gap: 16px;
}

.meta-icon-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.meta-icon {
  width: 16px;
  height: 16px;
  stroke-width: 2;
  color: var(--color-accent);
}

.plan-summary-card {
  background: rgba(0, 113, 227, 0.04);
  border-radius: 18px;
  padding: 18px;
  border: 1px solid rgba(0, 113, 227, 0.12);
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 12px;
  color: var(--color-text-primary);
  font-size: 15px;
  font-weight: 700;
}

.summary-icon {
  width: 18px;
  height: 18px;
  stroke-width: 1.8;
  color: var(--color-accent);
}

.summary-content {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 14px;
}

.summary-text {
  margin: 0;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: var(--color-text-primary);
}

.plan-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: var(--color-bg);
  border-radius: 16px;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: var(--color-accent);
  flex-shrink: 0;
  margin-top: 2px;
}

.section-icon svg {
  width: 100%;
  height: 100%;
  stroke-width: 1.8;
}

.section-content h5 {
  margin: 0 0 4px;
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: 700;
}

.section-content p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.action-hint {
  margin-top: 8px;
  color: var(--color-text-secondary);
  font-size: 12px;
  text-align: center;
  width: 100%;
}

.plan-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.btn-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  vertical-align: middle;
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
  background: var(--color-bg);
  font: inherit;
  color: var(--color-text-primary);
}

.send-btn,
.btn {
  padding: 12px 18px;
  border-radius: 16px;
  font-weight: 700;
}

.btn-primary,
.send-btn {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-hover));
  color: #fff;
  box-shadow: 0 14px 28px rgba(0, 113, 227, 0.22);
}

.btn-secondary {
  background: var(--color-bg);
  color: var(--color-text-primary);
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
  background: linear-gradient(180deg, var(--color-surface), var(--color-bg));
  box-shadow: 0 28px 70px rgba(12, 24, 20, 0.22);
}

.plan-modal {
  padding: 32px;
}

.questionnaire-modal {
  padding: 32px;
  display: flex;
  flex-direction: column;
}

.questionnaire-header-modal {
  margin-bottom: 28px;
}

.questionnaire-header-modal .coach-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  background: rgba(97, 82, 223, 0.08);
  color: var(--color-accent);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 14px;
}

.questionnaire-header-modal h2 {
  margin: 0 0 10px;
  font-size: 28px;
  line-height: 1.3;
  color: var(--color-text-primary);
}

.questionnaire-header-modal .modal-copy {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 15px;
}

.progress-bar {
  margin-top: 20px;
  height: 4px;
  background: var(--color-bg);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent), var(--color-accent-hover));
  transition: width 0.3s ease;
}

.questionnaire-content {
  flex: 1;
  margin-bottom: 24px;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.option-card {
  border: 1px solid var(--color-bg);
  background: #fff;
  border-radius: 18px;
  min-height: 80px;
  padding: 16px 14px;
  text-align: center;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  cursor: pointer;
}

.option-card:hover {
  transform: translateY(-2px);
  border-color: rgba(54, 209, 149, 0.5);
  box-shadow: 0 10px 24px rgba(52, 199, 137, 0.12);
}

.option-card.selected {
  border-color: var(--color-accent);
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.12), rgba(0, 113, 227, 0.04));
  color: var(--color-accent);
  box-shadow: 0 10px 24px rgba(0, 113, 227, 0.12);
}

.form-field {
  margin-top: 20px;
}

.form-field label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.form-field textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-bg);
  border-radius: 16px;
  background: var(--color-bg);
  font: inherit;
  color: var(--color-text-primary);
  resize: vertical;
}

.form-field textarea:focus {
  outline: none;
  border-color: rgba(52, 199, 89, 0.5);
  background: #fff;
}

.modal-close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--color-bg);
  color: var(--color-text-primary);
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

.preview-markdown {
  color: var(--color-text-primary);
}

.weekday-grid {
  margin-top: 14px;
}

.weekday-chip.active {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-hover));
  color: #fff;
}

.modal-actions {
  margin-top: 22px;
  justify-content: flex-end;
}

/* 思考过程样式 */
.thinking-container {
  margin-bottom: 14px;
  padding: 14px;
  background: linear-gradient(135deg, rgba(97, 82, 223, 0.08), rgba(52, 199, 89, 0.04));
  border-radius: 16px;
  border-left: 3px solid var(--color-accent);
}

.thinking-toggle {
  width: 100%;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-accent);
  font-weight: 600;
  font-size: 14px;
  transition: color 0.2s ease;
}

.thinking-toggle:hover {
  color: var(--color-accent);
}

.thinking-icon {
  display: inline-block;
  transition: transform 0.2s ease;
  font-size: 12px;
}

.thinking-label {
  flex: 1;
  text-align: left;
}

.thinking-content {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(97, 82, 223, 0.2);
  font-size: 13px;
  color: var(--color-accent);
  line-height: 1.6;
}

.thinking-line {
  margin: 6px 0;
  white-space: pre-wrap;
}

/* 加载状态样式 */
.message-text.loading {
  font-style: italic;
  color: #999;
}

.loading-dots {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
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
