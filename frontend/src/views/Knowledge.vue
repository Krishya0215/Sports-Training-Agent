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
          <button class="btn btn-primary" @click="showUploadModal = true">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M9 1V15M9 1L5 5M9 1L13 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 10C2 8.4087 2.63214 6.88258 3.75736 5.75736C4.88258 4.63214 6.4087 4 8 4H10C11.5913 4 13.1174 4.63214 14.2426 5.75736C15.3679 6.88258 16 8.4087 16 10V14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            上传文档
          </button>
          <button class="btn btn-secondary" @click="loadKnowledge(false)" :disabled="loading">
            <svg v-if="!loading" width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M15 3V7H11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3 15V11H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M14.5 6.5C13.5 4.5 11.5 3 9 3C5.5 3 2.5 6 2.5 9.5M3.5 11.5C4.5 13.5 6.5 15 9 15C12.5 15 15.5 12 15.5 8.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span v-if="loading" class="loading-spinner small"></span>
            {{ loading ? '加载中...' : '加载知识库' }}
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

        <div v-if="documentsLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载文档列表...</p>
        </div>

        <div v-else-if="filteredDocuments.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <path d="M40 4H16C13.7909 4 12 5.79086 12 8V56C12 58.2091 13.7909 60 16 60H48C50.2091 60 52 58.2091 52 56V16L40 4Z" stroke="currentColor" stroke-width="2"/>
            <path d="M40 4V16H52" stroke="currentColor" stroke-width="2"/>
          </svg>
          <p>暂无文档，点击"上传文档"添加知识库文件</p>
        </div>

        <div v-else class="documents-grid">
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
                <span class="doc-size">{{ doc.size_formatted }}</span>
                <span class="doc-chunks">{{ doc.chunks }} 块</span>
                <span class="doc-status" :class="{ active: doc.in_vector_db }">
                  {{ doc.in_vector_db ? '已加载' : '未加载' }}
                </span>
              </div>
            </div>
            <button class="icon-btn delete-btn" @click="confirmDelete(doc)" :disabled="deleting">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M3 6H15M5 6V14C5 15.1046 5.89543 16 7 16H11C12.1046 16 13 15.1046 13 14V6M8 6V4M10 6V4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传模态框 -->
    <div v-if="showUploadModal" class="modal-overlay" @click="closeUploadModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>上传文档</h3>
          <button class="icon-btn" @click="closeUploadModal">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M15 3L3 15M3 3L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div
            class="upload-area"
            :class="{ 'dragover': isDragover }"
            @dragover.prevent="isDragover = true"
            @dragleave.prevent="isDragover = false"
            @drop.prevent="handleDrop"
            @click="fileInput?.click()"
          >
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <path d="M24 4V38M24 4L14 14M24 4L34 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 26C4 21.5817 7.58172 18 12 18H36C40.4183 18 44 21.5817 44 26V30" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <p>点击或拖拽文件到此处上传</p>
            <p class="upload-hint">支持 PDF、Markdown、TXT 格式</p>
          </div>
          <input
            ref="fileInput"
            type="file"
            accept=".pdf,.md,.txt"
            @change="handleFileSelect"
            style="display: none"
          />
          <div v-if="selectedFile" class="selected-file">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
              <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span>{{ selectedFile.name }}</span>
            <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeUploadModal">取消</button>
          <button class="btn btn-primary" @click="uploadFile" :disabled="!selectedFile || uploading">
            {{ uploading ? '上传中...' : '上传' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 确认删除模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content modal-small" @click.stop>
        <div class="modal-body">
          <div class="delete-icon">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="20" stroke="currentColor" stroke-width="2"/>
              <path d="M16 16L32 32M32 16L16 32" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <h3>确认删除</h3>
          <p>确定要删除文档 <strong>{{ docToDelete?.name }}</strong> 吗？</p>
          <p class="warning-text">此操作将从知识库中移除该文档的所有内容，且无法恢复。</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeDeleteModal" :disabled="deleting">取消</button>
          <button class="btn btn-danger" @click="deleteDocument" :disabled="deleting">
            {{ deleting ? '删除中...' : '删除' }}
          </button>
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
const documentsLoading = ref(false)
const uploading = ref(false)
const deleting = ref(false)
const searchQuery = ref('')

const showUploadModal = ref(false)
const showDeleteModal = ref(false)
const isDragover = ref(false)
const selectedFile = ref(null)
const fileInput = ref(null)
const docToDelete = ref(null)

const stats = ref({
  totalDocs: 0,
  totalChunks: 0,
  lastUpdate: '未知'
})

const documents = ref([])

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
    await loadDocuments()
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
  }
}

