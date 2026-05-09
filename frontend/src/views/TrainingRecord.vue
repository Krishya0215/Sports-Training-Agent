<template>
  <div class="training-record-page">
    <Navbar />
    <div class="page-content">

      <!-- 顶部标题 -->
      <div class="page-header">
        <div class="header-left">
          <h1>健康记录</h1>
          <p class="header-sub">记录训练、饮食与体重，追踪你的健康数据</p>
        </div>
      </div>

      <!-- Tab 切换 -->
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.icon }} {{ tab.label }}
          <span class="tab-count">{{ getCount(tab.key) }}</span>
        </button>
      </div>

      <!-- 未选中任何 Tab 时的概览 -->
      <div v-if="activeTab === null" class="overview-grid">
        <div class="overview-card" @click="activeTab = 'training'">
          <!-- <span class="overview-icon">📝</span> -->
          <div class="overview-info">
            <p class="overview-label">训练记录</p>
            <p class="overview-count">{{ trainingRecords.length }} 条</p>
          </div>
        </div>
        <div class="overview-card" @click="activeTab = 'diet'">
          <!-- <span class="overview-icon">🍎</span> -->
          <div class="overview-info">
            <p class="overview-label">饮食记录</p>
            <p class="overview-count">{{ dietRecords.length }} 条</p>
          </div>
        </div>
        <div class="overview-card" @click="activeTab = 'weight'">
          <!-- <span class="overview-icon">⚖️</span> -->
          <div class="overview-info">
            <p class="overview-label">体重记录</p>
            <p class="overview-count">{{ weightRecords.length }} 条</p>
          </div>
        </div>
      </div>

      <!-- 训练记录列表 -->
      <div v-if="activeTab === 'training'">
        <div class="tab-header">
          <button class="btn btn-outline" @click="openModal('training')">+ 记录训练</button>
        </div>        <div v-if="trainingRecords.length === 0" class="empty-state">
          <p class="empty-icon">📝</p>
          <p class="empty-title">还没有训练记录</p>
          <p class="empty-hint">点击「记录训练」开始追踪你的训练状态</p>
        </div>
        <div v-else class="records-list">
          <div v-for="record in trainingRecords" :key="record.id" class="record-card">
            <div class="record-date-badge">
              <span class="date-day">{{ formatDate(record.date).day }}</span>
              <span class="date-month">{{ formatDate(record.date).month }}</span>
            </div>
            <div class="record-body">
              <div class="record-top">
                <h3 class="record-title">{{ record.training_type }}</h3>
                <div class="record-tags">
                  <span v-if="record.duration" class="tag">⏱ {{ record.duration }} 分钟</span>
                  <span v-if="record.intensity" class="tag">💪 {{ record.intensity }}强度</span>
                </div>
              </div>
              <div class="level-bars">
                <div class="level-row">
                  <span class="level-label">疲劳</span>
                  <div class="level-track">
                    <div class="level-fill" :class="getLevelClass(record.fatigue_level)" :style="{ width: (record.fatigue_level || 0) * 20 + '%' }"></div>
                  </div>
                  <span class="level-num">{{ record.fatigue_level || 0 }}/5</span>
                </div>
                <div class="level-row">
                  <span class="level-label">疼痛</span>
                  <div class="level-track">
                    <div class="level-fill" :class="getLevelClass(record.pain_level)" :style="{ width: (record.pain_level || 0) * 20 + '%' }"></div>
                  </div>
                  <span class="level-num">{{ record.pain_level || 0 }}/5</span>
                </div>
              </div>
              <p v-if="record.notes" class="record-notes">{{ record.notes }}</p>
            </div>
            <button class="delete-btn" @click="deleteRecord('training', record.id)" title="删除">✕</button>
          </div>
        </div>
      </div>

      <!-- 饮食记录列表 -->
      <div v-if="activeTab === 'diet'">
        <div class="tab-header">
          <button class="btn btn-outline" @click="openModal('diet')">+ 记录饮食</button>
        </div>        <div v-if="dietRecords.length === 0" class="empty-state">
          <p class="empty-icon">🍎</p>
          <p class="empty-title">还没有饮食记录</p>
          <p class="empty-hint">点击「记录饮食」开始追踪你的每日饮食</p>
        </div>
        <div v-else class="records-list">
          <div v-for="record in dietRecords" :key="record.id" class="record-card">
            <div class="record-date-badge diet">
              <span class="date-day">{{ formatDate(record.date).day }}</span>
              <span class="date-month">{{ formatDate(record.date).month }}</span>
            </div>
            <div class="record-body">
              <div class="record-top">
                <h3 class="record-title">{{ record.meal_type }}</h3>
              </div>
              <p class="record-food">{{ record.food_content }}</p>
              <p v-if="record.notes" class="record-notes">{{ record.notes }}</p>
            </div>
            <button class="delete-btn" @click="deleteRecord('diet', record.id)" title="删除">✕</button>
          </div>
        </div>
      </div>

      <!-- 体重记录列表 -->
      <div v-if="activeTab === 'weight'">
        <div class="tab-header">
          <button class="btn btn-outline" @click="openModal('weight')">+ 记录体重</button>
        </div>        <div v-if="weightRecords.length === 0" class="empty-state">
          <p class="empty-icon">⚖️</p>
          <p class="empty-title">还没有体重记录</p>
          <p class="empty-hint">点击「记录体重」开始追踪你的体重变化</p>
        </div>
        <div v-else class="records-list">
          <div v-for="record in weightRecords" :key="record.id" class="record-card">
            <div class="record-date-badge weight">
              <span class="date-day">{{ formatDate(record.date).day }}</span>
              <span class="date-month">{{ formatDate(record.date).month }}</span>
            </div>
            <div class="record-body">
              <div class="record-top">
                <h3 class="record-title">{{ record.weight }} kg</h3>
                <span v-if="record.body_fat" class="tag">体脂 {{ record.body_fat }}%</span>
              </div>
              <p v-if="record.notes" class="record-notes">{{ record.notes }}</p>
            </div>
            <button class="delete-btn" @click="deleteRecord('weight', record.id)" title="删除">✕</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 记录训练 Modal -->
    <div v-if="activeModal === 'training'" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <button class="modal-close" @click="closeModal">✕</button>
        <div class="modal-head">
          <p class="modal-tag">训练记录</p>
          <h2>记录今天的训练表现</h2>
          <p class="modal-copy">填写训练类型、时长和身体反馈，方便后续分析训练节奏与恢复状态。</p>
        </div>
        <form @submit.prevent="submitTrainingRecord">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">训练类型</label>
              <select v-model="trainingForm.training_type" class="form-input">
                <option value="">请选择</option>
                <option value="力量训练">力量训练</option>
                <option value="有氧训练">有氧训练</option>
                <option value="跑步">跑步</option>
                <option value="HIIT">HIIT</option>
                <option value="瑜伽拉伸">瑜伽拉伸</option>
                <option value="球类运动">球类运动</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">训练时长（分钟）</label>
              <input v-model.number="trainingForm.duration" class="form-input" type="number" min="1" max="600" placeholder="分钟">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">训练强度</label>
            <select v-model="trainingForm.intensity" class="form-input">
              <option value="">请选择</option>
              <option value="低">低</option>
              <option value="中">中</option>
              <option value="高">高</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">疲劳程度</label>
            <div class="range-selector">
              <button v-for="n in [1,2,3,4,5]" :key="n" type="button" class="level-btn" :class="{ selected: trainingForm.fatigue_level === n }" @click="trainingForm.fatigue_level = n">{{ n }}</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">疼痛程度</label>
            <div class="range-selector">
              <button v-for="n in [0,1,2,3,4,5]" :key="n" type="button" class="level-btn" :class="{ selected: trainingForm.pain_level === n }" @click="trainingForm.pain_level = n">{{ n }}</button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea v-model.trim="trainingForm.notes" class="form-textarea" rows="3" placeholder="例如：今天状态不错，右膝有轻微不适"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存训练记录' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 记录饮食 Modal -->
    <div v-if="activeModal === 'diet'" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <button class="modal-close" @click="closeModal">✕</button>
        <div class="modal-head">
          <p class="modal-tag">饮食记录</p>
          <h2>记录今天吃了什么</h2>
          <p class="modal-copy">记录餐别和食物内容，系统会结合训练安排分析你的饮食情况。</p>
        </div>
        <form @submit.prevent="submitDietRecord">
          <div class="form-group">
            <label class="form-label">餐别</label>
            <select v-model="dietForm.meal_type" class="form-input">
              <option value="">请选择</option>
              <option value="早餐">早餐</option>
              <option value="午餐">午餐</option>
              <option value="晚餐">晚餐</option>
              <option value="加餐">加餐</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">食物内容</label>
            <textarea v-model.trim="dietForm.food_content" class="form-textarea" rows="4" placeholder="例如：鸡胸肉沙拉、米饭半碗、无糖酸奶"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea v-model.trim="dietForm.notes" class="form-textarea" rows="2" placeholder="例如：训练后 30 分钟内进食，今天饮水偏少"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存饮食记录' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 记录体重 Modal -->
    <div v-if="activeModal === 'weight'" class="modal-mask" @click.self="closeModal">
      <div class="modal-card">
        <button class="modal-close" @click="closeModal">✕</button>
        <div class="modal-head">
          <p class="modal-tag">体重记录</p>
          <h2>记录体重变化</h2>
          <p class="modal-copy">记录体重即可，体脂率可以选填，方便后续观察减脂、增肌或维持阶段的趋势。</p>
        </div>
        <form @submit.prevent="submitWeightRecord">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">体重（kg）</label>
              <input v-model.number="weightForm.weight" class="form-input" type="number" min="0" step="0.1" placeholder="kg">
            </div>
            <div class="form-group">
              <label class="form-label">体脂率（选填）</label>
              <input v-model.number="weightForm.body_fat" class="form-input" type="number" min="0" max="100" step="0.1" placeholder="%">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">备注</label>
            <textarea v-model.trim="weightForm.notes" class="form-textarea" rows="2" placeholder="例如：晨起空腹测量，昨晚睡眠一般"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-outline" @click="closeModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存体重记录' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import api from '../api'

