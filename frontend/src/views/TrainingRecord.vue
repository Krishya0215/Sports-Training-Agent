<template>
  <div class="training-record-page">
    <Navbar />
    <div class="page-content">
      <div class="page-header">
        <h1>📝 训练记录</h1>
        <button class="btn-primary" @click="showRecordDialog = true">
          + 记录训练
        </button>
      </div>

    <!-- AI建议卡片 -->
    <div v-if="aiSuggestion" class="suggestion-card">
      <div class="suggestion-icon">💡</div>
      <div class="suggestion-content">
        <h3>AI 训练建议</h3>
        <p>{{ aiSuggestion }}</p>
      </div>
      <button class="btn-close-small" @click="aiSuggestion = null">×</button>
    </div>

    <!-- 记录列表 -->
    <div class="records-list">
      <div
        v-for="record in records"
        :key="record.id"
        class="record-card"
      >
        <div class="record-header">
          <div class="record-date">
            <span class="date-day">{{ formatDate(record.date).day }}</span>
            <span class="date-month">{{ formatDate(record.date).month }}</span>
          </div>
          <div class="record-info">
            <h3>{{ record.training_type }}</h3>
            <div class="record-meta">
              <span v-if="record.duration">⏱ {{ record.duration }}分钟</span>
              <span v-if="record.intensity">
                💪 {{ record.intensity }}强度
              </span>
            </div>
          </div>
        </div>

        <div class="record-feedback">
          <div class="feedback-item">
            <span class="label">疲劳度:</span>
            <div class="level-bar">
              <div
                class="level-fill"
                :style="{ width: (record.fatigue_level || 0) * 20 + '%' }"
                :class="getLevelClass(record.fatigue_level)"
              ></div>
            </div>
            <span class="level-text">{{ record.fatigue_level || 0 }}/5</span>
          </div>
          <div class="feedback-item">
            <span class="label">疼痛度:</span>
            <div class="level-bar">
              <div
                class="level-fill"
                :style="{ width: (record.pain_level || 0) * 20 + '%' }"
                :class="getLevelClass(record.pain_level)"
              ></div>
            </div>
            <span class="level-text">{{ record.pain_level || 0 }}/5</span>
          </div>
        </div>

        <div v-if="record.notes" class="record-notes">
          <p>{{ record.notes }}</p>
        </div>

        <div class="record-actions">
          <button class="btn-text" @click="viewRecord(record)">查看详情</button>
          <button class="btn-text danger" @click="deleteRecord(record.id)">
            删除
          </button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="records.length === 0" class="empty-state">
        <p>还没有训练记录</p>
        <p class="hint">开始记录你的训练，AI会帮你分析训练状态</p>
      </div>
    </div>

    <!-- 记录训练对话框 -->
    <div v-if="showRecordDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h2>记录训练</h2>
          <button class="btn-close" @click="closeDialog">×</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>训练日期</label>
            <input v-model="formData.date" type="date" required />
          </div>
          <div class="form-group">
            <label>训练类型</label>
            <select v-model="formData.training_type" required>
              <option value="">请选择</option>
              <option value="力量训练">力量训练</option>
              <option value="有氧运动">有氧运动</option>
              <option value="HIIT">HIIT</option>
              <option value="瑜伽">瑜伽</option>
              <option value="拉伸">拉伸</option>
              <option value="其他">其他</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>训练时长（分钟）</label>
              <input v-model.number="formData.duration" type="number" min="1" />
            </div>
            <div class="form-group">
              <label>训练强度</label>
              <select v-model="formData.intensity">
                <option value="低">低</option>
                <option value="中">中</option>
                <option value="高">高</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>疲劳度 (1-5)</label>
            <div class="slider-group">
              <input
                v-model.number="formData.fatigue_level"
                type="range"
                min="1"
                max="5"
                step="1"
              />
              <span class="slider-value">{{ formData.fatigue_level }}</span>
            </div>
            <div class="slider-labels">
              <span>轻松</span>
              <span>疲劳</span>
            </div>
          </div>
          <div class="form-group">
            <label>疼痛度 (1-5)</label>
            <div class="slider-group">
              <input
                v-model.number="formData.pain_level"
                type="range"
                min="1"
                max="5"
                step="1"
              />
              <span class="slider-value">{{ formData.pain_level }}</span>
            </div>
            <div class="slider-labels">
              <span>无痛</span>
              <span>疼痛</span>
            </div>
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea
              v-model="formData.notes"
              rows="4"
              placeholder="记录训练感受、完成情况等..."
            ></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveRecord">保存</button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import api from '../api'

