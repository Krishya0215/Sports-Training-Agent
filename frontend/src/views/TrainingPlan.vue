<template>
  <div class="training-plan-page">
    <Navbar />

    <div class="page-container">
      <!-- 页面头部 -->
      <header class="page-header">
        <div class="header-content">
          <div class="header-text">
            <p class="header-label">Training Plans</p>
            <h1 class="header-title">{{ isDetailView ? '查看训练计划详情' : '管理你的训练计划' }}</h1>
            <p class="header-description">
              {{ isDetailView ? '先确认计划内容和训练日，再使用到日历中。' : '查看当前计划、切换历史计划，并在日历中查看每日训练内容。' }}
            </p>
          </div>
          <div class="header-actions">
            <button v-if="isDetailView" type="button" class="btn btn-outline" @click="goBoard">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              返回列表
            </button>
            <button type="button" class="btn btn-primary" @click="goCreatePlan">
              <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              创建新计划
            </button>
          </div>
        </div>
      </header>

      <!-- 详情视图 -->
      <template v-if="isDetailView && selectedPlan">
        <div class="detail-view">
          <!-- 详情侧边栏 -->
          <aside class="detail-sidebar">
            <div class="plan-card">
              <div class="plan-header">
                <div class="plan-badge-row">
                  <span v-if="selectedPlan.created_from_ai" class="badge badge-ai">AI 生成</span>
                  <span class="badge badge-method">{{ selectedPlan.metadata?.method || '综合训练' }}</span>
                </div>
                <h2 class="plan-title">{{ selectedPlan.title }}</h2>
                <p class="plan-subtitle">{{ planSubtitle(selectedPlan) }}</p>
              </div>

              <div class="plan-meta-grid">
                <div class="meta-item">
                  <div class="meta-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </div>
                  <div>
                    <p class="meta-label">训练目标</p>
                    <p class="meta-value">{{ selectedPlan.goal || 'AI 教练推荐' }}</p>
                  </div>
                </div>
                <div class="meta-item">
                  <div class="meta-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                  </div>
                  <div>
                    <p class="meta-label">计划周期</p>
                    <p class="meta-value">{{ formatDate(selectedPlan.start_date) }} - {{ formatDate(selectedPlan.end_date) }}</p>
                  </div>
                </div>
                <div class="meta-item">
                  <div class="meta-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </div>
                  <div>
                    <p class="meta-label">训练日</p>
                    <p class="meta-value">{{ getWeekdaysLabel(selectedPlan) }}</p>
                  </div>
                </div>
                <div class="meta-item">
                  <div class="meta-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
                    </svg>
                  </div>
                  <div>
                    <p class="meta-label">训练强度</p>
                    <p class="meta-value">{{ selectedPlan.metadata?.intensity || '中等' }}</p>
                  </div>
                </div>
              </div>

              <div class="plan-content">
                <h3 class="content-title">
                  <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                  计划内容
                </h3>
                <div class="content-body">
                  <pre>{{ removeMarkdownFormat(selectedPlan.content) }}</pre>
                </div>
              </div>

              <div class="plan-actions">
                <button type="button" class="btn btn-primary" @click="openWeekdayModal(selectedPlan)">
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  选择训练日
                </button>
                <div class="action-group">
                  <button type="button" class="btn btn-secondary" @click="openEditModal(selectedPlan)">
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    修改
                  </button>
                  <button type="button" class="btn btn-danger" @click="removePlan(selectedPlan)">
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                    删除
                  </button>
                </div>
              </div>
            </div>
          </aside>

          <!-- 详情主内容 -->
          <main class="detail-main">
            <div class="calendar-section">
              <div class="section-header">
                <h3>训练日历</h3>
                <div class="calendar-nav">
                  <button type="button" class="btn btn-icon" @click="changeMonth(-1)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M15 19l-7-7 7-7"/>
                    </svg>
                  </button>
                  <span class="calendar-title">{{ monthLabel }}</span>
                  <button type="button" class="btn btn-icon" @click="changeMonth(1)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M9 5l7 7-7 7"/>
                    </svg>
                  </button>
                </div>
              </div>

              <CalendarPanel
                :month-label="monthLabel"
                :weekday-headers="weekdayHeaders"
                :calendar-days="calendarDays"
                :entry-for-day="(day) => getTrainingEntry(selectedPlan, day)"
                @prev="changeMonth(-1)"
                @next="changeMonth(1)"
                @open-entry="openDetailEntry"
              />

              <div v-if="detailEntry" class="training-entry">
                <div class="entry-header">
                  <div>
                    <span class="entry-date">{{ formatDate(detailEntry.date) }}</span>
                    <h4>{{ detailEntry.title }}</h4>
                  </div>
                  <button type="button" class="btn btn-icon" @click="detailEntry = null">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
                <div class="entry-details">
                  <div class="detail-item">
                    <span class="detail-label">时长</span>
                    <span class="detail-value">{{ detailEntry.duration }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">训练重点</span>
                    <span class="detail-value">{{ detailEntry.focus }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">恢复建议</span>
                    <span class="detail-value">{{ detailEntry.recovery }}</span>
                  </div>
                  <div class="detail-item full-width">
                    <span class="detail-label">训练内容</span>
                    <p class="detail-text">{{ detailEntry.summary }}</p>
                  </div>
                </div>
              </div>
            </div>
          </main>
        </div>
      </template>

      <!-- 列表视图 -->
      <template v-else>
        <div v-if="currentPlan" class="dashboard-view">
          <div class="dashboard-grid">
            <!-- 左侧：当前计划概览 -->
            <div class="dashboard-sidebar">
              <div class="current-plan-card">
                <div class="plan-card-header">
                  <div>
                    <p class="card-label">Current Plan</p>
                    <h2 class="card-title">{{ currentPlan.title }}</h2>
                    <p class="card-subtitle">{{ planSubtitle(currentPlan) }}</p>
                  </div>
                  <div v-if="currentPlan.created_from_ai" class="badge badge-ai">AI 生成</div>
                </div>

                <div class="plan-tags">
                  <span class="tag">{{ currentPlan.metadata?.weekly_days ? `每周 ${currentPlan.metadata.weekly_days} 天` : '频率待定' }}</span>
                  <span class="tag">{{ currentPlan.metadata?.daily_duration ? `${currentPlan.metadata.daily_duration} 分钟` : '时长待定' }}</span>
                  <span class="tag">{{ currentPlan.metadata?.intensity || '强度待定' }}</span>
                  <span class="tag">{{ getWeekdaysLabel(currentPlan) }}</span>
                </div>

                <div class="plan-actions">
                  <button type="button" class="btn btn-primary" @click="openPlanDetail(currentPlan.id)">
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                    查看详情
                  </button>
                  <div class="action-group">
                    <button type="button" class="btn btn-secondary" @click="openEditModal(currentPlan)">
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                      </svg>
                      修改
                    </button>
                    <button type="button" class="btn btn-danger" @click="removePlan(currentPlan)">
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                      删除
                    </button>
                  </div>
                </div>
              </div>

              <!-- 训练内容面板 -->
              <div class="training-content-card">
                <div class="card-header">
                  <h3>训练内容</h3>
                </div>
                <div v-if="boardEntry" class="content-details">
                  <div class="detail-row">
                    <span class="detail-label">所属计划</span>
                    <span class="detail-value">{{ currentPlan.title }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">日期</span>
                    <span class="detail-value">{{ formatDate(boardEntry.date) }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">时长</span>
                    <span class="detail-value">{{ boardEntry.duration }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">训练重点</span>
                    <span class="detail-value">{{ boardEntry.focus }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">恢复建议</span>
                    <span class="detail-value">{{ boardEntry.recovery }}</span>
                  </div>
                  <div class="detail-row">
                    <span class="detail-label">训练内容</span>
                    <p class="detail-text">{{ boardEntry.summary }}</p>
                  </div>
                </div>
                <div v-else class="content-empty">
                  <div class="empty-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                    </svg>
                  </div>
                  <p>点击日历中的训练日查看详细内容</p>
                  <p class="empty-hint">只有确认后的训练日才会显示训练内容</p>
                </div>
              </div>
            </div>

            <!-- 中间：日历 -->
            <div class="dashboard-main">
              <div class="calendar-card">
                <div class="calendar-header">
                  <h3>训练日历</h3>
                  <div class="calendar-nav">
                    <button type="button" class="btn btn-icon" @click="changeMonth(-1)">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M15 19l-7-7 7-7"/>
                      </svg>
                    </button>
                    <span class="calendar-title">{{ monthLabel }}</span>
                    <button type="button" class="btn btn-icon" @click="changeMonth(1)">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 5l7 7-7 7"/>
                      </svg>
                    </button>
                  </div>
                </div>

                <CalendarPanel
                  :month-label="monthLabel"
                  :weekday-headers="weekdayHeaders"
                  :calendar-days="calendarDays"
                  :entry-for-day="(day) => getTrainingEntry(currentPlan, day)"
                  @prev="changeMonth(-1)"
                  @next="changeMonth(1)"
                  @open-entry="openBoardEntry"
                />
              </div>
            </div>

            <!-- 右侧：历史计划 -->
            <div class="dashboard-sidebar">
              <div class="history-card">
                <div class="card-header">
                  <h3>历史训练计划</h3>
                </div>

                <div v-if="historyPlans.length" class="history-list">
                  <div v-for="plan in historyPlans" :key="plan.id" class="history-item">
                    <div class="history-item-header">
                      <div>
                        <h4>{{ plan.title }}</h4>
                        <p class="item-subtitle">{{ plan.goal || 'AI 教练推荐' }}</p>
                      </div>
                      <div v-if="plan.created_from_ai" class="badge badge-ai small">AI</div>
                    </div>

                    <div class="item-tags">
                      <span class="tag small">{{ getWeekdaysLabel(plan) }}</span>
                      <span class="tag small">{{ plan.metadata?.intensity || '强度待定' }}</span>
                    </div>

                    <div class="item-actions">
                      <button type="button" class="btn btn-secondary small" @click="switchCurrentPlan(plan.id)">
                        设为当前
                      </button>
                      <button type="button" class="btn btn-outline small" @click="openPlanDetail(plan.id)">
                        详情
                      </button>
                      <button type="button" class="btn btn-outline small" @click="openEditModal(plan)">
                        修改
                      </button>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-state">
                  <div class="empty-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    </svg>
                  </div>
                  <p>还没有历史训练计划</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态带日历 -->
        <div v-else class="empty-state-with-calendar">
          <!-- 日历部分 -->
          <div class="calendar-empty-section">
            <div class="calendar-header">
              <h3>训练日历</h3>
              <div class="calendar-nav">
                <button type="button" class="btn btn-icon" @click="changeMonth(-1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M15 19l-7-7 7-7"/>
                  </svg>
                </button>
                <span class="calendar-title">{{ monthLabel }}</span>
                <button type="button" class="btn btn-icon" @click="changeMonth(1)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 5l7 7-7 7"/>
                  </svg>
                </button>
              </div>
            </div>

            <CalendarPanel
              :month-label="monthLabel"
              :weekday-headers="weekdayHeaders"
              :calendar-days="calendarDays"
              :entry-for-day="(day) => getTrainingEntry(null, day)"
              @prev="changeMonth(-1)"
              @next="changeMonth(1)"
              @open-entry="() => {}"
            />
          </div>

        </div>
      </template>
    </div>

    <!-- 训练日选择模态框 -->
    <div v-if="showWeekdayModal" class="modal-overlay" @click.self="closeWeekdayModal">
      <div class="modal-container">
        <div class="modal-header">
          <h3 class="modal-title">
            <svg class="modal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            选择训练日
          </h3>
          <button type="button" class="btn btn-icon modal-close" @click="closeWeekdayModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="modal-description">只有你确认的训练日，才会同步到训练计划日历中。</p>
          <div class="weekday-selector">
            <div class="weekday-grid">
              <button
                v-for="day in weekdayHeaders"
                :key="day"
                type="button"
                class="weekday-option"
                :class="{ selected: weekdayDraft.includes(day) }"
                @click="toggleWeekday(day)"
              >
                <span class="weekday-text">{{ day }}</span>
                <span v-if="weekdayDraft.includes(day)" class="weekday-check">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <path d="M5 13l4 4L19 7"/>
                  </svg>
                </span>
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline" @click="closeWeekdayModal">取消</button>
          <button type="button" class="btn btn-primary" :disabled="!weekdayDraft.length" @click="saveWeekdays">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 13l4 4L19 7"/>
            </svg>
            确定并使用计划
          </button>
        </div>
      </div>
    </div>

    <!-- 编辑训练计划模态框 -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-container wide">
        <div class="modal-header">
          <h3 class="modal-title">
            <svg class="modal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            修改训练计划
          </h3>
          <button type="button" class="btn btn-icon modal-close" @click="closeEditModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-container">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">计划标题</span>
                  <input v-model.trim="editForm.title" type="text" class="form-input" placeholder="例如：增肌训练计划" />
                </label>
              </div>
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">训练目标</span>
                  <input v-model.trim="editForm.goal" type="text" class="form-input" placeholder="例如：增加肌肉量，提高力量" />
                </label>
              </div>
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">训练方式</span>
                  <input v-model.trim="editForm.method" type="text" class="form-input" placeholder="例如：力量训练，有氧训练" />
                </label>
              </div>
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">每周训练天数</span>
                  <input v-model.trim="editForm.weekly_days" type="text" class="form-input" placeholder="例如：4" />
                </label>
              </div>
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">单次时长</span>
                  <input v-model.trim="editForm.daily_duration" type="text" class="form-input" placeholder="例如：60分钟" />
                </label>
              </div>
              <div class="form-group">
                <label class="form-label">
                  <span class="label-text">强度</span>
                  <input v-model.trim="editForm.intensity" type="text" class="form-input" placeholder="例如：中等，高强度" />
                </label>
              </div>
            </div>
            <div class="form-group full-width">
              <label class="form-label">
                <span class="label-text">计划内容</span>
                <textarea v-model="editForm.content" rows="12" class="form-textarea" placeholder="详细描述训练计划内容..."></textarea>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-outline" @click="closeEditModal">取消</button>
          <button type="button" class="btn btn-primary" @click="saveEdit">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 13l4 4L19 7"/>
            </svg>
            保存修改
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const ACTIVE_PLAN_KEY = 'sports-training-active-plan-id'
const weekdayHeaders = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

// 清理Markdown格式符号
const removeMarkdownFormat = (text = '') => {
  if (!text || typeof text !== 'string') return text

  // 处理HTML实体
  let cleaned = text
    .replace(/&middot;|&bull;|&sdot;/g, '') // HTML项目符号
    .replace(/&nbsp;/g, ' ')              // 非换行空格
    .replace(/&[a-z]+;/g, '')             // 其他简单HTML实体

  // 处理Markdown表格：移除表格分隔符和表头分隔线，将表格转换为更易读的格式
  const lines = cleaned.split('\n')
  const processedLines = []
  let inTable = false
  let tableHeaders = []
  let tableRows = []

  for (let line of lines) {
    // 检测表格行：包含 | 且不是代码块
    if (line.includes('|') && !line.startsWith('    ') && !line.startsWith('\t')) {
      const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell !== '')

      // 检测表头分隔线（只包含 - 和 |）
      const isHeaderSeparator = /^[\s|]*[-:| ]+[\s|]*$/.test(line)

      if (!inTable) {
        inTable = true
        tableHeaders = cells
        tableRows = []
      } else if (isHeaderSeparator) {
        // 跳过表头分隔线
        continue
      } else {
        tableRows.push(cells)
      }

      // 如果这一行处理完了，继续下一行
      continue
    } else if (inTable) {
      // 表格结束，将表格转换为更易读的格式
      if (tableRows.length > 0) {
        // 简单格式：每行作为文本
        for (let row of tableRows) {
          let rowText = ''
          for (let i = 0; i < Math.min(tableHeaders.length, row.length); i++) {
            rowText += `${tableHeaders[i]}: ${row[i]}  `
          }
          processedLines.push(rowText.trim())
        }
      }
      inTable = false
      tableHeaders = []
      tableRows = []
    }

    // 非表格行，直接添加
    if (!inTable) {
      processedLines.push(line)
    }
  }

  // 处理最后可能剩余的表格
  if (inTable && tableRows.length > 0) {
    for (let row of tableRows) {
      let rowText = ''
      for (let i = 0; i < Math.min(tableHeaders.length, row.length); i++) {
        rowText += `${tableHeaders[i]}: ${row[i]}  `
      }
      processedLines.push(rowText.trim())
    }
  }

  cleaned = processedLines.join('\n')

  // 移除常见的Markdown格式符号
  cleaned = cleaned
    .replace(/\*\*(.*?)\*\*/g, '$1')      // 粗体 **text**
    .replace(/\*(.*?)\*/g, '$1')          // 斜体 *text*
    .replace(/__(.*?)__/g, '$1')          // 粗体 __text__
    .replace(/_(.*?)_/g, '$1')            // 斜体 _text_
    .replace(/~~(.*?)~~/g, '$1')          // 删除线 ~~text~~
    .replace(/`(.*?)`/g, '$1')            // 行内代码 `text`
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')   // 链接 [text](url)
    .replace(/^#+\s*/gm, '')              // 标题 # text
    .replace(/^-\s*/gm, '')               // 无序列表 - text
    .replace(/^\d+\.\s*/gm, '')           // 有序列表 1. text
    .replace(/^\s*[-*+]\s*/gm, '')        // 各种列表符号
    .replace(/^>\s*/gm, '')               // 引用块 > text
    .replace(/<br\s*\/?>/g, '\n')         // HTML换行 <br> 替换为换行
    .replace(/[-=*_]{3,}/g, '')           // 分隔线 --- === *** ___
    // 清理常见的Unicode符号（复选框、警告、项目符号等）
    .replace(/[✅❌⚠️🔹🗓️🌟📌💡🌿🛑📊🎯🌱💪😊📄📝🔍💬📋🎯🏥💡🚫✨🌞💦🏃‍♀️🏃‍♂️🧘‍♀️🧘‍♂️]/gu, '')
    .replace(/[▪•·∙◦●○◆◇■□▢▣▲△▶▷▼▽➤➢➔→]/g, '') // 各种项目符号
    .replace(/[·•]/g, '')                 // 中文常用的项目符号
    .replace(/[ 　]/g, ' ')               // 全角空格和中文空格
    .replace(/\|\s*/g, ' ')               // 表格分隔符 | 替换为空格（处理残留的）
    .replace(/\s*\|\s*/g, ' ')            // 表格分隔符 | 替换为空格（带空格的）
    .replace(/\n{3,}/g, '\n\n')           // 多个换行符减少为两个
    .replace(/\s{2,}/g, ' ')              // 多个空格合并为一个
    .replace(/^\s+|\s+$/g, '')            // 去除首尾空格
    .trim()

  return cleaned
}

const route = useRoute()
const router = useRouter()

const plans = ref([])
const selectedPlan = ref(null)
const activePlanId = ref(null)
const currentMonth = ref(new Date())
const boardEntry = ref(null)
const detailEntry = ref(null)

const showWeekdayModal = ref(false)
const weekdayPlan = ref(null)
const weekdayDraft = ref([])

const showEditModal = ref(false)
const editTargetPlan = ref(null)
const editForm = ref({
  title: '',
  goal: '',
  method: '',
  weekly_days: '',
  daily_duration: '',
  intensity: '',
  content: ''
})

const isDetailView = computed(() => Boolean(Number(route.query.planId)))

const sortedPlans = computed(() =>
  [...plans.value].sort((a, b) => {
    const timeA = new Date(a.updated_at || a.created_at || a.start_date || 0).getTime()
    const timeB = new Date(b.updated_at || b.created_at || b.start_date || 0).getTime()
    return timeB - timeA
  })
)

const currentPlan = computed(() => sortedPlans.value.find((plan) => plan.id === activePlanId.value) || sortedPlans.value[0] || null)
const historyPlans = computed(() => sortedPlans.value.filter((plan) => plan.id !== currentPlan.value?.id))
const monthLabel = computed(() => `${currentMonth.value.getFullYear()} 年 ${currentMonth.value.getMonth() + 1} 月`)

const normalizePlan = (plan = {}) => ({
  ...plan,
  metadata: plan.metadata || {},
  selected_weekdays: Array.isArray(plan.selected_weekdays) ? plan.selected_weekdays : []
})

const formatDate = (value) => {
  if (!value) return '未设置'
  return new Date(value).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getDateKey = (value) => {
  const date = new Date(value)
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

const getSelectedWeekdays = (plan) => (Array.isArray(plan?.selected_weekdays) ? plan.selected_weekdays : [])

const getWeekdaysLabel = (plan) => {
  const weekdays = getSelectedWeekdays(plan)
  return weekdays.length ? weekdays.join(' / ') : '尚未选择训练日'
}

const planSubtitle = (plan) => {
  const method = plan?.metadata?.method || '综合训练'
  const duration = plan?.metadata?.daily_duration ? `${plan.metadata.daily_duration} 分钟` : '30 分钟'
  return `围绕 ${method} 制定，单次训练约 ${duration}。`
}

const contentSegments = (plan) =>
  removeMarkdownFormat(String(plan?.content || ''))
    .split(/\n+/)
    .map((segment) => segment.trim())
    .filter(Boolean)

const getRecoveryText = (plan) => {
  const intensity = String(plan?.metadata?.intensity || '')
  if (intensity.includes('高')) return '训练后增加拉伸和补水，第二天注意恢复。'
  if (intensity.includes('中')) return '注意呼吸节奏，并安排轻量恢复。'
  return '保持动作质量，训练后适度放松。'
}

const buildTrainingEntries = (plan) => {
  if (!plan) return []

  const weekdays = getSelectedWeekdays(plan)
  if (!weekdays.length) return []

  const start = new Date(plan.start_date || new Date())
  const end = new Date(plan.end_date || addDays(plan.start_date || new Date().toISOString(), 29))
  const segments = contentSegments(plan)
  const entries = []
  let sessionIndex = 0

  for (const cursor = new Date(start); cursor <= end; cursor.setDate(cursor.getDate() + 1)) {
    const weekday = weekdayHeaders[(cursor.getDay() + 6) % 7]
    if (!weekdays.includes(weekday)) continue

    entries.push({
      date: getDateKey(cursor),
      title: `第 ${sessionIndex + 1} 次训练`,
      duration: `${plan?.metadata?.daily_duration || 30} 分钟`,
      focus: `${plan?.metadata?.method || '综合训练'} · ${plan?.goal || '训练目标'}`,
      recovery: getRecoveryText(plan),
      summary: segments[sessionIndex % Math.max(segments.length, 1)] || '按照计划完成今天的训练内容。'
    })
    sessionIndex += 1
  }

  return entries
}

const addDays = (value, days) => {
  const date = new Date(value)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

const getTrainingEntry = (plan, calendarDay) => {
  if (!plan || !calendarDay?.date) return null
  const dayKey = getDateKey(calendarDay.date)
  return buildTrainingEntries(plan).find((entry) => entry.date === dayKey) || null
}

const calendarDays = computed(() => {
  const year = currentMonth.value.getFullYear()
  const month = currentMonth.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDate = new Date(year, month + 1, 0).getDate()
  const startOffset = (firstDay.getDay() + 6) % 7
  const result = []

  for (let i = 0; i < startOffset; i += 1) {
    result.push({ key: `empty-start-${i}`, date: null })
  }

  for (let day = 1; day <= lastDate; day += 1) {
    const date = new Date(year, month, day)
    result.push({
      key: `${year}-${month}-${day}`,
      date,
      day,
      isToday: getDateKey(date) === getDateKey(new Date())
    })
  }

  while (result.length % 7 !== 0) {
    result.push({ key: `empty-end-${result.length}`, date: null })
  }

  return result
})

const changeMonth = (offset) => {
  const nextMonth = new Date(currentMonth.value)
  nextMonth.setMonth(nextMonth.getMonth() + offset)
  currentMonth.value = nextMonth
}

const applyUpdatedPlan = (plan) => {
  const normalized = normalizePlan(plan)
  const index = plans.value.findIndex((item) => item.id === normalized.id)
  if (index >= 0) {
    plans.value.splice(index, 1, normalized)
  } else {
    plans.value.unshift(normalized)
  }
  if (selectedPlan.value?.id === normalized.id) selectedPlan.value = normalized
}

const loadPlans = async () => {
  const response = await api.get('/training/plans')
  plans.value = (response?.plans || []).map(normalizePlan)
}

const syncCurrentPlan = () => {
  const storedPlanId = Number(localStorage.getItem(ACTIVE_PLAN_KEY))
  if (storedPlanId && plans.value.some((plan) => plan.id === storedPlanId)) {
    activePlanId.value = storedPlanId
  } else {
    activePlanId.value = sortedPlans.value[0]?.id || null
  }
}

const syncSelectedPlan = async () => {
  const planId = Number(route.query.planId)
  if (!planId) {
    selectedPlan.value = null
    detailEntry.value = null
    return
  }

  const localPlan = plans.value.find((plan) => plan.id === planId)
  if (localPlan) {
    selectedPlan.value = localPlan
    return
  }

  const response = await api.get(`/training/plans/${planId}`)
  selectedPlan.value = normalizePlan(response)
}

const goBoard = () => {
  router.push({ name: 'TrainingPlan' })
}

const goCreatePlan = () => {
  router.push({ name: 'TrainingQuestionnaire' })
}

const openPlanDetail = (planId) => {
  router.push({ name: 'TrainingPlan', query: { planId } })
}

const switchCurrentPlan = (planId) => {
  activePlanId.value = planId
  localStorage.setItem(ACTIVE_PLAN_KEY, String(planId))
  boardEntry.value = null
}

const openBoardEntry = (entry) => {
  boardEntry.value = entry
}

const openDetailEntry = (entry) => {
  detailEntry.value = entry
}

const openWeekdayModal = (plan) => {
  weekdayPlan.value = plan
  weekdayDraft.value = [...getSelectedWeekdays(plan)]
  showWeekdayModal.value = true
}

const closeWeekdayModal = () => {
  showWeekdayModal.value = false
  weekdayPlan.value = null
  weekdayDraft.value = []
}

const toggleWeekday = (day) => {
  weekdayDraft.value = weekdayDraft.value.includes(day)
    ? weekdayDraft.value.filter((item) => item !== day)
    : [...weekdayDraft.value, day]
}

const saveWeekdays = async () => {
  if (!weekdayPlan.value || !weekdayDraft.value.length) return

  try {
    const response = await api.put(`/training/plans/${weekdayPlan.value.id}`, {
      selected_weekdays: [...weekdayDraft.value]
    })
    applyUpdatedPlan(response.plan)
    localStorage.setItem(ACTIVE_PLAN_KEY, String(weekdayPlan.value.id))
  } catch (error) {
    console.error('保存训练日失败:', error)
    applyUpdatedPlan({
      ...weekdayPlan.value,
      selected_weekdays: [...weekdayDraft.value]
    })
  }

  closeWeekdayModal()
  router.push({ name: 'TrainingPlan' })
}

const openEditModal = (plan) => {
  editTargetPlan.value = plan
  editForm.value = {
    title: plan.title || '',
    goal: plan.goal || '',
    method: plan.metadata?.method || '',
    weekly_days: plan.metadata?.weekly_days || '',
    daily_duration: plan.metadata?.daily_duration || '',
    intensity: plan.metadata?.intensity || '',
    content: plan.content || ''
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editTargetPlan.value = null
}

const saveEdit = async () => {
  if (!editTargetPlan.value) return

  const payload = {
    title: editForm.value.title,
    goal: editForm.value.goal,
    content: editForm.value.content,
    metadata: {
      ...(editTargetPlan.value.metadata || {}),
      method: editForm.value.method,
      weekly_days: editForm.value.weekly_days,
      daily_duration: editForm.value.daily_duration,
      intensity: editForm.value.intensity
    }
  }

  try {
    const response = await api.put(`/training/plans/${editTargetPlan.value.id}`, payload)
    applyUpdatedPlan(response.plan)
  } catch (error) {
    console.error('保存训练计划修改失败:', error)
    applyUpdatedPlan({
      ...editTargetPlan.value,
      ...payload
    })
  }

  closeEditModal()
}

const removePlan = async (plan) => {
  if (!window.confirm('确认删除这个训练计划吗？')) return

  try {
    await api.delete(`/training/plans/${plan.id}`)
  } catch (error) {
    console.error('删除训练计划失败:', error)
  }

  plans.value = plans.value.filter((item) => item.id !== plan.id)
  if (activePlanId.value === plan.id) {
    activePlanId.value = plans.value[0]?.id || null
    if (activePlanId.value) {
      localStorage.setItem(ACTIVE_PLAN_KEY, String(activePlanId.value))
    } else {
      localStorage.removeItem(ACTIVE_PLAN_KEY)
    }
  }

  if (selectedPlan.value?.id === plan.id) {
    router.push({ name: 'TrainingPlan' })
  }
}

watch(
  () => route.query.planId,
  () => {
    syncSelectedPlan()
  }
)

watch(
  () => currentPlan.value?.id,
  () => {
    boardEntry.value = null
  }
)

watch(
  () => activePlanId.value,
  (value) => {
    if (value) {
      localStorage.setItem(ACTIVE_PLAN_KEY, String(value))
    }
  }
)

onMounted(async () => {
  try {
    await loadPlans()
    syncCurrentPlan()
    await syncSelectedPlan()
  } catch (error) {
    console.error('读取训练计划失败:', error)
    plans.value = []
  }
})

const CalendarPanel = defineComponent({
  props: {
    monthLabel: String,
    weekdayHeaders: Array,
    calendarDays: Array,
    entryForDay: Function
  },
  emits: ['prev', 'next', 'open-entry'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'calendar-box' }, [
        h('div', { class: 'calendar-head' }, [
          h('button', { class: 'btn btn-ghost', onClick: () => emit('prev') }, '上个月'),
          h('strong', props.monthLabel),
          h('button', { class: 'btn btn-ghost', onClick: () => emit('next') }, '下个月')
        ]),
        h('div', { class: 'calendar-grid' }, [
          ...(props.weekdayHeaders || []).map((day) => h('div', { class: 'calendar-weekday', key: `weekday-${day}` }, day)),
          ...((props.calendarDays || []).map((day) => {
            const entry = props.entryForDay?.(day)
            return h(
              'div',
              {
                class: ['calendar-day', { empty: !day.date, today: day.isToday, active: !!entry }],
                key: day.key
              },
              day.date
                ? [
                    h('div', { class: 'calendar-day-top' }, [
                      h('span', { class: 'day-number' }, String(day.day)),
                      entry ? h('span', { class: 'day-badge' }, '训练日') : null
                    ]),
                    entry
                      ? h(
                          'button',
                          {
                            class: 'day-action',
                            onClick: () => emit('open-entry', entry)
                          },
                          '查看训练内容'
                        )
                      : null
                  ]
                : []
            )
          }) || [])
        ])
      ])
  }
})
</script>

<style scoped>
/* 基础样式 */
.training-plan-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-surface) 100%);
  font-family: 'Inter', 'Noto Sans SC', 'PingFang SC', sans-serif;
  color: var(--color-text-primary);
}

.page-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
}

/* 头部样式 */
.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 32px 40px;
  margin-bottom: 32px;
  border: 1px solid rgba(0, 113, 227, 0.1);
  box-shadow: 0 20px 40px rgba(0, 82, 163, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.header-text {
  flex: 1;
}

.header-label {
  display: inline-block;
  padding: 6px 12px;
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-accent);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.header-title {
  font-size: 32px;
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 12px 0;
  color: var(--color-text-primary);
}

.header-description {
  font-size: 16px;
  line-height: 1.6;
  color: var(--color-text-secondary);
  margin: 0;
  max-width: 600px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

/* 按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
}

.btn:hover {
  transform: translateY(-2px);
}

.btn:active {
  transform: translateY(0);
}

.btn-icon {
  width: 18px;
  height: 18px;
  stroke-width: 2;
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-accent), #0066CC);
  color: white;
  box-shadow: 0 8px 24px rgba(0, 113, 227, 0.3);
}

.btn-primary:hover {
  box-shadow: 0 12px 32px rgba(0, 113, 227, 0.4);
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid rgba(0, 113, 227, 0.2);
}

.btn-secondary:hover {
  background: rgba(0, 113, 227, 0.05);
}

.btn-outline {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid rgba(0, 113, 227, 0.3);
}

.btn-outline:hover {
  background: rgba(0, 113, 227, 0.05);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #DC2626;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.15);
}

.btn-icon {
  padding: 10px;
  width: 40px;
  height: 40px;
}

.btn.small {
  padding: 8px 16px;
  font-size: 13px;
}

/* 详情视图 */
.detail-view {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

.detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.plan-card {
  background: white;
  border-radius: 20px;
  padding: 28px;
  border: 1px solid rgba(0, 113, 227, 0.1);
  box-shadow: 0 16px 40px rgba(0, 82, 163, 0.08);
}

.plan-header {
  margin-bottom: 24px;
}

.plan-badge-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-ai {
  background: rgba(0, 113, 227, 0.1);
  color: var(--color-accent);
}

.badge-method {
  background: rgba(34, 197, 94, 0.1);
  color: #16A34A;
}

.badge.small {
  padding: 4px 8px;
  font-size: 11px;
}

.plan-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--color-text-primary);
}

.plan-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.plan-meta-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 28px;
}

.meta-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--color-bg);
  border-radius: 16px;
  border: 1px solid rgba(0, 113, 227, 0.08);
}

.meta-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  color: var(--color-accent);
}

.meta-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0 0 4px 0;
  font-weight: 500;
}