// Tab
const tabs = [
  { key: 'training', label: '训练记录', icon: '📝' },
  { key: 'diet',     label: '饮食记录', icon: '🍎' },
  { key: 'weight',   label: '体重记录', icon: '⚖️' }
]
const activeTab = ref('training')

// 数据
const trainingRecords = ref([])
const dietRecords = ref([])
const weightRecords = ref([])
// Modal
const activeModal = ref(null) // 'training' | 'diet' | 'weight' | null
const saving = ref(false)

// 表单
const trainingForm = ref({ training_type: '', duration: 30, intensity: '', fatigue_level: 3, pain_level: 0, notes: '' })
const dietForm     = ref({ meal_type: '', food_content: '', notes: '' })
const weightForm   = ref({ weight: '', body_fat: '', notes: '' })

const openModal = (type) => {
  activeModal.value = type
}
const closeModal = () => {
  activeModal.value = null
  trainingForm.value = { training_type: '', duration: 30, intensity: '', fatigue_level: 3, pain_level: 0, notes: '' }
  dietForm.value     = { meal_type: '', food_content: '', notes: '' }
  weightForm.value   = { weight: '', body_fat: '', notes: '' }
}

const getCount = (tab) => {
  if (tab === 'training') return trainingRecords.value.length
  if (tab === 'diet')     return dietRecords.value.length
  if (tab === 'weight')   return weightRecords.value.length
  return 0
}

