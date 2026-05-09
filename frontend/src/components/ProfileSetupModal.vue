<template>
  <div class="modal-overlay" @click.self="handleOverlayClick">
    <div class="modal-card">
      <!-- 步骤指示器 -->
      <div class="step-indicator">
        <div class="step" :class="{ active: step === 1, done: step > 1 }">
          <span class="step-num">{{ step > 1 ? '✓' : '1' }}</span>
          <span class="step-label">基础信息</span>
        </div>
        <div class="step-line"></div>
        <div class="step" :class="{ active: step === 2 }">
          <span class="step-num">2</span>
          <span class="step-label">训练偏好</span>
        </div>
      </div>

      <!-- Step 1: 基础信息 -->
      <div v-if="step === 1">
        <div class="modal-header">
          <h2>欢迎加入 AI 运动教练！</h2>
          <p>请填写您的基本信息，帮助我们为您定制专属训练方案</p>
        </div>

        <div class="form-body">
          <div class="form-row">
            <div class="form-group">
              <label>年龄</label>
              <input
                v-model.number="formData.age"
                type="number"
                placeholder="请输入年龄"
                min="10"
                max="100"
              />
            </div>
            <div class="form-group">
              <label>性别</label>
              <div class="radio-group">
                <label class="radio-label" :class="{ selected: formData.gender === 'female' }">
                  <input type="radio" v-model="formData.gender" value="female" hidden />
                  女
                </label>
                <label class="radio-label" :class="{ selected: formData.gender === 'male' }">
                  <input type="radio" v-model="formData.gender" value="male" hidden />
                  男
                </label>       
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>身高 (cm)</label>
              <input
                v-model.number="formData.height"
                type="number"
                placeholder="如 170"
                min="100"
                max="250"
              />
            </div>
            <div class="form-group">
              <label>体重 (kg)</label>
              <input
                v-model.number="formData.weight"
                type="number"
                placeholder="如 65"
                min="30"
                max="200"
              />
            </div>
          </div>

          <div class="form-group">
            <label>运动水平</label>
            <select v-model="formData.fitnessLevel">
              <option value="">请选择</option>
              <option value="beginner">初学者 - 很少运动</option>
              <option value="intermediate">中级 - 每周运动 2-3 次</option>
              <option value="advanced">高级 - 每周运动 4 次以上</option>
            </select>
          </div>
        </div>

        <div v-if="step1Error" class="error-msg">{{ step1Error }}</div>

        <div class="modal-footer">
          <button class="btn-skip" @click="handleSkip">暂时跳过</button>
          <button class="btn-next" @click="goStep2">下一步</button>
        </div>
      </div>

      <!-- Step 2: 训练偏好 -->
      <div v-if="step === 2">
        <div class="modal-header">
          <h2>训练偏好设置</h2>
          <p>告诉我们您的训练目标，AI 教练将更精准地服务您</p>
        </div>

        <div class="form-body">
          <div class="form-group">
            <label>训练目标</label>
            <select v-model="formData.goal">
              <option value="">请选择</option>
              <option value="lose_weight">减脂塑形</option>
              <option value="build_muscle">增肌增重</option>
              <option value="improve_endurance">提升耐力</option>
              <option value="improve_strength">增强力量</option>
              <option value="stay_healthy">保持健康</option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>每周训练天数</label>
              <select v-model.number="formData.weeklyDays">
                <option value="">请选择</option>
                <option v-for="d in 7" :key="d" :value="d">{{ d }} 天</option>
              </select>
            </div>
            <div class="form-group">
              <label>每次训练时长</label>
              <select v-model.number="formData.dailyDuration">
                <option value="">请选择</option>
                <option value="15">15 分钟</option>
                <option value="30">30 分钟</option>
                <option value="45">45 分钟</option>
                <option value="60">60 分钟</option>
                <option value="90">90 分钟</option>
                <option value="120">120 分钟</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>运动损伤史（选填）</label>
            <textarea
              v-model="formData.injuries"
              placeholder="如有运动损伤或身体不适，请在此说明，如：左膝半月板损伤"
              rows="3"
            ></textarea>
          </div>
        </div>

        <div v-if="errorMessage" class="error-msg">{{ errorMessage }}</div>

        <div class="modal-footer">
          <button class="btn-back" @click="step = 1">上一步</button>
          <button class="btn-submit" :disabled="loading" @click="handleSubmit">
            {{ loading ? '保存中...' : '完成设置' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const emit = defineEmits(['complete'])

const authStore = useAuthStore()

const step = ref(1)
const loading = ref(false)
const step1Error = ref('')
const errorMessage = ref('')

const formData = ref({
  age: null,
  gender: '',
  height: null,
  weight: null,
  fitnessLevel: '',
  goal: '',
  weeklyDays: '',
  dailyDuration: '',
  injuries: ''
})

function ageToRange(age) {
  if (!age) return ''
  if (age < 18) return 'under_18'
  if (age <= 25) return '18-25'
  if (age <= 35) return '26-35'
  if (age <= 45) return '36-45'
  if (age <= 55) return '46-55'
  return '55+'
}

function goStep2() {
  step1Error.value = ''
  if (!formData.value.age || !formData.value.gender || !formData.value.height ||
      !formData.value.weight || !formData.value.fitnessLevel) {
    step1Error.value = '请填写所有必填项'
    return
  }
  step.value = 2
}

async function handleSubmit() {
  errorMessage.value = ''
  if (!formData.value.goal) {
    errorMessage.value = '请选择训练目标'
    return
  }

  loading.value = true
  try {
    const payload = {
      goal: formData.value.goal,
      fitness_level: formData.value.fitnessLevel,
      age_range: ageToRange(formData.value.age),
      gender: formData.value.gender,
      height_cm: formData.value.height,
      weight_kg: formData.value.weight,
      weekly_days: formData.value.weeklyDays || null,
      daily_duration: formData.value.dailyDuration || null,
      injury_status: formData.value.injuries ? '有伤病史' : '无',
      injury_detail: formData.value.injuries || '',
      profile_source: 'manual'
    }

    await api.initializeProfile(payload)
    await authStore.completeProfile()
    emit('complete')
  } catch (error) {
    errorMessage.value = '保存失败，请稍后重试'
    console.error('初始化资料失败:', error)
  } finally {
    loading.value = false
  }
}

async function handleSkip() {
  await authStore.completeProfile()
  emit('complete')
}

function handleOverlayClick() {
  // 不允许点击遮罩关闭，必须填写或跳过
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.25);
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 32px;
}

/* 步骤指示器 */
.step-indicator {
  display: flex;
  align-items: center;
  margin-bottom: 28px;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
  opacity: 0.4;
}

.step.active,
.step.done {
  opacity: 1;
}

.step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  flex-shrink: 0;
}

