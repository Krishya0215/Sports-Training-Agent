<template>
  <div class="memory-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <div>
          <h1 class="page-title">记忆系统</h1>
          <p class="page-subtitle">查看和管理多层次记忆状态</p>
        </div>
        <button class="btn btn-secondary" @click="refreshMemory">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M15 3V7H11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3 15V11H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14.5 6.5C13.5 4.5 11.5 3 9 3C5.5 3 2.5 6 2.5 9.5M3.5 11.5C4.5 13.5 6.5 15 9 15C12.5 15 15.5 12 15.5 8.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          刷新
        </button>
      </div>
      
      <div class="memory-grid">
        <div class="memory-card card">
          <div class="memory-header">
            <div class="memory-icon" style="background: rgba(0, 113, 227, 0.1); color: #0071e3;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <h3 class="memory-title">工作记忆</h3>
              <p class="memory-desc">当前对话上下文</p>
            </div>
          </div>
          <div class="memory-stats">
            <div class="stat-item">
              <span class="stat-label">记忆条目</span>
              <span class="stat-value">{{ memorySummary.working_memory_size || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">容量限制</span>
              <span class="stat-value">5 轮</span>
            </div>
          </div>
          <div class="memory-progress">
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: `${(memorySummary.working_memory_size / 5) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <div class="memory-card card">
          <div class="memory-header">
            <div class="memory-icon" style="background: rgba(0, 113, 227, 0.15); color: #0071e3;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div>
              <h3 class="memory-title">情景记忆</h3>
              <p class="memory-desc">问答历史记录</p>
            </div>
          </div>
          <div class="memory-stats">
            <div class="stat-item">
              <span class="stat-label">历史记录</span>
              <span class="stat-value">{{ memorySummary.episodic_memory_size || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">状态</span>
              <span class="stat-value">{{ memorySummary.episodic_memory_size > 0 ? '活跃' : '空闲' }}</span>
            </div>
          </div>
        </div>
        
        <div class="memory-card card">
          <div class="memory-header">
            <div class="memory-icon" style="background: rgba(0, 113, 227, 0.1); color: #0071e3;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              </svg>
            </div>
            <div>
              <h3 class="memory-title">语义记忆</h3>
              <p class="memory-desc">概念知识存储</p>
            </div>
          </div>
          <div class="memory-stats">
            <div class="stat-item">
              <span class="stat-label">概念数量</span>
              <span class="stat-value">{{ memorySummary.semantic_concepts || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">状态</span>
              <span class="stat-value">{{ memorySummary.semantic_concepts > 0 ? '活跃' : '空闲' }}</span>
            </div>
          </div>
        </div>
        
        <div class="memory-card card">
          <div class="memory-header">
            <div class="memory-icon" style="background: rgba(0, 113, 227, 0.2); color: #0071e3;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M3 9H21M9 21V9" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div>
              <h3 class="memory-title">感知记忆</h3>
              <p class="memory-desc">文档特征信息</p>
            </div>
          </div>
          <div class="memory-stats">
            <div class="stat-item">
              <span class="stat-label">文档数量</span>
              <span class="stat-value">{{ memorySummary.perceptual_documents || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">状态</span>
              <span class="stat-value">{{ memorySummary.perceptual_documents > 0 ? '活跃' : '空闲' }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="recent-activity card">
        <h2 class="section-title">最近活动</h2>
        <div class="activity-list">
          <div 
            v-for="(activity, index) in recentActivities" 
            :key="index"
            class="activity-item"
          >
            <div class="activity-icon">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <circle cx="8" cy="8" r="6"/>
              </svg>
            </div>
            <div class="activity-content">
              <div class="activity-text">{{ activity.text }}</div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const memorySummary = ref({
  working_memory_size: 0,
  episodic_memory_size: 0,
  semantic_concepts: 0,
  perceptual_documents: 0
})

const recentActivities = ref([
  { text: '用户查询：什么是有氧运动？', time: '2分钟前' },
  { text: '系统回答：有氧运动是指...', time: '2分钟前' },
  { text: '用户查询：如何进行力量训练？', time: '5分钟前' },
  { text: '加载知识库完成', time: '10分钟前' }
])

const refreshMemory = async () => {
  try {
    const [summary, dashboard] = await Promise.all([
      api.getMemorySummary(),
      api.getMemoryDashboard()
    ])
    memorySummary.value = summary
    recentActivities.value = (dashboard?.episodic_memory?.recent_events || []).map((event) => ({
      text: event.event_summary || event.question || '最近有新的记忆活动',
      time: event.event_time || event.created_at || ''
    }))
  } catch (error) {
    console.error('Failed to refresh memory:', error)
  }
}

onMounted(() => {
  refreshMemory()
})
</script>

<style scoped>
.memory-page {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 32px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  color: var(--color-text-secondary);
}

.memory-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.memory-card {
  padding: 24px;
}

.memory-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.memory-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.memory-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.memory-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.memory-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.memory-progress {
  margin-top: 16px;
}

.progress-bar {
  height: 6px;
  background: var(--color-bg);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-accent);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.recent-activity {
  padding: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 20px;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: var(--color-bg);
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 14px;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .memory-grid {
    grid-template-columns: 1fr;
  }
}
</style>
