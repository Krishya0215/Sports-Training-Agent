<template>
  <div class="questionnaire-page">
    <Navbar />

    <div class="questionnaire-shell">
      <header class="questionnaire-header">
        <router-link to="/chat" class="back-btn" aria-label="返回 AI 教练">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </router-link>
        <div class="header-copy">
          <div class="coach-tag">AI 教练</div>
          <h1>{{ currentQuestion.title }}</h1>
          <p>{{ currentQuestion.subtitle }}</p>
        </div>
      </header>

      <section class="questionnaire-card">
        <div class="options-grid">
          <button
            v-for="option in currentQuestion.options"
            :key="option.value"
            class="option-card"
            :class="{ selected: currentQuestion.answer === option.value }"
            @click="selectOption(option.value)"
          >
            <span>{{ option.label }}</span>
          </button>
        </div>

        <div v-if="currentQuestion.key === 'injury' && currentQuestion.answer === 'other'" class="form-field">
          <label for="injury-detail">请输入具体伤病情况</label>
          <textarea
            id="injury-detail"
            v-model.trim="questionnaire.injury_detail"
            rows="3"
            placeholder="例如：膝盖疼痛、腰部不适、肩部活动受限"
          />
        </div>

        <footer class="footer-actions">
          <button class="btn btn-ghost" :disabled="stepIndex === 0 || loading" @click="prevStep">上一步</button>
          <button class="btn btn-primary" :disabled="!canProceed || loading" @click="nextStep">
            {{ stepIndex === questions.length - 1 ? (loading ? '正在跳转...' : '生成计划') : '下一步' }}
          </button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const PRESELECTED_GOAL_KEY = 'selectedTrainingGoal'

const router = useRouter()
const stepIndex = ref(0)
const loading = ref(false)

const questionnaire = ref({
  goal: '',
  method: '',
  weekly_days: '',
  daily_duration: '',
  intensity: '',
  injury: '',
  injury_detail: ''
})

const questions = [
  {
    key: 'goal',
    title: '你的训练目标是什么？',
    subtitle: '选择一个最符合你当前需求的目标',
    options: [
      { label: '全身减脂减重', value: '全身减脂减重' },
      { label: '局部塑形紧致', value: '局部塑形紧致' },
      { label: '增肌与线条提升', value: '增肌与线条提升' },
      { label: '改善体态与核心', value: '改善体态与核心' },
      { label: '保持身体健康', value: '保持身体健康' }
    ]
  },
  {
    key: 'method',
    title: '你更想采用哪种训练方式？',
    subtitle: '选择一个你最愿意坚持的主要训练方式',
    options: [
      { label: '户外跑步', value: '户外跑步' },
      { label: '燃脂 HIIT', value: '燃脂 HIIT' },
      { label: '跳绳', value: '跳绳' },
      { label: '健身操', value: '健身操' },
      { label: '瑜伽', value: '瑜伽' },
      { label: '舞蹈有氧', value: '舞蹈有氧' },
      { label: '椭圆机', value: '椭圆机' },
      { label: '跑步机', value: '跑步机' },
      { label: '室内走路', value: '室内走路' },
      { label: '动感单车', value: '动感单车' },
      { label: '划船机', value: '划船机' }
    ]
  },
  {
    key: 'weekly_days',
    title: '你每周能训练几天？',
    subtitle: '系统会根据这个频率安排一个月训练日程',
    options: [1, 2, 3, 4, 5, 6, 7].map((value) => ({
      label: `每周 ${value} 天`,
      value: String(value)
    }))
  },
  {
    key: 'daily_duration',
    title: '你每天能训练多长时间？',
    subtitle: '请选择一个你更容易长期坚持的时长',
    options: [10, 20, 30, 40, 60].map((value) => ({
      label: `${value} 分钟左右`,
      value: String(value)
    }))
  },
  {
    key: 'intensity',
    title: '你能接受的训练强度是？',
    subtitle: 'AI 会根据强度调整动作难度和恢复安排',
    options: [
      { label: 'K1 零基础', value: 'K1 零基础' },
      { label: 'K2-K3 中低强度', value: 'K2-K3 中低强度' },
      { label: 'K3-K4 中高强度', value: 'K3-K4 中高强度' },
      { label: 'K4-K5 高强度', value: 'K4-K5 高强度' }
    ]
  },
  {
    key: 'injury',
    title: '你是否存在伤病困扰？',
    subtitle: '如有不适，AI 会自动规避高风险动作',
    options: [
      { label: '不存在伤病困扰', value: '无伤病困扰' },
      { label: '膝盖', value: '膝盖' },
      { label: '腰部', value: '腰部' },
      { label: '肩部', value: '肩部' },
      { label: '手腕', value: '手腕' },
      { label: '其他情况', value: 'other' }
    ]
  }
]