.meta-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.4;
}

.plan-content {
  margin-bottom: 28px;
}

.content-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 16px 0;
  color: var(--color-text-primary);
}

.title-icon {
  width: 20px;
  height: 20px;
  color: var(--color-accent);
}

.content-body {
  background: var(--color-bg);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(0, 113, 227, 0.08);
}

.content-body pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-primary);
}

.plan-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-group {
  display: flex;
  gap: 8px;
}

/* 详情主内容 */
.detail-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.calendar-section {
  background: white;
  border-radius: 20px;
  padding: 28px;
  border: 1px solid rgba(0, 113, 227, 0.1);
  box-shadow: 0 16px 40px rgba(0, 82, 163, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h3 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-primary);
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}

.calendar-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  min-width: 180px;
  text-align: center;
}

.training-entry {
  background: var(--color-bg);
  border-radius: 16px;
  padding: 24px;
  margin-top: 24px;
  border: 1px solid rgba(0, 113, 227, 0.1);
}

.entry-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.entry-date {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.entry-header h4 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-primary);
}

.entry-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.detail-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--color-text-primary);
  margin: 0;
  padding: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 113, 227, 0.08);
}

/* 仪表板视图 */
.dashboard-view {
  margin-bottom: 32px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 320px 1fr 320px;
  gap: 24px;
}