export default {
  name: 'TrainingRecord',
  setup() {
    const records = ref([])
    const showRecordDialog = ref(false)
    const aiSuggestion = ref(null)
    const formData = ref({
      date: new Date().toISOString().split('T')[0],
      training_type: '',
      duration: 60,
      intensity: '中',
      fatigue_level: 3,
      pain_level: 1,
      notes: ''
    })

    const loadRecords = async () => {
      try {
        const response = await api.get('/training/records')
        records.value = (response.records || []).sort((a, b) => 
          new Date(b.date) - new Date(a.date)
        )
      } catch (error) {
        console.error('加载训练记录失败:', error)
      }
    }

    const saveRecord = async () => {
      try {
        if (!formData.value.training_type) {
          alert('请选择训练类型')
          return
        }

        const response = await api.post('/training/records', formData.value)
        records.value.unshift(response.record)
        
        // 显示AI建议
        if (response.suggestion) {
          aiSuggestion.value = response.suggestion
        }

        closeDialog()
      } catch (error) {
        console.error('保存训练记录失败:', error)
        alert('保存失败，请重试')
      }
    }

    const deleteRecord = async (recordId) => {
      if (!confirm('确定要删除这条训练记录吗？')) return

      try {
        await api.delete(`/training/records/${recordId}`)
        records.value = records.value.filter(r => r.id !== recordId)
      } catch (error) {
        console.error('删除训练记录失败:', error)
        alert('删除失败，请重试')
      }
    }

    const viewRecord = (record) => {
      // 可以扩展为详情页
      console.log('查看记录:', record)
    }

    const closeDialog = () => {
      showRecordDialog.value = false
      formData.value = {
        date: new Date().toISOString().split('T')[0],
        training_type: '',
        duration: 60,
        intensity: '中',
        fatigue_level: 3,
        pain_level: 1,
        notes: ''
      }
    }

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      const day = date.getDate()
      const month = date.toLocaleDateString('zh-CN', { month: 'short' })
      return { day, month }
    }

    const getLevelClass = (level) => {
      if (level <= 2) return 'level-low'
      if (level <= 3) return 'level-medium'
      return 'level-high'
    }

    onMounted(() => {
      loadRecords()
    })

    return {
      records,
      showRecordDialog,
      aiSuggestion,
      formData,
      saveRecord,
      deleteRecord,
      viewRecord,
      closeDialog,
      formatDate,
      getLevelClass
    }
  }
}
</script>

<style scoped>
.training-record-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.page-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

/* AI建议卡片 */
.suggestion-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}

.suggestion-icon {
  font-size: 2rem;
}

.suggestion-content h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.suggestion-content p {
  margin: 0;
  opacity: 0.95;
}

.btn-close-small {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
}

/* 记录列表 */
.records-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.record-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.record-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.record-header {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.record-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.75rem;
  border-radius: 8px;
  min-width: 60px;
}

.date-day {
  font-size: 1.5rem;
  font-weight: bold;
}

.date-month {
  font-size: 0.85rem;
  opacity: 0.9;
}

.record-info h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.record-meta {
  display: flex;
  gap: 1rem;
  color: #666;
  font-size: 0.9rem;
}

/* 反馈条 */
.record-feedback {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.feedback-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.feedback-item .label {
  min-width: 60px;
  color: #666;
  font-size: 0.9rem;
}

.level-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.level-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.level-fill.level-low {
  background: #27ae60;
}

.level-fill.level-medium {
  background: #f39c12;
}

.level-fill.level-high {
  background: #e74c3c;
}

.level-text {
  min-width: 40px;
  text-align: right;
  color: #666;
  font-size: 0.9rem;
}

.record-notes {
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.record-notes p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

.record-actions {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

/* 表单样式 */
.slider-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slider-group input[type="range"] {
  flex: 1;
}

.slider-value {
  min-width: 30px;
  text-align: center;
  font-weight: bold;
  color: #667eea;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 0.25rem;
  font-size: 0.85rem;
  color: #999;
}

select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
}

/* 复用其他样式 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #999;
}

.empty-state .hint {
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

.dialog-overlay,
.dialog,
.dialog-header,
.dialog-body,
.dialog-footer,
.form-group,
.form-row,
.btn-primary,
.btn-secondary,
.btn-text,
.btn-close {
  /* 复用TrainingPlan.vue的样式 */
}
</style>