// 加载数据
const loadAll = async () => {
  try {
    const [tr, dr, wr] = await Promise.allSettled([
      api.get('/training/records'),
      api.get('/daily/records'),
      api.get('/weight/records')
    ])
    if (tr.status === 'fulfilled') trainingRecords.value = (tr.value.records || []).sort((a, b) => new Date(b.date) - new Date(a.date))
    if (dr.status === 'fulfilled') dietRecords.value     = (dr.value.records || []).sort((a, b) => new Date(b.date) - new Date(a.date))
    if (wr.status === 'fulfilled') weightRecords.value   = (wr.value.records || []).sort((a, b) => new Date(b.date) - new Date(a.date))
  } catch (e) {
    console.error('加载记录失败', e)
  }
}

// 提交
const submitTrainingRecord = async () => {
  if (!trainingForm.value.training_type) { alert('请选择训练类型'); return }
  saving.value = true
  try {
    const res = await api.post('/training/records', {
      date: new Date().toISOString().split('T')[0],
      ...trainingForm.value,
      completion_status: 'completed'
    })
    trainingRecords.value.unshift(res.record)
    activeTab.value = 'training'
    closeModal()
  } catch (e) { alert('保存失败：' + e.message) }
  finally { saving.value = false }
}

const submitDietRecord = async () => {
  if (!dietForm.value.meal_type || !dietForm.value.food_content) { alert('请填写餐别和食物内容'); return }
  saving.value = true
  try {
    const res = await api.post('/daily/records', {
      date: new Date().toISOString().split('T')[0],
      ...dietForm.value
    })
    dietRecords.value.unshift(res.record)
    activeTab.value = 'diet'
    closeModal()
  } catch (e) { alert('保存失败：' + e.message) }
  finally { saving.value = false }
}

