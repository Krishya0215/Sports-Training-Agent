<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>🏃 AI运动教练</h1>
        <p>欢迎回来，开始您的训练之旅</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="account">账号 / 邮箱</label>
          <input
            id="account"
            v-model="formData.account"
            type="text"
            placeholder="请输入用户名或邮箱"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="login-btn" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        
        <div class="login-links">
          <router-link to="/register" class="link">注册新账号</router-link>
          <span class="divider">|</span>
          <router-link to="/forgot-password" class="link">找回密码</router-link>
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
  account: '',
  password: ''
})

const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true
  
  try {
    const result = await authStore.login(
      formData.value.account,
      formData.value.password
    )
    
    if (result.success) {
      // 检查是否首次登录
      if (authStore.isFirstLogin && !authStore.profileCompleted) {
        // 跳转到基础信息填写页
        router.push('/profile-setup')
      } else {
        // 跳转到首页
        router.push('/')
      }
    } else {
      errorMessage.value = result.message
    }
  } catch (error) {
    errorMessage.value = '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: 20px;
}

.login-box {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: 0 2px 12px var(--color-shadow);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  transition: all 0.3s ease;
}

.login-box:hover {
  box-shadow: 0 4px 20px var(--color-shadow);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 28px;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  font-weight: 700;
}

.login-header p {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.login-form {
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

.login-btn {
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

.login-btn:hover:not(:disabled) {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-links {
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