.step.active .step-num {
  background: #2563eb;
  color: #fff;
}

.step.done .step-num {
  background: #2563eb;
  color: #fff;
}

.step-label {
  font-size: 13px;
  font-weight: 500;
  color: #444;
}

.step-line {
  flex: 1;
  height: 2px;
  background: #e0e0e0;
  margin: 0 12px;
}

/* 头部 */
.modal-header {
  margin-bottom: 24px;
}

.modal-header h2 {
  font-size: 22px;
  color: #222;
  margin-bottom: 6px;
}

.modal-header p {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

/* 表单 */
.form-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 14px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.radio-group {
  display: flex;
  gap: 10px;
  padding-top: 4px;
}

.radio-label {
  flex: 1;
  padding: 9px 0;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  color: #555;
}

.radio-label.selected {
  border-color: #2563eb;
  background: rgba(37, 99, 235, 0.07);
  color: #2563eb;
  font-weight: 500;
}

/* 错误提示 */
.error-msg {
  margin-top: 14px;
  padding: 10px 14px;
  background: #fff0f0;
  border: 1px solid #ffcccc;
  border-radius: 8px;
  color: #c33;
  font-size: 13px;
}

/* 底部按钮 */
.modal-footer {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  justify-content: flex-end;
}

.btn-skip {
  padding: 10px 20px;
  background: transparent;
  color: #888;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-skip:hover {
  border-color: #aaa;
  color: #555;
}

.btn-back {
  padding: 10px 20px;
  background: transparent;
  color: #555;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.btn-next,
.btn-submit {
  padding: 10px 28px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-next:hover,
.btn-submit:hover:not(:disabled) {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