const submitWeightRecord = async () => {
  if (!weightForm.value.weight) { alert('请输入体重'); return }
  saving.value = true
  try {
    const payload = { date: new Date().toISOString().split('T')[0], weight: weightForm.value.weight, notes: weightForm.value.notes }
    if (weightForm.value.body_fat !== '' && weightForm.value.body_fat !== null && weightForm.value.body_fat !== undefined) {
      payload.body_fat = weightForm.value.body_fat
    }
    const res = await api.post('/weight/records', payload)
    weightRecords.value.unshift(res.record)
    activeTab.value = 'weight'
    closeModal()
  } catch (e) { alert('保存失败：' + e.message) }
  finally { saving.value = false }
}

// 删除
const deleteRecord = async (type, id) => {
  if (!confirm('确定删除这条记录吗？')) return
  try {
    if (type === 'training') {
      await api.delete(`/training/records/${id}`)
      trainingRecords.value = trainingRecords.value.filter(r => r.id !== id)
    } else if (type === 'diet') {
      await api.delete(`/daily/records/${id}`)
      dietRecords.value = dietRecords.value.filter(r => r.id !== id)
    } else if (type === 'weight') {
      await api.delete(`/weight/records/${id}`)
      weightRecords.value = weightRecords.value.filter(r => r.id !== id)
    }
  } catch (e) { alert('删除失败：' + e.message) }
}

// 工具函数
const formatDate = (dateStr) => {
  const d = new Date(dateStr)
  return { day: d.getDate(), month: d.toLocaleDateString('zh-CN', { month: 'short' }) }
}
const getLevelClass = (level) => {
  if (level <= 2) return 'level-low'
  if (level <= 3) return 'level-medium'
  return 'level-high'
}

onMounted(loadAll)
</script>

<style scoped>
.training-record-page {
  min-height: 100vh;
  background: var(--color-bg, #f5f5f7);
}

.page-content {
  max-width: 860px;
  margin: 0 auto;
  padding: 32px 24px 60px;
}

/* 顶部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 28px;
  gap: 16px;
  flex-wrap: wrap;
}

.header-left h1 {
  font-size: 26px;
  font-weight: 700;
  color: var(--color-text-primary, #111);
  margin: 0 0 4px;
}

.header-sub {
  font-size: 14px;
  color: var(--color-text-secondary, #666);
  margin: 0;
}

.tab-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 按钮 */
.btn {
  padding: 9px 18px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.18s;
  white-space: nowrap;
}

.btn-primary {
  background: #2563eb;
  color: #fff;
}
.btn-primary:hover { background: #1d4ed8; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-outline {
  background: #fff;
  color: #333;
  border: 1px solid #d1d5db;
}
.btn-outline:hover { border-color: #2563eb; color: #2563eb; }

/* Tab */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  background: #fff;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  transition: all 0.18s;
}

.tab-btn.active {
  background: #111;
  color: #fff;
  border-color: #111;
}

.tab-count {
  background: rgba(0,0,0,0.08);
  border-radius: 999px;
  padding: 1px 7px;
  font-size: 12px;
}
.tab-btn.active .tab-count {
  background: rgba(255,255,255,0.25);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
}
.empty-icon { font-size: 40px; margin: 0 0 12px; }
.empty-title { font-size: 16px; font-weight: 600; color: #333; margin: 0 0 6px; }
.empty-hint { font-size: 14px; color: #999; margin: 0; }

/* 记录卡片 */
.records-list { display: flex; flex-direction: column; gap: 12px; }

.record-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: #fff;
  border-radius: 14px;
  padding: 16px 20px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  position: relative;
  transition: box-shadow 0.2s;
}
.record-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.1); }

