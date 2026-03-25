<template>
  <div class="analytics-page">
    <Navbar />
    <div class="page-content">
      <div class="page-header">
        <h1>📊 数据分析</h1>
        <div class="period-selector">
          <button
            v-for="period in periods"
            :key="period.value"
            :class="['period-btn', { active: selectedPeriod === period.value }]"
            @click="selectedPeriod = period.value; loadData()"
          >
            {{ period.label }}
          </button>
        </div>
      </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🏃</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_trainings }}</div>
          <div class="stat-label">总训练次数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏱</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_duration }}</div>
          <div class="stat-label">总时长（分钟）</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💪</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.average_fatigue }}</div>
          <div class="stat-label">平均疲劳度</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-content">
          <div class="stat-value">{{ weeklyAverage }}</div>
          <div class="stat-label">周均训练次数</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 训练频率趋势 -->
      <div class="chart-card">
        <h3>📈 训练频率趋势</h3>
        <div class="chart-container">
          <canvas ref="frequencyChart"></canvas>
        </div>
      </div>

      <!-- 训练负荷变化 -->
      <div class="chart-card">
        <h3>📉 训练负荷变化</h3>
        <div class="chart-container">
          <canvas ref="loadChart"></canvas>
        </div>
      </div>

      <!-- 训练类型分布 -->
      <div class="chart-card">
        <h3>🎯 训练类型分布</h3>
        <div class="type-distribution">
          <div
            v-for="(count, type) in summary.training_types"
            :key="type"
            class="type-item"
          >
            <div class="type-bar-container">
              <div class="type-label">{{ type }}</div>
              <div class="type-bar">
                <div
                  class="type-bar-fill"
                  :style="{ width: (count / summary.total_trainings * 100) + '%' }"
                ></div>
              </div>
              <div class="type-count">{{ count }}次</div>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed, nextTick } from 'vue'
import Navbar from '../components/Navbar.vue'
import api from '../api'

export default {
  name: 'Analytics',
  setup() {
    const selectedPeriod = ref('week')
    const periods = [
      { label: '最近7天', value: 'week' },
      { label: '最近30天', value: 'month' },
      { label: '最近90天', value: 'quarter' }
    ]

    const summary = ref({
      total_trainings: 0,
      total_duration: 0,
      average_fatigue: 0,
      training_types: {}
    })

    const frequencyData = ref({ dates: [], counts: [] })
    const loadData_ref = ref({ dates: [], loads: [] })

    const frequencyChart = ref(null)
    const loadChart = ref(null)
    let frequencyChartInstance = null
    let loadChartInstance = null

    const weeklyAverage = computed(() => {
      const days = selectedPeriod.value === 'week' ? 7 : selectedPeriod.value === 'month' ? 30 : 90
      return (summary.value.total_trainings / (days / 7)).toFixed(1)
    })

    const loadData = async () => {
      try {
        const days = selectedPeriod.value === 'week' ? 7 : selectedPeriod.value === 'month' ? 30 : 90

        // 加载统计摘要
        const summaryRes = await api.get(`/training/analytics/summary?period=${selectedPeriod.value}`)
        summary.value = summaryRes.data

        // 加载频率数据
        const frequencyRes = await api.get(`/training/analytics/frequency?days=${days}`)
        frequencyData.value = frequencyRes.data

        // 加载负荷数据
        const loadRes = await api.get(`/training/analytics/load?days=${days}`)
        loadData_ref.value = loadRes.data

        // 更新图表
        await nextTick()
        updateCharts()
      } catch (error) {
        console.error('加载数据失败:', error)
      }
    }

    const updateCharts = () => {
      // 简化的图表实现（实际应使用Chart.js或ECharts）
      // 这里仅作示例，实际项目中需要引入图表库
      console.log('更新图表:', frequencyData.value, loadData_ref.value)
      
      // 如果有Chart.js，可以这样使用：
      // if (frequencyChartInstance) frequencyChartInstance.destroy()
      // frequencyChartInstance = new Chart(frequencyChart.value, {...})
    }

    watch(selectedPeriod, () => {
      loadData()
    })

    onMounted(() => {
      loadData()
    })

    return {
      selectedPeriod,
      periods,
      summary,
      weeklyAverage,
      frequencyChart,
      loadChart,
      loadData
    }
  }
}
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.page-content {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin: 0;
}

.period-selector {
  display: flex;
  gap: 0.5rem;
  background: #f5f5f5;
  padding: 0.25rem;
  border-radius: 8px;
}

.period-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #666;
}

.period-btn.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

/* 训练类型分布 */
.type-distribution {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.type-item {
  display: flex;
  align-items: center;
}

.type-bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.type-label {
  min-width: 80px;
  color: #666;
  font-size: 0.9rem;
}

.type-bar {
  flex: 1;
  height: 24px;
  background: #f0f0f0;
  border-radius: 12px;
  overflow: hidden;
}

.type-bar-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.type-count {
  min-width: 50px;
  text-align: right;
  color: #666;
  font-size: 0.9rem;
}
</style>
