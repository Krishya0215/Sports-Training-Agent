<template>
  <div class="knowledge-page">
    <Navbar />
    
    <div class="container">
      <div class="page-header">
        <div>
          <h1 class="page-title">知识库管理</h1>
          <p class="page-subtitle">管理和浏览运动训练知识文档</p>
        </div>
        <div class="btn-group">
          <button class="btn btn-primary" @click="loadKnowledge(false)" :disabled="loading">
            <svg v-if="!loading" width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M15 3V7H11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3 15V11H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14.5 6.5C13.5 4.5 11.5 3 9 3C5.5 3 2.5 6 2.5 9.5M3.5 11.5C4.5 13.5 6.5 15 9 15C12.5 15 15.5 12 15.5 8.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span v-if="loading" class="loading-spinner small"></span>
            {{ loading ? '加载中...' : '加载知识库' }}
          </button>
          <button class="btn btn-secondary" @click="loadKnowledge(true)" :disabled="loading" title="清除缓存并强制重新加载">
            <svg v-if="!loading" width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M3 3L15 15M15 3L3 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span v-if="loading" class="loading-spinner small"></span>
            {{ loading ? '加载中...' : '强制重载' }}
          </button>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-box card">
          <div class="stat-label">文档总数</div>
          <div class="stat-value">{{ stats.totalDocs }}</div>
        </div>
        <div class="stat-box card">
          <div class="stat-label">文本块数</div>
          <div class="stat-value">{{ stats.totalChunks }}</div>
        </div>
        <div class="stat-box card">
          <div class="stat-label">最后更新</div>
          <div class="stat-value">{{ stats.lastUpdate }}</div>
        </div>
      </div>
      
      <div class="documents-section">
        <div class="section-header">
          <h2>文档列表</h2>
          <div class="search-box">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
              <path d="M12 12L16 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="搜索文档..."
            />
          </div>
        </div>
        
        <div class="documents-grid">
          <div 
            v-for="doc in filteredDocuments" 
            :key="doc.id"
            class="document-card card"
          >
            <div class="doc-icon">
              <svg v-if="doc.type === 'pdf'" width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M20 2H8C6.89543 2 6 2.89543 6 4V28C6 29.1046 6.89543 30 8 30H24C25.1046 30 26 29.1046 26 28V8L20 2Z" stroke="currentColor" stroke-width="2"/>
                <path d="M20 2V8H26" stroke="currentColor" stroke-width="2"/>
              </svg>
              <svg v-else width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M20 2H8C6.89543 2 6 2.89543 6 4V28C6 29.1046 6.89543 30 8 30H24C25.1046 30 26 29.1046 26 28V8L20 2Z" stroke="currentColor" stroke-width="2"/>
                <path d="M20 2V8H26" stroke="currentColor" stroke-width="2"/>
                <path d="M10 14H22M10 18H22M10 22H18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="doc-info">
              <h3 class="doc-title">{{ doc.name }}</h3>
              <div class="doc-meta">
                <span class="doc-type">{{ doc.type.toUpperCase() }}</span>
                <span class="doc-size">{{ doc.size }}</span>
                <span class="doc-chunks">{{ doc.chunks }} 块</span>
              </div>
            </div>
            <button class="icon-btn">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <circle cx="9" cy="5" r="1" fill="currentColor"/>
                <circle cx="9" cy="9" r="1" fill="currentColor"/>
                <circle cx="9" cy="13" r="1" fill="currentColor"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const loading = ref(false)
const searchQuery = ref('')

const stats = ref({
  totalDocs: 0,
  totalChunks: 0,
  lastUpdate: '未知'
})

const documents = ref([
  {
    id: 1,
    name: '运动训练基础理论.pdf',
    type: 'pdf',
    size: '2.3 MB',
    chunks: 45,
    date: '2024-01-15'
  },
  {
    id: 2,
    name: 'sample_sports_training.md',
    type: 'md',
    size: '156 KB',
    chunks: 12,
    date: '2024-01-20'
  }
])

const filteredDocuments = computed(() => {
  if (!searchQuery.value) return documents.value
  return documents.value.filter(doc => 
    doc.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const loadKnowledge = async (forceReload = false) => {
  loading.value = true
  try {
    const result = await api.loadKnowledge(forceReload)
    const message = forceReload 
      ? `知识库强制重载成功！\n文档块数: ${result.document_count}`
      : `知识库加载成功！\n文档块数: ${result.document_count}`
    alert(message)
    await loadStats()
  } catch (error) {
    alert('知识库加载失败：' + error.message)
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const stats_data = await api.getKnowledgeStats()
    stats.value = {
      totalDocs: stats_data.total_documents || 0,
      totalChunks: stats_data.total_chunks || 0,
      lastUpdate: new Date(stats_data.last_update).toLocaleDateString('zh-CN')
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    // 如果新API不可用，尝试使用旧的记忆摘要API
    try {
      const summary = await api.getMemorySummary()
      stats.value = {
        totalDocs: summary.perceptual_documents || 0,
        totalChunks: 0,
        lastUpdate: new Date().toLocaleDateString('zh-CN')
      }
    } catch (fallbackError) {
      console.error('Fallback also failed:', fallbackError)
    }
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.knowledge-page {
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

.btn-group {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-bg);
  border-color: var(--color-accent);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.stat-box {
  padding: 24px;
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.documents-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  width: 300px;
}

.search-box svg {
  color: var(--color-text-secondary);
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 0;
  font-size: 14px;
  color: var(--color-text-primary);
}

.search-box input:focus {
  outline: none;
  box-shadow: none;
}

.documents-grid {
  display: grid;
  gap: 16px;
}

.document-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s ease;
}

.document-card:hover {
  transform: translateY(-2px);
}

.doc-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
  flex-shrink: 0;
}

.doc-info {
  flex: 1;
}

.doc-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 6px;
}

.doc-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.doc-type {
  padding: 2px 8px;
  background: var(--color-bg);
  border-radius: 4px;
  font-weight: 500;
}

.loading-spinner.small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