.dashboard-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.current-plan-card,
.training-content-card,
.history-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(0, 113, 227, 0.1);
  box-shadow: 0 16px 40px rgba(0, 82, 163, 0.08);
}

.card-header {
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-primary);
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.card-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  margin-bottom: 8px;
  display: block;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: var(--color-text-primary);
}

.card-subtitle {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.plan-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.tag {
  display: inline-block;
  padding: 6px 12px;
  background: var(--color-bg);
  color: var(--color-text-primary);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid rgba(0, 113, 227, 0.1);
}

.tag.small {
  padding: 4px 8px;
  font-size: 11px;
}

.content-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 113, 227, 0.08);
}

.detail-row:last-child {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  border-bottom: none;
}

.content-empty {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  color: rgba(0, 113, 227, 0.3);
  margin: 0 auto 16px;
}

.empty-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 4px 0 0 0;
}

.calendar-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(0, 113, 227, 0.1);
  box-shadow: 0 16px 40px rgba(0, 82, 163, 0.08);
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  background: var(--color-bg);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(0, 113, 227, 0.08);
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.history-item-header h4 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: var(--color-text-primary);
}

.item-subtitle {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.4;
}

.item-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-text-secondary);
}

.empty-state-full {
  text-align: center;
  padding: 80px 40px;
  max-width: 600px;
  margin: 40px auto;
}

