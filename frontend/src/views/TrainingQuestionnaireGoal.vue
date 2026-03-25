<template>
  <div class="goal-page">
    <Navbar />

    <div class="goal-shell">
      <header class="goal-header">
        <router-link to="/chat" class="back-btn" aria-label="返回 AI 教练">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>

        <div>
          <div class="coach-tag">AI 教练 · 卡卡</div>
          <h1>你的运动目标是什么？</h1>
          <p>先告诉我你最关心的训练目标，我会带你进入更完整的问卷，最后生成专属训练计划。</p>
        </div>
      </header>

      <section class="goal-card">
        <div class="goal-list">
          <button
            v-for="goal in fitnessGoals"
            :key="goal.id"
            class="goal-item"
            :class="{ selected: selectedGoal === goal.id }"
            @click="selectGoal(goal.id)"
          >
            <div class="goal-icon">{{ goal.icon }}</div>
            <div class="goal-copy">
              <h3>{{ goal.name }}</h3>
              <p>{{ goal.description }}</p>
            </div>
          </button>
        </div>

        <button class="confirm-btn" :disabled="!selectedGoal" @click="handleConfirm">继续填写问卷</button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'

const PRESELECTED_GOAL_KEY = 'selectedTrainingGoal'

const router = useRouter()
const selectedGoal = ref(null)

const fitnessGoals = [
  {
    id: 'fat-loss',
    name: '全身减脂减重',
    icon: '燃',
    description: '更关注热量消耗、减脂效率和体重管理'
  },
  {
    id: 'local-toning',
    name: '局部塑形紧致',
    icon: '塑',
    description: '更关注局部线条、体态改善和紧致感'
  },
  {
    id: 'muscle-gain',
    name: '增肌与线条提升',
    icon: '力',
    description: '更关注力量增长、肌肉量和身体线条'
  },
  {
    id: 'body-shaping',
    name: '改善体态与核心',
    icon: '衡',
    description: '更关注姿态调整、核心稳定和灵活性'
  },
  {
    id: 'health-maintenance',
    name: '保持身体健康',
    icon: '健',
    description: '更关注体能提升、习惯养成和长期健康'
  }
]

const selectGoal = (goalId) => {
  selectedGoal.value = goalId
}

const handleConfirm = async () => {
  if (!selectedGoal.value) return

  const selectedGoalObj = fitnessGoals.find((goal) => goal.id === selectedGoal.value)
  sessionStorage.setItem(
    PRESELECTED_GOAL_KEY,
    JSON.stringify({
      id: selectedGoal.value,
      name: selectedGoalObj?.name || ''
    })
  )

  await router.push({ name: 'TrainingQuestionnaire' })
}
</script>

<style scoped>
.goal-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(97, 82, 223, 0.12), transparent 28%),
    linear-gradient(180deg, #f7fbfa 0%, #eef6f3 100%);
  padding: 24px 16px 48px;
}

.goal-shell {
  width: min(100%, 760px);
  margin: 0 auto;
}

.goal-header {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.back-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #1f2d2a;
  background: #f1f7f4;
  flex-shrink: 0;
}

.coach-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  background: rgba(97, 82, 223, 0.08);
  color: #6152df;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 14px;
}

.goal-header h1 {
  margin: 0 0 10px;
  font-size: clamp(28px, 4vw, 40px);
  color: #132320;
}

.goal-header p {
  margin: 0;
  color: #67817a;
  line-height: 1.7;
}

.goal-card {
  background: rgba(255, 255, 255, 0.94);
  border-radius: 28px;
  padding: 28px 24px;
  box-shadow: 0 24px 60px rgba(36, 74, 63, 0.12);
}

.goal-list {
  display: grid;
  gap: 14px;
}

.goal-item {
  width: 100%;
  padding: 18px;
  border: 1px solid #e8f0ed;
  border-radius: 20px;
  background: #fff;
  display: flex;
  gap: 16px;
  align-items: center;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.goal-item:hover {
  transform: translateY(-2px);
  border-color: rgba(54, 209, 149, 0.45);
  box-shadow: 0 10px 24px rgba(52, 199, 137, 0.12);
}

.goal-item.selected {
  border-color: #34c98b;
  background: linear-gradient(135deg, rgba(52, 201, 139, 0.12), rgba(52, 201, 139, 0.04));
}

.goal-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: #eef8f3;
  color: #179564;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
  flex-shrink: 0;
}

.goal-copy h3 {
  margin: 0 0 6px;
  color: #173029;
  font-size: 18px;
}

.goal-copy p {
  margin: 0;
  color: #6a847c;
  line-height: 1.6;
}

.confirm-btn {
  width: 100%;
  margin-top: 24px;
  min-height: 54px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #4adea0, #34c98b);
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 14px 28px rgba(52, 201, 139, 0.24);
  cursor: pointer;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

@media (max-width: 640px) {
  .goal-card {
    padding: 22px 18px;
  }

  .goal-item {
    align-items: flex-start;
  }
}
</style>
