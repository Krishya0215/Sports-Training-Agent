<template>
  <nav class="navbar" v-if="isAuthenticated">
    <div class="navbar-container">
      <div class="navbar-brand">
        <div class="logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="currentColor" stroke-width="2"/>
            <path d="M12 16L15 19L20 13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <span class="brand-text">运动训练助手</span>
      </div>

      <div class="navbar-menu">
        <router-link to="/chat" class="nav-item">AI教练</router-link>
        <router-link to="/training-plan" class="nav-item">训练计划</router-link>
        <router-link to="/training-record" class="nav-item">健康记录</router-link>
        <router-link v-if="isAdmin" to="/knowledge" class="nav-item">知识库管理</router-link>
        <!-- <router-link v-if="isAdmin" to="/memory" class="nav-item">记忆管理</router-link> -->
      </div>

      <div class="navbar-actions">
        <div class="user-menu" @click="toggleUserMenu" ref="userMenuRef">
          <div class="avatar">
            <img v-if="user?.avatar_url" :src="user.avatar_url" class="avatar-img" alt="头像" />
            <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <circle cx="10" cy="7" r="3"/>
              <path d="M4 18C4 14.6863 6.68629 12 10 12C13.3137 12 16 14.6863 16 18"/>
            </svg>
          </div>
          <div class="user-info">
            <span class="username">{{ user?.username || '用户' }}</span>
            <span class="email">{{ user?.email || '' }}</span>
          </div>

          <!-- 用户菜单下拉 -->
          <div class="user-dropdown" v-if="showUserMenu">
            <div class="dropdown-item" @click="goToProfile">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                <circle cx="8" cy="5" r="2.5"/>
                <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
              </svg>
              <span>个人资料</span>
            </div>
            <div class="dropdown-item" @click="handleLogout">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M6 12H3V4H6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M6 8H13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <path d="M10 5L13 8L10 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <span>退出登录</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const userMenuRef = ref(null)
const showUserMenu = ref(false)

// 计算属性
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)
const isAdmin = computed(() => user.value?.role === 'admin')

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const goToProfile = () => {
  showUserMenu.value = false
  router.push('/profile')
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('退出登录失败:', error)
  }
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navbar {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.8);
}

.navbar-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  color: var(--color-accent);
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.navbar-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  padding: 8px 16px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: var(--color-text-primary);
  background: var(--color-bg);
}

.nav-item.router-link-active {
  color: var(--color-text-primary);
  background: var(--color-bg);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background: var(--color-bg);
  color: var(--color-text-primary);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-md);
  position: relative;
  transition: all 0.2s ease;
}

.user-menu:hover {
  background: var(--color-bg);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  overflow: hidden;
}

.avatar-img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  display: block;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.email {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 160px;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  color: var(--color-text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background: var(--color-bg);
}

.dropdown-item svg {
  color: var(--color-text-secondary);
}
</style>
