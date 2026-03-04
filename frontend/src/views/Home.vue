<template>
  <div class="home">
    <Navbar />
    
    <div class="container">
      <div class="hero">
        <h1 class="hero-title">运动训练知识问答</h1>
        <p class="hero-subtitle">基于AI的智能运动训练助手，为您提供专业的训练指导</p>
        <div class="hero-actions">
          <button class="btn btn-primary" @click="$router.push('/chat')">开始问答</button>
          <button class="btn btn-secondary" @click="$router.push('/knowledge')">浏览知识库</button>
        </div>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.documents }}</div>
            <div class="stat-label">知识文档</div>
          </div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.queries }}</div>
            <div class="stat-label">问答次数</div>
          </div>
        </div>
        
        <div class="stat-card card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M20 7H4C2.89543 7 2 7.89543 2 9V19C2 20.1046 2.89543 21 4 21H20C21.1046 21 22 20.1046 22 19V9C22 7.89543 21.1046 7 20 7Z" stroke="currentColor" stroke-width="2"/>
              <path d="M16 7V5C16 3.89543 15.1046 3 14 3H10C8.89543 3 8 3.89543 8 5V7" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.memory }}</div>
            <div class="stat-label">记忆条目</div>
          </div>
        </div>
      </div>
      
      <div class="features">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card card">
            <div class="feature-icon">🤖</div>
            <h3 class="feature-title">智能问答</h3>
            <p class="feature-desc">基于RAG技术的智能问答系统，提供准确的运动训练指导</p>
          </div>
          
          <div class="feature-card card">
            <div class="feature-icon">📚</div>
            <h3 class="feature-title">知识库管理</h3>
            <p class="feature-desc">支持PDF、Markdown等多种格式，智能处理和索引</p>
          </div>
          
          <div class="feature-card card">
            <div class="feature-icon">🧠</div>
            <h3 class="feature-title">多层记忆</h3>
            <p class="feature-desc">工作记忆、情景记忆、语义记忆，提供上下文感知</p>
          </div>
          
          <div class="feature-card card">
            <div class="feature-icon">🔍</div>
            <h3 class="feature-title">高级检索</h3>
            <p class="feature-desc">多查询扩展和假设文档嵌入，提升检索精度</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const stats = ref({
  documents: 0,
  queries: 0,
  memory: 0
})

onMounted(async () => {
  try {
    const summary = await api.getMemorySummary()
    stats.value = {
      documents: summary.perceptual_documents || 0,
      queries: summary.episodic_memory_size || 0,
      memory: summary.working_memory_size || 0
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
})
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 32px;
}

.hero {
  text-align: center;
  margin-bottom: 80px;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 20px;
  color: var(--color-text-secondary);
  margin-bottom: 32px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 80px;
}

.stat-card {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-accent);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.section-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 32px;
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.feature-card {
  padding: 32px;
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.feature-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .stats-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-title {
    font-size: 36px;
  }
}
</style>
