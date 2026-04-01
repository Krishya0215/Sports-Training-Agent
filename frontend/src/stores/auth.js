import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const isFirstLogin = computed(() => user.value?.is_first_login || false)
  const profileCompleted = computed(() => user.value?.profile_completed || false)
  
  // 登录
  async function login(account, password) {
    try {
      const data = await api.post('/auth/login', {
        account,
        password
      })

      if (data.success) {
        token.value = data.token
        user.value = data.user

        // 保存到本地存储
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))

        return { success: true }
      } else {
        return { success: false, message: data.message }
      }
    } catch (error) {
      console.error('登录失败:', error)
      return {
        success: false,
        message: error.response?.data?.detail || '登录失败，请稍后重试'
      }
    }
  }
  
  // 注册
  async function register(username, email, password, confirmPassword) {
    try {
      const data = await api.post('/auth/register', {
        username,
        email,
        password,
        confirm_password: confirmPassword
      })

      if (!data) {
        throw new Error('服务器响应为空')
      }

      if (data.success) {
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch (error) {
      console.error('注册失败:', error)
      return {
        success: false,
        message: error.response?.data?.detail || '注册失败，请稍后重试'
      }
    }
  }
  
  // 退出登录
  async function logout() {
    try {
      if (token.value) {
        await api.post('/auth/logout', null, {
          params: { token: token.value }
        })
      }
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      // 清除状态
      const userInfo = user.value
      const userId = userInfo?.id

      token.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')

      // 清除该用户的聊天历史
      if (userId) {
        localStorage.removeItem(`sports-training-chat-history-${userId}`)
        localStorage.removeItem(`sports-training-active-plan-id-${userId}`)
        localStorage.removeItem(`sports-training-use-multi-agent-${userId}`)
      }
    }
  }
  
  // 验证token
  async function verifyToken() {
    if (!token.value) {
      return false
    }

    try {
      const data = await api.get('/auth/verify', {
        params: { token: token.value }
      })

      if (data.success) {
        user.value = data.user
        localStorage.setItem('user', JSON.stringify(data.user))
        return true
      } else {
        // token无效，清除登录状态
        await logout()
        return false
      }
    } catch (error) {
      console.error('验证token失败:', error)
      await logout()
      return false
    }
  }
  
  // 发送验证码
  async function sendVerificationCode(email) {
    try {
      const data = await api.post('/auth/send-code', { email })

      if (data.success) {
        return {
          success: true,
          message: data.message,
          code: data.code // 仅用于测试
        }
      } else {
        return { success: false, message: data.message }
      }
    } catch (error) {
      console.error('发送验证码失败:', error)
      return {
        success: false,
        message: error.response?.data?.detail || '发送验证码失败'
      }
    }
  }
  
  // 重置密码
  async function resetPassword(email, code, newPassword, confirmPassword) {
    try {
      const data = await api.post('/auth/reset-password', {
        email,
        code,
        new_password: newPassword,
        confirm_password: confirmPassword
      })

      if (data.success) {
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch (error) {
      console.error('重置密码失败:', error)
      return {
        success: false,
        message: error.response?.data?.detail || '重置密码失败'
      }
    }
  }
  
  // 完成资料填写
  async function completeProfile() {
    if (!user.value) return

    try {
      const data = await api.post('/auth/complete-profile', null, {
        params: { email: user.value.email }
      })

      if (data.success) {
        user.value.profile_completed = true
        user.value.is_first_login = false
        localStorage.setItem('user', JSON.stringify(user.value))
        return { success: true }
      }
    } catch (error) {
      console.error('更新资料状态失败:', error)
    }
  }
  
  return {
    token,
    user,
    isAuthenticated,
    isFirstLogin,
    profileCompleted,
    login,
    register,
    logout,
    verifyToken,
    sendVerificationCode,
    resetPassword,
    completeProfile
  }
})