.record-date-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #2563eb;
  color: #fff;
  border-radius: 10px;
  padding: 10px 12px;
  min-width: 52px;
  flex-shrink: 0;
}
.record-date-badge.diet   { background: #16a34a; }
.record-date-badge.weight { background: #7c3aed; }
.date-day   { font-size: 20px; font-weight: 700; line-height: 1; }
.date-month { font-size: 12px; opacity: 0.85; margin-top: 2px; }

.record-body { flex: 1; min-width: 0; }
.record-top {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.record-title { font-size: 16px; font-weight: 600; color: #111; margin: 0; }

.tag {
  background: #f0f4ff;
  color: #2563eb;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 500;
}

/* 进度条 */
.level-bars { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
.level-row { display: flex; align-items: center; gap: 10px; }
.level-label { min-width: 28px; font-size: 12px; color: #888; }
.level-track { flex: 1; height: 6px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.level-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
.level-low    { background: #22c55e; }
.level-medium { background: #f59e0b; }
.level-high   { background: #ef4444; }
.level-num { min-width: 32px; font-size: 12px; color: #666; text-align: right; }

.record-food {
  font-size: 14px;
  color: #444;
  line-height: 1.5;
  margin: 0 0 6px;
}
.record-notes {
  font-size: 13px;
  color: #888;
  line-height: 1.5;
  margin: 0;
}

.delete-btn {
  position: absolute; top: 12px; right: 12px;
  background: none; border: none; color: #ccc;
  cursor: pointer; font-size: 14px; padding: 4px;
  border-radius: 50%; transition: color 0.2s, background 0.2s;
}
.delete-btn:hover { color: #ef4444; background: #fef2f2; }

/* 概览卡片 */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 8px;
}

.overview-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 20px 24px;
  cursor: pointer;
  transition: box-shadow 0.18s, border-color 0.18s;
}
.overview-card:hover {
  border-color: #2563eb;
  box-shadow: 0 4px 14px rgba(37,99,235,0.08);
}

.overview-icon { font-size: 28px; flex-shrink: 0; }
.overview-label { font-size: 13px; color: #888; margin: 0 0 4px; }
.overview-count { font-size: 22px; font-weight: 700; color: #111; margin: 0; }

@media (max-width: 600px) {
  .overview-grid { grid-template-columns: 1fr; }
}


.modal-mask {
  position: fixed; inset: 0;
  background: rgba(12, 24, 20, 0.5);
  display: flex; align-items: center; justify-content: center;
  padding: 24px; z-index: 200;
}

.modal-card {
  width: min(500px, 100%);
  max-height: 88vh;
  overflow-y: auto;
  background: #fff;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 24px 60px rgba(0,0,0,0.18);
  position: relative;
}

.modal-close {
  position: absolute; top: 16px; right: 20px;
  background: none; border: none; font-size: 18px;
  color: #999; cursor: pointer; padding: 4px;
}
.modal-close:hover { color: #333; }

.modal-head { margin-bottom: 20px; }
.modal-tag {
  display: inline-flex; align-items: center;
  padding: 5px 12px;
  background: rgba(37,99,235,0.08);
  color: #2563eb;
  border-radius: 999px;
  font-size: 13px; font-weight: 700;
  margin-bottom: 10px;
}
.modal-head h2 { font-size: 22px; font-weight: 700; margin: 0 0 6px; color: #111; }
.modal-copy { font-size: 14px; color: #888; margin: 0; line-height: 1.5; }

/* 表单 */
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.form-group { margin-bottom: 14px; }
.form-label { display: block; font-size: 14px; font-weight: 500; color: #333; margin-bottom: 6px; }

.form-input {
  width: 100%; padding: 9px 12px;
  border: 1px solid #d1d5db; border-radius: 8px;
  font-size: 14px; outline: none; transition: border-color 0.2s;
  box-sizing: border-box;
}
.form-input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }

.form-textarea {
  width: 100%; padding: 9px 12px;
  border: 1px solid #d1d5db; border-radius: 8px;
  font-size: 14px; outline: none; resize: vertical;
  font-family: inherit; transition: border-color 0.2s;
  box-sizing: border-box;
}
.form-textarea:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }

.range-selector { display: flex; gap: 8px; }
.level-btn {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  background: #fff; color: #111;
  border: 1px solid #d1d5db; border-radius: 8px;
  cursor: pointer; font-size: 14px; font-weight: 500;
  transition: all 0.15s;
}
.level-btn.selected { background: #2563eb; color: #fff; border-color: #2563eb; }
.level-btn:hover { border-color: #2563eb; }

.modal-actions {
  display: flex; gap: 10px; justify-content: flex-end;
  margin-top: 20px; padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
</style>
