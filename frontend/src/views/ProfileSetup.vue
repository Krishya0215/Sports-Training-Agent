<template>
  <div class="profile-setup-container">
    <div class="profile-setup-box">
      <div class="profile-setup-header">
        <h1>👋 欢迎加入AI运动教练</h1>
        <p>请完善您的基础信息，帮助我们为您提供更精准的训练建议</p>
      </div>
      
      <form @submit.prevent="handleSubmit" class="profile-setup-form">
        <div class="form-group">
          <label for="age">年龄</label>
          <input
            id="age"
            v-model.number="formData.age"
            type="number"
            placeholder="请输入您的年龄"
            min="10"
            max="100"
            required
          />
        </div>
        
        <div class="form-group">
          <label>性别</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="formData.gender" value="male" required />
              <span>男</span>
            </label>
            <label class="radio-label">
              <input type="radio" v-model="formData.gender" value="female" required />
              <span>女</span>
            </label>
          </div>
        </div>
        
        <div class="form-group">
          <label for="height">身高 (cm)</label>
          <input
            id="height"
            v-model.number="formData.height"
            type="number"
            placeholder="请输入您的身高"
            min="100"
            max="250"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="weight">体重 (kg)</label>
          <input
            id="weight"
            v-model.number="formData.weight"
            type="number"
            placeholder="请输入您的体重"
            min="30"
            max="200"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="fitnessLevel">运动水平</label>
          <select id="fitnessLevel" v-model="formData.fitnessLevel" required>
            <option value="">请选择</option>
            <option value="beginner">初学者 - 很少运动</option>
            <option value="intermediate">中级 - 每周运动2-3次</option>
            <option value="advanced">高级 - 每周运动4次以上</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="goal">训练目标</label>
          <select id="goal" v-model="formData.goal" required>
            <option value="">请选择</option>
            <option value="lose_weight">减脂塑形</option>
            <option value="build_muscle">增肌增重</option>
            <option value="improve_endurance">提升耐力</option>
            <option value="improve_strength">增强力量</option>
            <option value="stay_healthy">保持健康</option>
          </select>
        </div>
        
        <div class="form-group">
          <label for="injuries">运动损伤史（选填）</label>
          <textarea
            id="injuries"
            v-model="formData.injuries"
            placeholder="如有运动损伤或身体不适，请在此说明"
            rows="3"
          ></textarea>
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '提交中...' : '完成设置' }}
        </button>
        
        <button type="button" class="skip-btn" @click="handleSkip">
          暂时跳过
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  age: null,
  gender: '',
  height: null,
  weight: null,
  fitnessLevel: '',
  goal: '',
  injuries: ''
})

const loading = ref(false)
const errorMessage = ref('')

const handleSubmit = async () => {
  errorMessage.value = ''
  loading.value = true
  
  try {
    // 这里可以调用API保存用户资料
    // 暂时只标记为已完成
    await authStore.completeProfile()
    
    // 跳转到AI教练页
    router.push('/chat')
  } catch (error) {
    errorMessage.value = '保存失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const handleSkip = async () => {
  // 标记为已完成（即使跳过）
  await authStore.completeProfile()
  router.push('/chat')
}
</script>

<style scoped>
.profile-setup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.profile-setup-box {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.profile-setup-header {
  text-align: center;
  margin-bottom: 32px;
}

.profile-setup-header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.profile-setup-header p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.profile-setup-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
  font-family: inherit;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
}

.radio-label input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.error-message {
  padding: 12px;
  background: #fee;
  border: 1px solid #fcc;
  border-radius: 8px;
  color: #c33;
  font-size: 14px;
  text-align: center;
}

.submit-btn {
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.skip-btn {
  padding: 12px;
  background: transparent;
  color: #666;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.skip-btn:hover {
  border-color: #667eea;
  color: #667eea;
}
</style>