.empty-illustration {
  width: 160px;
  height: 160px;
  margin: 0 auto 32px;
  color: rgba(0, 113, 227, 0.1);
}

.empty-description {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin: 12px 0 32px 0;
  line-height: 1.6;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 24px;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.2);
}

.modal-container.wide {
  max-width: 800px;
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid rgba(0, 113, 227, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-primary);
}

.modal-icon {
  width: 24px;
  height: 24px;
  color: var(--color-accent);
}

.modal-close {
  color: var(--color-text-secondary);
}

.modal-body {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.modal-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.modal-footer {
  padding: 24px 32px;
  border-top: 1px solid rgba(0, 113, 227, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 训练日选择器 */
.weekday-selector {
  margin-bottom: 24px;
}

.weekday-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.weekday-option {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(0, 113, 227, 0.2);
  border-radius: 12px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 12px 8px;
}

.weekday-option:hover {
  border-color: var(--color-accent);
  background: rgba(0, 113, 227, 0.05);
}

.weekday-option.selected {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: white;
}

.weekday-text {
  font-size: 14px;
  font-weight: 600;
}

.weekday-check {
  margin-top: 4px;
  width: 16px;
  height: 16px;
}

/* 表单 */
.form-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.form-input,
.form-textarea {
  padding: 12px 16px;
  border: 1px solid rgba(0, 113, 227, 0.2);
  border-radius: 12px;
  font-family: inherit;
  font-size: 14px;
  color: var(--color-text-primary);
  background: white;
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

/* 保持原有的日历组件样式 */
:deep(.calendar-box) {
  margin-top: 0;
  padding: 20px;
  border-radius: 20px;
  background:
    radial-gradient(circle at top left, rgba(0, 113, 227, 0.14), transparent 30%),
    linear-gradient(180deg, rgba(248, 251, 255, 0.98), rgba(240, 246, 255, 0.94));
  border: 1px solid rgba(0, 113, 227, 0.14);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45), 0 14px 28px rgba(0, 82, 163, 0.08);
}

:deep(.calendar-head strong) {
  color: var(--color-text-primary);
  font-size: 22px;
  font-weight: 800;
}

:deep(.calendar-grid) {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

:deep(.calendar-weekday) {
  text-align: center;
  padding: 10px 0;
  color: var(--color-text-primary);
  font-weight: 700;
  border-radius: 12px;
  background: var(--color-bg);
  font-size: 13px;
}

:deep(.calendar-day) {
  min-height: 128px;
  padding: 12px;
  border-radius: 16px;
  background: linear-gradient(180deg, var(--color-surface), var(--color-bg));
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 10px;
  border: 1px solid rgba(0, 113, 227, 0.12);
  box-shadow: 0 8px 18px rgba(0, 113, 227, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

:deep(.calendar-day:not(.empty):hover) {
  transform: translateY(-2px);
  box-shadow: 0 14px 24px rgba(0, 113, 227, 0.1);
}

:deep(.calendar-day.empty) {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
}

:deep(.calendar-day.today) {
  border-color: rgba(0, 113, 227, 0.5);
}

:deep(.calendar-day.active) {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.99), rgba(229, 239, 255, 0.98));
  border-color: rgba(0, 113, 227, 0.5);
  box-shadow: 0 14px 30px rgba(0, 113, 227, 0.16);
}

:deep(.calendar-day-top) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.day-number) {
  color: var(--color-text-primary);
  font-weight: 800;
  font-size: 16px;
}

:deep(.day-badge) {
  padding: 5px 9px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent));
  color: #fff;
  font-size: 11px;
  font-weight: 700;
}

:deep(.day-action) {
  width: 100%;
  padding: 9px 10px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-hover));
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 280px 1fr 280px;
    gap: 20px;
  }

  .detail-view {
    grid-template-columns: 320px 1fr;
    gap: 24px;
  }
}

