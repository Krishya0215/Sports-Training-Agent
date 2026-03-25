<template>
  <div class="forgot-password-container">
    <div class="forgot-password-box">
      <div class="forgot-password-header">
        <h1>🔑 找回密码</h1>
        <p>通过邮箱验证码重置您的密码</p>
      </div>
      
      <form @submit.prevent="handleResetPassword" class="forgot-password-form">
        <div class="form-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="请输入注册邮箱"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="code">验证码</label>
          <div class="code-input-group">
            <input
              id="code"
              v-model="formData.code"
              type="text"
              placeholder="请输入6位验证码"
              maxlength="6"
              required
            />
            <button
              type="button"
              class="send-code-btn"
              :disabled="codeSending || countdown > 0"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? `${countdown}秒后重试` : '发送验证码' }}
            </button>
          </div>
        </div>
        
        <div class="form-group">
          <label for="newPassword">新密码</label>
          <input
            id="newPassword"
            v-model="formData.newPassword"
            type="password"
            placeholder="请输入新密码（6-20位）"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认新密码</label>
          <input
            id="confirmPassword"
            v-model="formData.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            required
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
        
        <div v-if="testCode" class="test-code-message">
          测试验证码：{{ testCode }}
        </div>
        
        <button type="submit" class="reset-btn" :disabled="loading">
          {{ loading ? '重置中...' : '重置密码' }}
        </button>
        
        <div class="forgot-password-links">
          <router-link to="/login" class="link">返回登录</router-link>
          <span class="divider">|</span>
          <router-link to="/register" class="link">注册新账号</router-link>
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
  email: '',
  code: '',
  newPassword: '',
  confirmPassword: ''
})

const loading = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
const errorMessage = ref('')
const successMessage = ref('')
const testCode = ref('') // 用于显示测试验证码

let countdownTimer = null

const handleSendCode = async () => {
  if (!formData.value.email) {
    errorMessage.value = '请输入邮箱地址'
    return
  }
  
  errorMessage.value = ''
  successMessage.value = ''
  testCode.value = ''
  codeSending.value = true
  
  try {
    const result = await authStore.sendVerificationCode(formData.value.email)
    
    if (result.success) {
      successMessage.value = result.message
      // 显示测试验证码（仅用于开发测试）
      if (result.code) {
        testCode.value = result.code
      }
      
      // 开始倒计时
      countdown.value = 60
      countdownTimer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(countdownTimer)
        }
      }, 1000)
    } else {
      errorMessage.value = result.message
    }
  } catch (error) {
    errorMessage.value = '发送验证码失败'
  } finally {
    codeSending.value = false
  }
}

const handleResetPassword = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  // 前端验证
  if (formData.value.newPassword !== formData.value.confirmPassword) {
    errorMessage.value = '两次输入的密码不一致'
    return
  }
  
  if (formData.value.newPassword.length < 6 || formData.value.newPassword.length > 20) {
    errorMessage.value = '密码长度应为6-20位'
    return
  }
  
  if (formData.value.code.length !== 6) {
    errorMessage.value = '请输入6位验证码'
    return
  }
  
  loading.value = true
  
  try {
    const result = await authStore.resetPassword(
      formData.value.email,
      formData.value.code,
      formData.value.newPassword,
      formData.value.confirmPassword
    )
    
    if (result.success) {
      successMessage.value = '密码重置成功！3秒后跳转到登录页...'
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    } else {
      errorMessage.value = result.message
    }
  } catch (error) {
    errorMessage.value = '重置密码失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 组件卸载时清除定时器
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: 20px;
}

.forgot-password-box {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: 0 2px 12px var(--color-shadow);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  transition: all 0.3s ease;
}

.forgot-password-box:hover {
  box-shadow: 0 4px 20px var(--color-shadow);
}

.forgot-password-header {
  text-align: center;
  margin-bottom: 32px;
}

.forgot-password-header h1 {
  font-size: 28px;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  font-weight: 700;
}

.forgot-password-header p {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.forgot-password-form {
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

.code-input-group {
  display: flex;
  gap: 8px;
}

.code-input-group input {
  flex: 1;
}

.send-code-btn {
  padding: 12px 16px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.send-code-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.send-code-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.test-code-message {
  padding: 12px;
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.2);
  border-radius: var(--radius-md);
  color: #d97706;
  font-size: 14px;
  text-align: center;
  font-weight: 600;
}

.reset-btn {
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

.reset-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.reset-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.forgot-password-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.link {
  color: var(--color-accent);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s ease;
}

.link:hover {
  color: var(--color-accent-hover);
  text-decoration: underline;
}

.divider {
  color: var(--color-border);
}
</style>