const currentQuestion = computed(() => {
  const question = questions[stepIndex.value]
  return {
    ...question,
    answer: questionnaire.value[question.key]
  }
})

const canProceed = computed(() => {
  if (!currentQuestion.value.answer) return false
  if (currentQuestion.value.key === 'injury' && currentQuestion.value.answer === 'other') {
    return Boolean(questionnaire.value.injury_detail)
  }
  return true
})

const selectOption = (value) => {
  questionnaire.value[currentQuestion.value.key] = value
}

const parseWeeklyDaysLimit = (value) => {
  const match = String(value ?? '').match(/\d+/)
  const parsed = match ? Number(match[0]) : NaN
  if (!Number.isFinite(parsed) || parsed <= 0) return 1
  return Math.min(parsed, 7)
}

const buildWeeklyTrainingDayTemplate = (weeklyDaysValue) => {
  const weeklyDays = parseWeeklyDaysLimit(weeklyDaysValue)
  const lines = []

  for (let index = 1; index <= weeklyDays; index += 1) {
    lines.push(`### 训练日${index}`)
    lines.push('- 训练主题：')
    lines.push('- 建议时长：')
    lines.push('- 训练重点：')
    lines.push('- 恢复建议：')
    lines.push('- 替代方案：如无伤病风险不用写')
    lines.push('')
  }

  return lines
}

const prevStep = () => {
  if (stepIndex.value > 0) stepIndex.value -= 1
}

const buildPrompt = () => {
  const injuryText =
    questionnaire.value.injury === 'other'
      ? `其他伤病：${questionnaire.value.injury_detail}`
      : questionnaire.value.injury
  const weeklyTrainingDayTemplate = buildWeeklyTrainingDayTemplate(questionnaire.value.weekly_days)

  return [
    '请你扮演专业 AI 运动教练，根据以下用户问卷信息生成一个 1 个月训练计划。',
    '输出格式要求：',
    '1. 先输出“计划标题”和“计划概述”两个部分。',
    '2. 训练主体必须按周展开，尽量细化到完整 4 周；每周下再按训练日展开。',
    '3. 每个训练日都必须明确写出：训练主题、建议时长、训练重点、恢复建议。',
    '4. 如果用户有伤病困扰，必须主动规避高风险动作，并在对应训练日中写出替代方案或调整建议。',
    '5. 保持结构化输出，标题清晰，便于后续按卡片和训练日详情解析。',
    '6. 不要只给原则性建议，必须给出可执行的每日安排。',
    '7. 不要使用 ---、*** 这类生硬分隔线，统一使用 Markdown 标题层级和空行来分段。',
    '8. 在用户还没有手动选择每周训练日之前，不要擅自写“周一训练日”“周四训练日”这类具体周几，只能使用“训练日1 / 训练日2”这类通用编号。',
    '9. 训练日标题禁止出现括号或连字符补充说明，例如不要写“训练日1（周一）”“训练日2(周四)”或“训练日1-周一”，只保留“训练日1”“训练日2”。',
    '',
    '请严格遵循下面的标准 Markdown 输出骨架：',
    '# 计划标题（只需要给出标题即可，不要带有“计划标题”这几个字）',
    '',
    '## 计划概述',
    '这里写目标、周期、每周频次、强度和注意事项。',
    '',
    '## 第1周',
    '',
    ...weeklyTrainingDayTemplate,
    '',
    '## 第2周',
    '...',
    '',
    '用户信息：',
    `- 训练目标：${questionnaire.value.goal}`,
    `- 偏好训练方式：${questionnaire.value.method}`,
    `- 每周训练天数：${questionnaire.value.weekly_days} 天`,
    `- 单次训练时长：${questionnaire.value.daily_duration} 分钟`,
    `- 可接受强度：${questionnaire.value.intensity}`,
    `- 伤病情况：${injuryText}`
  ].join('\n')
}

