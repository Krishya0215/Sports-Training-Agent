<template>
  <div id="app">
    <router-view />
    <ProfileSetupModal
      v-if="showProfileModal"
      @complete="onProfileComplete"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from './stores/auth'
import ProfileSetupModal from './components/ProfileSetupModal.vue'

const authStore = useAuthStore()
const showProfileModal = computed(
  () => authStore.isAuthenticated && authStore.isFirstLogin && !authStore.profileCompleted
)
const onProfileComplete = () => {
  // authStore.profileCompleted 响应式更新后 showProfileModal 自动变 false
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  width: 100%;
  min-height: 100vh;
  background: #f5f5f7;
}
</style>
