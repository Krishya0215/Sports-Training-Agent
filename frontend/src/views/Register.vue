<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h1>🏃 注册新账号</h1>
        <p>加入AI运动教练，开启智能训练</p>
      </div>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="请输入用户名"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="请输入邮箱地址"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码（6-20位）"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="formData.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        
        <button type="submit" class="register-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        
        <div class="register-links">
          <span>已有账号？</span>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
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
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleRegister = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  // 前端验证
  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  if (formData.value.password.length < 6 || formData.value.password.length > 20) {
    errorMessage.value = '密码长度应为6-20位'
    return
  }
  
  loading.value = true
  
  try {
    const result = await authStore.register(
      formData.value.username,
      formData.value.email,
      formData.value.password,
      formData.value.confirmPassword
    )
    
    if (result.success) {
      successMessage.value = '注册成功！3秒后跳转到登录页...'
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    } else {
      errorMessage.value = result.message
    }
  } catch (error) {
    errorMessage.value = '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: 20px;
}

.register-box {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: 0 2px 12px var(--color-shadow);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  transition: all 0.3s ease;
}

.register-box:hover {
  box-shadow: 0 4px 20px var(--color-shadow);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h1 {
  font-size: 28px;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  font-weight: 700;
}

.register-header p {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.register-form {
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
  color: var(--color-text-primary);
}

.error-message {
  padding: 12px;
  background: rgba(255, 59, 48, 0.1);
  border: 1px solid rgba(255, 59, 48, 0.2);
  border-radius: var(--radius-md);
  color: #ff3b30;
  font-size: 14px;
  text-align: center;
}

.success-message {
  padding: 12px;
  background: rgba(52, 199, 89, 0.1);
  border: 1px solid rgba(52, 199, 89, 0.2);
  border-radius: var(--radius-md);
  color: #34c759;
  font-size: 14px;
  text-align: center;
}

.register-btn {
  padding: 14px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.register-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.register-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.link {
  color: var(--color-accent);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.link:hover {
  color: var(--color-accent-hover);
  text-decoration: underline;
}
</style>
