<template>
  <div class="profile-page">
    <div class="page-header">
      <button class="back-btn" @click="router.back()">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10 12L6 8L10 4"/>
        </svg>
        返回
      </button>
      <h1 class="page-title">个人资料</h1>
      <p class="page-subtitle">管理您的账户信息和运动档案</p>
    </div>

    <div class="profile-grid">
      <!-- 左列：账户信息 + 修改密码 -->
      <div class="profile-col">
        <!-- 账户信息卡片 -->
        <div class="card">
          <div class="card-header">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <circle cx="10" cy="7" r="3"/>
                <path d="M4 18C4 14.6863 6.68629 12 10 12C13.3137 12 16 14.6863 16 18" stroke="currentColor" stroke-width="1.5" fill="none" stroke-linecap="round"/>
              </svg>
            </div>
            <h2 class="card-title">账户信息</h2>
          </div>

          <div class="avatar-section">
            <div class="avatar-wrapper" @click="triggerFileInput" :class="{ uploading: avatarUploading }">
              <img v-if="avatarUrl" :src="avatarUrl" class="avatar-img" alt="头像" />
              <div v-else class="avatar-circle">
                <span class="avatar-letter">{{ avatarLetter }}</span>
              </div>
              <div class="avatar-overlay">
                <svg v-if="!avatarUploading" width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="white" stroke-width="1.5" stroke-linecap="round">
                  <path d="M9 12V6M6 9l3-3 3 3"/>
                  <rect x="2" y="2" width="14" height="14" rx="3"/>
                </svg>
                <div v-else class="avatar-spinner"></div>
              </div>
            </div>
            <input ref="fileInputRef" type="file" accept="image/jpeg,image/png,image/webp" class="hidden-input" @change="handleAvatarChange" />
            <div class="avatar-info">
              <p class="avatar-name">{{ user?.username || '用户' }}</p>
              <p class="avatar-role">{{ user?.role === 'admin' ? '管理员' : '普通用户' }}</p>
            </div>
          </div>

          <form @submit.prevent="saveAccountInfo" class="form">
            <div class="form-group">
              <label>用户名</label>
              <input v-model="accountForm.username" type="text" placeholder="请输入用户名" maxlength="20" />
            </div>
            <div class="form-group">
              <label>邮箱</label>
              <input v-model="accountForm.email" type="email" placeholder="请输入邮箱" />
            </div>
            <div v-if="accountMsg" :class="['msg', accountMsg.type]">{{ accountMsg.text }}</div>
            <button type="submit" class="btn-primary" :disabled="accountLoading">
              {{ accountLoading ? '保存中...' : '保存修改' }}
            </button>
          </form>
        </div>

        <!-- 修改密码卡片 -->
        <div class="card">
          <div class="card-header">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="4" y="9" width="12" height="9" rx="2"/>
                <path d="M7 9V6a3 3 0 0 1 6 0v3" stroke-linecap="round"/>
              </svg>
            </div>
            <h2 class="card-title">修改密码</h2>
          </div>

          <form @submit.prevent="changePassword" class="form">
            <div class="form-group">
              <label>当前密码</label>
              <div class="password-input">
                <input
                  v-model="passwordForm.currentPassword"
                  :type="showCurrentPwd ? 'text' : 'password'"
                  placeholder="请输入当前密码"
                  required
                />
                <button type="button" class="eye-btn" @click="showCurrentPwd = !showCurrentPwd">
                  <svg v-if="!showCurrentPwd" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M1 8C1 8 3.5 3 8 3C12.5 3 15 8 15 8C15 8 12.5 13 8 13C3.5 13 1 8 1 8Z"/>
                    <circle cx="8" cy="8" r="2"/>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M2 2L14 14M6.5 6.7C6.2 7 6 7.5 6 8C6 9.1 6.9 10 8 10C8.5 10 8.9 9.8 9.2 9.5"/>
                    <path d="M4 4.5C2.5 5.5 1.5 7 1 8C1.5 9 3.5 13 8 13C9.5 13 10.8 12.5 11.8 11.8"/>
                    <path d="M12.5 10C13.5 9 14.5 8 15 8C14.5 7 12.5 3 8 3C7 3 6 3.3 5.2 3.7"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="form-group">
              <label>新密码</label>
              <div class="password-input">
                <input
                  v-model="passwordForm.newPassword"
                  :type="showNewPwd ? 'text' : 'password'"
                  placeholder="请输入新密码（6-20位）"
                  required
                />
                <button type="button" class="eye-btn" @click="showNewPwd = !showNewPwd">
                  <svg v-if="!showNewPwd" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M1 8C1 8 3.5 3 8 3C12.5 3 15 8 15 8C15 8 12.5 13 8 13C3.5 13 1 8 1 8Z"/>
                    <circle cx="8" cy="8" r="2"/>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M2 2L14 14M6.5 6.7C6.2 7 6 7.5 6 8C6 9.1 6.9 10 8 10C8.5 10 8.9 9.8 9.2 9.5"/>
                    <path d="M4 4.5C2.5 5.5 1.5 7 1 8C1.5 9 3.5 13 8 13C9.5 13 10.8 12.5 11.8 11.8"/>
                    <path d="M12.5 10C13.5 9 14.5 8 15 8C14.5 7 12.5 3 8 3C7 3 6 3.3 5.2 3.7"/>
                  </svg>
                </button>
              </div>
            </div>
            <div class="form-group">
              <label>确认新密码</label>
              <div class="password-input">
                <input
                  v-model="passwordForm.confirmPassword"
                  :type="showConfirmPwd ? 'text' : 'password'"
                  placeholder="请再次输入新密码"
                  required
                />
                <button type="button" class="eye-btn" @click="showConfirmPwd = !showConfirmPwd">
                  <svg v-if="!showConfirmPwd" width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M1 8C1 8 3.5 3 8 3C12.5 3 15 8 15 8C15 8 12.5 13 8 13C3.5 13 1 8 1 8Z"/>
                    <circle cx="8" cy="8" r="2"/>
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M2 2L14 14M6.5 6.7C6.2 7 6 7.5 6 8C6 9.1 6.9 10 8 10C8.5 10 8.9 9.8 9.2 9.5"/>
                    <path d="M4 4.5C2.5 5.5 1.5 7 1 8C1.5 9 3.5 13 8 13C9.5 13 10.8 12.5 11.8 11.8"/>
                    <path d="M12.5 10C13.5 9 14.5 8 15 8C14.5 7 12.5 3 8 3C7 3 6 3.3 5.2 3.7"/>
                  </svg>
                </button>
              </div>
            </div>
            <div v-if="passwordMsg" :class="['msg', passwordMsg.type]">{{ passwordMsg.text }}</div>
            <button type="submit" class="btn-primary" :disabled="passwordLoading">
              {{ passwordLoading ? '修改中...' : '确认修改' }}
            </button>
          </form>
        </div>
      </div>

      <!-- 右列：运动档案 -->
      <div class="profile-col">
        <div class="card">
          <div class="card-header">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 10C3 6.13 6.13 3 10 3C13.87 3 17 6.13 17 10C17 13.87 13.87 17 10 17C6.13 17 3 13.87 3 10Z"/>
                <path d="M10 7V10L12 12" stroke-linecap="round"/>
                <path d="M1 10H3M17 10H19M10 1V3M10 17V19" stroke-linecap="round"/>
              </svg>
            </div>
            <h2 class="card-title">运动档案</h2>
          </div>

          <div v-if="profileLoading" class="loading-state">
            <div class="spinner"></div>
            <p>加载中...</p>
          </div>

          <form v-else @submit.prevent="saveProfile" class="form">
            <div class="form-row">
              <div class="form-group">
                <label>年龄段</label>
                <select v-model="profileForm.age_range">
                  <option value="">请选择</option>
                  <option value="under_18">18岁以下</option>
                  <option value="18_25">18-25岁</option>
                  <option value="26_35">26-35岁</option>
                  <option value="36_45">36-45岁</option>
                  <option value="46_55">46-55岁</option>
                  <option value="over_55">55岁以上</option>
                </select>
              </div>
              <div class="form-group">
                <label>性别</label>
                <select v-model="profileForm.gender">
                  <option value="">请选择</option>
                  <option value="female">女</option>
                  <option value="male">男</option>                 
                  <option value="other">其他</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>身高 (cm)</label>
                <input v-model.number="profileForm.height_cm" type="number" placeholder="如：170" min="100" max="250" />
              </div>
              <div class="form-group">
                <label>体重 (kg)</label>
                <input v-model.number="profileForm.weight_kg" type="number" placeholder="如：65" min="30" max="200" step="0.1" />
              </div>
            </div>

            <!-- BMI 显示 -->
            <div v-if="bmi" class="bmi-card" :class="bmiCategory.level">
              <div class="bmi-value">BMI: {{ bmi }}</div>
              <div class="bmi-label">{{ bmiCategory.label }}</div>
            </div>

            <div class="form-group">
              <label>训练目标</label>
              <select v-model="profileForm.goal">
                <option value="">请选择</option>
                <option value="lose_weight">减脂塑形</option>
                <option value="build_muscle">增肌增重</option>
                <option value="improve_endurance">提升耐力</option>
                <option value="improve_strength">增强力量</option>
                <option value="stay_healthy">保持健康</option>
                <option value="sport_performance">运动表现</option>
              </select>
            </div>

            <div class="form-group">
              <label>运动水平</label>
              <select v-model="profileForm.fitness_level">
                <option value="">请选择</option>
                <option value="beginner">初学者 - 很少运动</option>
                <option value="intermediate">中级 - 每周运动2-3次</option>
                <option value="advanced">高级 - 每周运动4次以上</option>
              </select>
            </div>

            <div class="form-group">
              <label>偏好运动方式</label>
              <select v-model="profileForm.preferred_method">
                <option value="">请选择</option>
                <option value="gym">健身房训练</option>
                <option value="outdoor">户外运动</option>
                <option value="home">居家训练</option>
                <option value="mixed">综合训练</option>
              </select>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>每周训练天数</label>
                <select v-model.number="profileForm.weekly_days">
                  <option value="">请选择</option>
                  <option v-for="d in 7" :key="d" :value="d">{{ d }} 天</option>
                </select>
              </div>
              <div class="form-group">
                <label>每次时长 (分钟)</label>
                <input v-model.number="profileForm.daily_duration" type="number" placeholder="如：60" min="10" max="300" />
              </div>
            </div>

            <div class="form-group">
              <label>训练强度偏好</label>
              <div class="intensity-group">
                <label
                  v-for="opt in intensityOptions"
                  :key="opt.value"
                  class="intensity-option"
                  :class="{ active: profileForm.intensity_level === opt.value }"
                >
                  <input type="radio" v-model="profileForm.intensity_level" :value="opt.value" />
                  <span class="intensity-dot" :class="opt.value"></span>
                  {{ opt.label }}
                </label>
              </div>
            </div>

            <div class="form-group">
              <label>是否有运动损伤</label>
              <div class="radio-group">
                <label class="radio-label" :class="{ active: profileForm.injury_status === 'none' }">
                  <input type="radio" v-model="profileForm.injury_status" value="none" />
                  <span>无</span>
                </label>
                <label class="radio-label" :class="{ active: profileForm.injury_status === 'minor' }">
                  <input type="radio" v-model="profileForm.injury_status" value="minor" />
                  <span>轻微</span>
                </label>
                <label class="radio-label" :class="{ active: profileForm.injury_status === 'moderate' }">
                  <input type="radio" v-model="profileForm.injury_status" value="moderate" />
                  <span>中度</span>
                </label>
                <label class="radio-label" :class="{ active: profileForm.injury_status === 'severe' }">
                  <input type="radio" v-model="profileForm.injury_status" value="severe" />
                  <span>严重</span>
                </label>
              </div>
            </div>

            <div class="form-group" v-if="profileForm.injury_status && profileForm.injury_status !== 'none'">
              <label>损伤详情</label>
              <textarea
                v-model="profileForm.injury_detail"
                placeholder="请描述损伤部位及情况..."
                rows="3"
              ></textarea>
            </div>

            <div v-if="profileMsg" :class="['msg', profileMsg.type]">{{ profileMsg.text }}</div>

            <button type="submit" class="btn-primary" :disabled="profileSaving">
              {{ profileSaving ? '保存中...' : '保存运动档案' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const authStore = useAuthStore()
const user = computed(() => authStore.user)

// 头像
const fileInputRef = ref(null)
const avatarUploading = ref(false)
const avatarUrl = computed(() => {
  const url = user.value?.avatar_url
  if (!url) return null
  // 已是完整 URL（含 http）则直接用，否则加代理前缀
  return url.startsWith('http') ? url : `/avatars/${url.replace(/^\/avatars\//, '')}`
})

// 账户信息
const accountForm = ref({ username: '', email: '' })
const accountLoading = ref(false)
const accountMsg = ref(null)

// 密码修改
const passwordForm = ref({ currentPassword: '', newPassword: '', confirmPassword: '' })
const passwordLoading = ref(false)
const passwordMsg = ref(null)
const showCurrentPwd = ref(false)
const showNewPwd = ref(false)
const showConfirmPwd = ref(false)

// 运动档案
const profileLoading = ref(true)
const profileSaving = ref(false)
const profileMsg = ref(null)
const profileForm = ref({
  age_range: '',
  gender: '',
  height_cm: null,
  weight_kg: null,
  goal: '',
  fitness_level: '',
  preferred_method: '',
  weekly_days: '',
  daily_duration: null,
  intensity_level: '',
  injury_status: '',
  injury_detail: '',
  profile_source: 'manual'
})

const intensityOptions = [
  { value: 'low', label: '低强度' },
  { value: 'medium', label: '中强度' },
  { value: 'high', label: '高强度' }
]

const avatarLetter = computed(() => {
  const name = user.value?.username || '用'
  return name.charAt(0).toUpperCase()
})

const bmi = computed(() => {
  const h = profileForm.value.height_cm
  const w = profileForm.value.weight_kg
  if (!h || !w || h <= 0) return null
  return (w / ((h / 100) ** 2)).toFixed(1)
})

const bmiCategory = computed(() => {
  const v = parseFloat(bmi.value)
  if (isNaN(v)) return { label: '', level: '' }
  if (v < 18.5) return { label: '偏瘦', level: 'bmi-low' }
  if (v < 24) return { label: '正常', level: 'bmi-normal' }
  if (v < 28) return { label: '超重', level: 'bmi-warning' }
  return { label: '肥胖', level: 'bmi-danger' }
})

const showMsg = (ref, type, text, duration = 3000) => {
  ref.value = { type, text }
  setTimeout(() => { ref.value = null }, duration)
}

onMounted(async () => {
  accountForm.value.username = user.value?.username || ''
  accountForm.value.email = user.value?.email || ''
  await loadProfile()
})

async function loadProfile() {
  try {
    const data = await api.getMyProfile()
    if (data && Object.keys(data).length > 0) {
      Object.assign(profileForm.value, data)
    }
  } catch (e) {
    console.error('加载运动档案失败', e)
  } finally {
    profileLoading.value = false
  }
}

async function saveAccountInfo() {
  if (!accountForm.value.username.trim()) {
    showMsg(accountMsg, 'error', '用户名不能为空')
    return
  }
  if (!accountForm.value.email.trim()) {
    showMsg(accountMsg, 'error', '邮箱不能为空')
    return
  }
  accountLoading.value = true
  try {
    const data = await api.put('/auth/update-account', {
      username: accountForm.value.username.trim(),
      email: accountForm.value.email.trim()
    })
    if (data?.success) {
      if (authStore.user) {
        authStore.user.username = accountForm.value.username.trim()
        authStore.user.email = accountForm.value.email.trim()
        localStorage.setItem('user', JSON.stringify(authStore.user))
      }
      showMsg(accountMsg, 'success', '保存成功')
    } else {
      showMsg(accountMsg, 'error', data?.message || '保存失败')
    }
  } catch (e) {
    showMsg(accountMsg, 'error', e?.response?.data?.detail || '保存失败，请稍后重试')
  } finally {
    accountLoading.value = false
  }
}

async function changePassword() {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showMsg(passwordMsg, 'error', '两次输入的新密码不一致')
    return
  }
  if (passwordForm.value.newPassword.length < 6) {
    showMsg(passwordMsg, 'error', '新密码长度不能少于6位')
    return
  }
  passwordLoading.value = true
  try {
    const data = await api.changePassword(
      passwordForm.value.currentPassword,
      passwordForm.value.newPassword
    )
    if (data?.success) {
      passwordForm.value = { currentPassword: '', newPassword: '', confirmPassword: '' }
      showMsg(passwordMsg, 'success', '密码修改成功')
    } else {
      showMsg(passwordMsg, 'error', data?.message || '修改失败')
    }
  } catch (e) {
    showMsg(passwordMsg, 'error', e?.response?.data?.detail || '修改失败，请稍后重试')
  } finally {
    passwordLoading.value = false
  }
}

async function saveProfile() {
  profileSaving.value = true
  try {
    const payload = { ...profileForm.value, profile_source: 'manual' }
    const data = await api.updateMyProfile(payload)
    if (data?.status === 'success') {
      showMsg(profileMsg, 'success', '运动档案已保存')
    } else {
      showMsg(profileMsg, 'error', '保存失败，请稍后重试')
    }
  } catch (e) {
    showMsg(profileMsg, 'error', '保存失败，请稍后重试')
  } finally {
    profileSaving.value = false
  }
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function handleAvatarChange(e) {
  const file = e.target.files?.[0]
  if (!file) return

  avatarUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const data = await api.uploadAvatar(formData)
    if (data?.success) {
      if (authStore.user) {
        authStore.user.avatar_url = data.avatar_url
        localStorage.setItem('user', JSON.stringify(authStore.user))
      }
      showMsg(accountMsg, 'success', '头像更新成功')
    } else {
      showMsg(accountMsg, 'error', data?.message || '上传失败')
    }
  } catch (e) {
    showMsg(accountMsg, 'error', '上传失败，请稍后重试')
  } finally {
    avatarUploading.value = false
    e.target.value = ''
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 32px;
}

.page-header {
  margin-bottom: 32px;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  margin-bottom: 16px;
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: var(--color-bg);
  color: var(--color-text-primary);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 6px 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 两列布局 */
.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
}

.profile-col {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片 */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 24px;
}

.card-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

/* 头像区 */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--color-bg);
  border-radius: 10px;
  margin-bottom: 20px;
}