const buildRequestMessage = () => {
  const injuryText =
    questionnaire.value.injury === 'other'
      ? questionnaire.value.injury_detail
      : questionnaire.value.injury

  return [
    '请根据我的问卷生成一个 1 个月训练计划。',
    `目标：${questionnaire.value.goal || '未设置'}`,
    `方式：${questionnaire.value.method || '未设置'}`,
    `频率：每周 ${questionnaire.value.weekly_days || '未设置'} 天`,
    `时长：每次 ${questionnaire.value.daily_duration || '未设置'} 分钟`,
    `强度：${questionnaire.value.intensity || '未设置'}`,
    `伤病情况：${injuryText || '无伤病困扰'}`
  ].join('\n')
}

const nextStep = async () => {
  if (!canProceed.value || loading.value) return

  if (stepIndex.value < questions.length - 1) {
    stepIndex.value += 1
    return
  }

  loading.value = true

  const prompt = buildPrompt()
  const requestMessage = buildRequestMessage()

  try {
    await api.initializeProfile({
      goal: questionnaire.value.goal || null,
      preferred_method: questionnaire.value.method || null,
      weekly_days: parseWeeklyDaysLimit(questionnaire.value.weekly_days),
      daily_duration: Number(questionnaire.value.daily_duration || 0) || null,
      intensity_level: questionnaire.value.intensity || null,
      injury_status: questionnaire.value.injury || null,
      injury_detail: questionnaire.value.injury_detail || null,
      profile_source: 'training_questionnaire'
    })
  } catch (error) {
    console.error('初始化用户画像失败，将继续生成训练计划:', error)
  }

  sessionStorage.setItem(
    'pendingTrainingPrompt',
    JSON.stringify({
      prompt,
      requestMessage,
      questionnaire: { ...questionnaire.value },
      createdAt: new Date().toISOString()
    })
  )

  try {
    await router.push({ name: 'Chat', query: { autoPlan: '1' } })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  try {
    const raw = sessionStorage.getItem(PRESELECTED_GOAL_KEY)
    if (!raw) return

    const preselectedGoal = JSON.parse(raw)
    if (preselectedGoal?.name) {
      questionnaire.value.goal = preselectedGoal.name
      stepIndex.value = 1
    }
    sessionStorage.removeItem(PRESELECTED_GOAL_KEY)
  } catch (error) {
    console.error('读取预选目标失败:', error)
  }
})
</script>

<style scoped>
.questionnaire-page {
  min-height: 100vh;
  background:
    radial-gradient(circle at top left, rgba(82, 223, 177, 0.18), transparent 28%),
    linear-gradient(180deg, #f7fbfa 0%, #eef7f4 100%);
  padding: 24px 16px 48px;
}

.questionnaire-shell {
  width: min(100%, 760px);
  margin: 0 auto;
}

.questionnaire-header {
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

.header-copy h1 {
  margin: 0 0 10px;
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.15;
  color: #132320;
}

.header-copy p {
  margin: 0;
  color: #67817a;
  font-size: 15px;
}

.questionnaire-card {
  background: rgba(255, 255, 255, 0.94);
  border-radius: 28px;
  padding: 28px 24px;
  box-shadow: 0 24px 60px rgba(36, 74, 63, 0.12);
  backdrop-filter: blur(14px);
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.option-card {
  border: 1px solid #e8f0ed;
  background: #fff;
  border-radius: 18px;
  min-height: 84px;
  padding: 18px 16px;
  text-align: left;
  font-size: 16px;
  font-weight: 700;
  color: #223431;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
}

.option-card:hover {
  transform: translateY(-2px);
  border-color: rgba(54, 209, 149, 0.5);
  box-shadow: 0 10px 24px rgba(52, 199, 137, 0.12);
}

.option-card.selected {
  border-color: #34c98b;
  background: linear-gradient(135deg, rgba(52, 201, 139, 0.12), rgba(52, 201, 139, 0.04));
  color: #118559;
}

.form-field {
  margin-top: 20px;
}

.form-field label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 700;
  color: #223431;
}

.form-field textarea {
  width: 100%;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid #dfeae5;
  resize: vertical;
  font: inherit;
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 28px;
}

.btn {
  flex: 1;
  border: none;
  border-radius: 999px;
  min-height: 54px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.btn-ghost {
  background: #fff;
  border: 1px solid #8fe6c3;
  color: #34b981;
}

.btn-primary {
  background: linear-gradient(135deg, #4adea0, #34c98b);
  color: #fff;
  box-shadow: 0 14px 28px rgba(52, 201, 139, 0.24);
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  box-shadow: none;
}

@media (max-width: 640px) {
  .questionnaire-card {
    padding: 22px 18px;
  }

  .options-grid {
    grid-template-columns: 1fr;
  }

  .footer-actions {
    flex-direction: column;
  }
}
</style>