@media (max-width: 992px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .detail-view {
    grid-template-columns: 1fr;
  }

  .dashboard-sidebar {
    order: 3;
  }

  .dashboard-main {
    order: 2;
  }

  .dashboard-sidebar:first-child {
    order: 1;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .weekday-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .page-header {
    padding: 24px;
  }

  .header-content {
    flex-direction: column;
    gap: 20px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .plan-card,
  .calendar-section,
  .current-plan-card,
  .training-content-card,
  .history-card,
  .calendar-card {
    padding: 20px;
  }

  .modal-container {
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }

  :deep(.calendar-day) {
    min-height: 100px;
    padding: 10px;
  }

  .weekday-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .header-title {
    font-size: 24px;
  }

  .plan-title {
    font-size: 20px;
  }

  .weekday-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .entry-details {
    grid-template-columns: 1fr;
  }

  .action-group {
    flex-wrap: wrap;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}

/* 空状态带日历 */
.empty-state-with-calendar {
  display: flex;
  flex-direction: column;
  gap: 40px;
  margin-bottom: 32px;
}

.calendar-empty-section {
  background: white;
  border-radius: 20px;
  padding: 28px;
  border: 1px solid rgba(0, 113, 227, 0.1);
  box-shadow: 0 16px 40px rgba(0, 82, 163, 0.08);
}

.calendar-empty-section .calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.calendar-empty-section .calendar-header h3 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-primary);
}

.calendar-empty-section .calendar-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}

.calendar-empty-section .calendar-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  min-width: 180px;
  text-align: center;
}


/* 响应式调整 */
@media (max-width: 768px) {
  .empty-state-with-calendar {
    gap: 24px;
  }

  .calendar-empty-section {
    padding: 20px;
  }

}
</style>