const loadDocuments = async () => {
  documentsLoading.value = true
  try {
    const result = await api.getKnowledgeDocuments()
    documents.value = result.documents || []
  } catch (error) {
    console.error('Failed to load documents:', error)
  } finally {
    documentsLoading.value = false
  }
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
  }
}

const handleDrop = (event) => {
  isDragover.value = false
  const files = event.dataTransfer.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
  }
}

const uploadFile = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  try {
    const result = await api.uploadKnowledgeDocument(selectedFile.value)
    alert('文档上传成功！')
    closeUploadModal()
    await loadDocuments()
    await loadStats()
  } catch (error) {
    alert('文档上传失败：' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const confirmDelete = (doc) => {
  docToDelete.value = doc
  showDeleteModal.value = true
}

const deleteDocument = async () => {
  if (!docToDelete.value) return

  deleting.value = true
  try {
    await api.deleteKnowledgeDocument(docToDelete.value.id)
    alert('文档删除成功！')
    closeDeleteModal()
    await loadDocuments()
    await loadStats()
  } catch (error) {
    alert('文档删除失败：' + (error.response?.data?.detail || error.message))
  } finally {
    deleting.value = false
  }
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  docToDelete.value = null
}

const formatFileSize = (bytes) => {
  for (const unit of ['B', 'KB', 'MB', 'GB']) {
    if (bytes < 1024) {
      return `${bytes.toFixed(1)} ${unit}`
    }
    bytes /= 1024
  }
  return `${bytes.toFixed(1)} TB`
}

onMounted(() => {
  loadStats()
  loadDocuments()
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

.btn-secondary:disabled,
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
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

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-secondary);
}

.loading-state svg,
.empty-state svg {
  color: var(--color-text-tertiary);
  margin-bottom: 16px;
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
  align-items: center;
}

.doc-type {
  padding: 2px 8px;
  background: var(--color-bg);
  border-radius: 4px;
  font-weight: 500;
}

.doc-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
  color: var(--color-text-tertiary);
}

.doc-status.active {
  background: rgba(0, 113, 227, 0.1);
  color: #0071e3;
}

.delete-btn {
  color: #dc3545;
}

.delete-btn:hover {
  background: rgba(220, 53, 69, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-bg);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
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

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: var(--radius-lg);
  width: 500px;
  max-width: 90vw;
  overflow: hidden;
}

.modal-small {
  width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--color-border);
}

.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-area:hover,
.upload-area.dragover {
  border-color: var(--color-accent);
  background: rgba(0, 113, 227, 0.05);
}

.upload-area svg {
  color: var(--color-accent);
  margin-bottom: 12px;
}

.upload-area p {
  color: var(--color-text-primary);
  font-size: 14px;
  margin-bottom: 4px;
}

.upload-hint {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  margin-top: 16px;
}

.selected-file svg {
  color: var(--color-accent);
  flex-shrink: 0;
}

.selected-file .file-size {
  margin-left: auto;
  color: var(--color-text-secondary);
  font-size: 13px;
}

.delete-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.delete-icon svg {
  color: #dc3545;
}

.delete-icon {
  text-align: center;
}

.delete-icon h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.delete-icon p {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin-bottom: 8px;
}

.warning-text {
  color: #dc3545;
  font-size: 13px;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
