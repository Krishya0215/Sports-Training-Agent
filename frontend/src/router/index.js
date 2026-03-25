import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/profile-setup',
    name: 'ProfileSetup',
    component: () => import('../views/ProfileSetup.vue'),
    meta: { requiresAuth: true, requiresProfileSetup: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/Chat.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/training-plan',
    name: 'TrainingPlan',
    component: () => import('../views/TrainingPlan.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/training-questionnaire',
    name: 'TrainingQuestionnaire',
    component: () => import('../views/TrainingQuestionnaire.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/training-record',
    name: 'TrainingRecord',
    component: () => import('../views/TrainingRecord.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: () => import('../views/Analytics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('../views/Knowledge.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/memory',
    name: 'Memory',
    component: () => import('../views/Memory.vue'),
    meta: { requiresAuth: true }
  },
  // 重定向到登录页
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 尝试恢复登录状态
  await authStore.verifyToken()

  const isAuthenticated = authStore.isAuthenticated
  const isFirstLogin = authStore.isFirstLogin && !authStore.profileCompleted

  // 检查是否需要认证
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
    return
  }

  // 检查是否需要访客状态（已登录用户访问登录/注册页）
  if (to.meta.requiresGuest && isAuthenticated) {
    // 如果首次登录且资料未完成，跳转到资料填写页
    if (isFirstLogin) {
      next('/profile-setup')
    } else {
      next('/')
    }
    return
  }

  // 检查是否需要填写资料
  if (to.meta.requiresProfileSetup && !isFirstLogin) {
    next('/')
    return
  }

  // 首次登录且资料未完成，强制跳转到资料填写页（除非已在资料填写页）
  if (isAuthenticated && isFirstLogin && to.name !== 'ProfileSetup') {
    next('/profile-setup')
    return
  }

  next()
})

export default router