.avatar-wrapper {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  cursor: pointer;
  flex-shrink: 0;
}

.avatar-wrapper:hover .avatar-overlay,
.avatar-wrapper.uploading .avatar-overlay {
  opacity: 1;
}

.avatar-img {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.avatar-circle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-letter {
  font-size: 22px;
  font-weight: 600;
  color: #64748b;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.avatar-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.hidden-input {
  display: none;
}

.avatar-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 2px 0;
}

.avatar-role {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0 0 2px 0;
}

.avatar-hint {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin: 0;
  opacity: 0.7;
}

/* 表单 */
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: var(--color-surface);
  transition: border-color 0.2s;
  font-family: inherit;
  outline: none;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}


.field-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
}

/* 密码输入 */
.password-input {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input input {
  width: 100%;
  padding-right: 40px;
}

.eye-btn {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  padding: 4px;
}

.eye-btn:hover {
  color: var(--color-text-primary);
}

/* BMI */
.bmi-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
}

.bmi-value {
  font-weight: 700;
  font-size: 16px;
}

.bmi-low { background: #e3f2fd; color: #1565c0; }
.bmi-normal { background: #e8f5e9; color: #2e7d32; }
.bmi-warning { background: #fff3e0; color: #e65100; }
.bmi-danger { background: #fce4ec; color: #c62828; }

/* 强度选择 */
.intensity-group {
  display: flex;
  gap: 10px;
}

.intensity-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.intensity-option.active {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(102, 126, 234, 0.06);
}

.intensity-option input {
  display: none;
}

.intensity-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.intensity-dot.low { background: #4caf50; }
.intensity-dot.medium { background: #ff9800; }
.intensity-dot.high { background: #f44336; }

/* 损伤单选 */
.radio-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.radio-label.active {
  border-color: var(--color-accent);
  color: var(--color-accent);
  background: rgba(102, 126, 234, 0.06);
}

.radio-label input {
  display: none;
}

/* 消息提示 */
.msg {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
}

.msg.success {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
}

.msg.error {
  background: #fce4ec;
  color: #c62828;
  border: 1px solid #ef9a9a;
}

/* 按钮 */
.btn-primary {
  padding: 11px 20px;
  background: var(--color-accent, #667eea);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }

  .profile-page {
    padding: 24px 16px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
