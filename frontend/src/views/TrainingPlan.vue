<template>
  <div class="training-plan-page">
    <Navbar />

    <div class="page-container">
      <!-- 页面头部 -->
      <header v-if="isDetailView" class="page-header">
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
                <div class="content-body markdown-content" v-html="renderPlanContent(selectedPlan.content)"></div>
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
                <div class="entry-markdown-wrapper markdown-content entry-markdown" v-html="renderPlanContent(detailEntry.summary, { skipFirstDayHeading: true })"></div>
              </div>
            </div>
          </main>
        </div>
      </template>

      <!-- 列表视图 -->
      <template v-else>
        <div v-if="currentPlan" class="dashboard-view">
          <div class="dashboard-grid">
            <!-- 顶部：管理你的训练计划 + 当前计划 + 历史计划 -->
            <div class="dashboard-top">
              <div class="current-plan-card">

                <div class="plan-card-header">
                  <div>
                    <p class="card-label">Current Plan</p>
                    <h2 class="card-title">{{ currentPlan.title }}</h2>
                    <!-- <p class="card-subtitle">{{ planSubtitle(currentPlan) }}</p> -->
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
                  <button type="button" class="btn btn-day-badge" @click="openPlanDetail(currentPlan)">
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
              <div class="dashboard-sidebar">
                <div class="history-card">
                  <div class="card-header">
                    <h3>历史训练计划</h3>
                  </div>

                  <div v-if="historyPlans.length" class="history-list">
                    <div class="history-item">
                      <div class="history-item-header">
                        <div>
                          <h4>{{ currentHistoryPlan.title }}</h4>
                          <p class="item-subtitle">{{ currentHistoryPlan.goal || 'AI 教练推荐' }}</p>
                        </div>
                        <span v-if="currentHistoryPlan.created_from_ai" class="badge badge-ai small">AI</span>
                      </div>

                      <div class="item-tags">
                        <span class="tag small">{{ currentHistoryPlan.metadata?.weekly_days ? `每周 ${currentHistoryPlan.metadata.weekly_days} 天` : '频率待定' }}</span>
                        <span class="tag small">{{ currentHistoryPlan.metadata?.daily_duration ? `${currentHistoryPlan.metadata.daily_duration} 分钟` : '时长待定' }}</span>
                        <span class="tag small">{{ currentHistoryPlan.metadata?.intensity || '强度待定' }}</span>
                        <span class="tag small">{{ getWeekdaysLabel(currentHistoryPlan) }}</span>
                      </div>

                      <div class="item-actions">
                        <button type="button" class="btn btn-secondary small" @click="switchCurrentPlan(currentHistoryPlan.id)">
                          设为当前
                        </button>
                        <button type="button" class="btn btn-outline small" @click="openPlanDetail(currentHistoryPlan)">
                          详情
                        </button>
                        <button type="button" class="btn btn-outline small" @click="openEditModal(currentHistoryPlan)">
                          修改
                        </button>
                        <button type="button" class="btn btn-danger small" @click="removePlan(currentHistoryPlan)">
                          删除
                        </button>
                      </div>

                      <div class="history-footer">
                        <div class="history-nav">
                          <button type="button" class="btn btn-outline small" @click="prevHistory" :disabled="historyPage === 0">&lt;</button>
                          <span class="history-nav-label">{{ historyPage + 1 }} / {{ historyPlans.length }}</span>
                          <button type="button" class="btn btn-outline small" @click="nextHistory" :disabled="historyPage >= historyPlans.length - 1">&gt;</button>
                        </div>
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

            <!-- 下方：训练日历 -->
            <div class="dashboard-bottom">
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
            </div>

            <div v-if="boardEntry" class="board-entry-overlay" @click.self="closeBoardEntry">
              <div class="board-entry-card">
                <div class="board-entry-header">
                  <div>
                    <!-- <span class="entry-date">{{ formatDate(boardEntry.date) }}</span> -->
                    <h4>{{ formatDate(boardEntry.date) }}</h4>
                  </div>
                  <button type="button" class="btn btn-icon board-entry-close" @click="closeBoardEntry">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
                <div class="entry-markdown-wrapper markdown-content entry-markdown" v-html="renderPlanContent(boardEntry.summary, { skipFirstDayHeading: true })"></div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state-with-calendar">
          <div class="empty-dashboard-grid">
            <!-- 顶部：管理你的训练计划 + 当前计划占位 + 历史计划占位 -->
            <div class="dashboard-top">
              <div class="placeholder-card current-placeholder">
                <!-- <div class="management-intro">
                  <div class="management-text">
                    <p class="card-label">Training Plans</p>
                    <h2 class="management-title">管理你的训练计划</h2>
                    <p class="management-description">创建你的第一份训练计划，并在日历中查看后续训练安排。</p>
                  </div>
                  <button type="button" class="btn btn-primary management-create-btn" @click="goCreatePlan">
                    <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 5v14M5 12h14"/>
                    </svg>
                    创建首个计划
                  </button>
                </div>

                <div class="card-section-divider"></div> -->

                <div class="placeholder-illustration">
                  <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="40" cy="40" r="36" fill="url(#placeholderGrad1)" opacity="0.1"/>
                    <path d="M40 20L46 32H58L50 42L54 54L40 46L26 54L30 42L22 32H34L40 20Z" stroke="url(#placeholderGrad1)" stroke-width="2" fill="none"/>
                    <defs>
                      <linearGradient id="placeholderGrad1" x1="20" y1="20" x2="60" y2="60" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#0071e3"/>
                        <stop offset="1" stop-color="#0077ed"/>
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
                <p class="placeholder-title">当前计划</p>
                <p class="placeholder-desc">暂无正在进行的训练计划</p>
              </div>

              <div class="dashboard-sidebar">
                <div class="placeholder-card history-placeholder">
                  <div class="placeholder-illustration">
                    <svg viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="40" cy="40" r="36" fill="url(#placeholderGrad3)" opacity="0.1"/>
                      <path d="M28 32H52M28 40H44M28 48H40" stroke="url(#placeholderGrad3)" stroke-width="2" stroke-linecap="round"/>
                      <circle cx="58" cy="32" r="4" fill="url(#placeholderGrad3)"/>
                      <defs>
                        <linearGradient id="placeholderGrad3" x1="20" y1="20" x2="60" y2="60" gradientUnits="userSpaceOnUse">
                          <stop stop-color="#0071e3"/>
                          <stop offset="1" stop-color="#0077ed"/>
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                  <p class="placeholder-title">历史计划</p>
                  <p class="placeholder-desc">暂无历史训练计划</p>
                </div>
              </div>
            </div>

            <!-- 下方：训练日历 -->
            <div class="dashboard-bottom">
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
                    :entry-for-day="(day) => getTrainingEntry(null, day)"
                    @prev="changeMonth(-1)"
                    @next="changeMonth(1)"
                    @open-entry="() => {}"
                  />
                </div>
              </div>
            </div>
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
          <p class="modal-description">
            最多可选择 {{ getPlanWeekdayLimit(weekdayPlan) }} 个训练日。
          </p>
          <div class="weekday-selector">
            <div class="weekday-grid">
              <button
                v-for="day in weekdayHeaders"
                :key="day"
                type="button"
                class="weekday-option"
                :class="{ selected: weekdayDraft.includes(day) }"
                :disabled="isWeekdayDisabled(day)"
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
              <div class="form-label">
                <span class="label-text">训练日</span>
                <p class="form-hint">最多可选择 {{ getEditWeekdayLimit() }} 个训练日。</p>
                <div class="weekday-grid edit-weekday-grid">
                  <button
                    v-for="day in weekdayHeaders"
                    :key="`edit-${day}`"
                    type="button"
                    class="weekday-option"
                    :class="{ selected: editForm.selected_weekdays.includes(day) }"
                    :disabled="isEditWeekdayDisabled(day)"
                    @click="toggleEditWeekday(day)"
                  >
                    <span class="weekday-text">{{ day }}</span>
                    <span v-if="editForm.selected_weekdays.includes(day)" class="weekday-check">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path d="M5 13l4 4L19 7"/>
                      </svg>
                    </span>
                  </button>
                </div>
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

    <div v-if="planDetail" class="modal-overlay" @click.self="closePlanDetail">
      <div class="modal-container wide">
        <div class="modal-header">
          <h3 class="modal-title">
            <svg class="modal-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            训练计划详情
          </h3>
          <button type="button" class="btn btn-icon modal-close" @click="closePlanDetail">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="plan-card">
            <div class="plan-header">
              <div class="plan-badge-row">
                <span v-if="planDetail.created_from_ai" class="badge badge-ai">AI 生成</span>
                <span class="badge badge-method">{{ planDetail.metadata?.method || '综合训练' }}</span>
              </div>
              <h2 class="plan-title">{{ planDetail.title }}</h2>
              <p class="plan-subtitle">{{ planSubtitle(planDetail) }}</p>
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
                  <p class="meta-value">{{ planDetail.goal || 'AI 教练推荐' }}</p>
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
                  <p class="meta-value">{{ formatDate(planDetail.start_date) }} - {{ formatDate(planDetail.end_date) }}</p>
                </div>
              </div>
              <div class="meta-item">
                <div class="meta-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                </div>
                <div>
                  <p class="meta-label">训练日</p>
                  <p class="meta-value">{{ getWeekdaysLabel(planDetail) }}</p>
                </div>
              </div>
              <div class="meta-item">
                <div class="meta-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                </div>
                <div>
                  <p class="meta-label">训练强度</p>
                  <p class="meta-value">{{ planDetail.metadata?.intensity || '中等' }}</p>
                </div>
              </div>
            </div>
            <div class="plan-content">
              <h3 class="content-title">计划内容</h3>
              <div class="content-body markdown-content" v-html="renderPlanContent(planDetail.content)"></div>
            </div>
          </div>
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

// 获取当前用户的 active plan 存储 key
const getUserActivePlanKey = () => {
  const userInfo = JSON.parse(localStorage.getItem('user') || 'null')
  const userId = userInfo?.id || 'anonymous'
  return `${ACTIVE_PLAN_KEY}-${userId}`
}
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
const planDetail = ref(null)

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
  content: '',
  selected_weekdays: []
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
const historyPage = ref(0)
const currentHistoryPlan = computed(() => historyPlans.value[historyPage.value] || historyPlans.value[0] || null)
const monthLabel = computed(() => `${currentMonth.value.getFullYear()} 年 ${currentMonth.value.getMonth() + 1} 月`)
const prevHistory = () => {
  if (historyPage.value > 0) historyPage.value -= 1
}
const nextHistory = () => {
  if (historyPage.value < historyPlans.value.length - 1) historyPage.value += 1
}
watch(historyPlans, (plans) => {
  if (historyPage.value > plans.length - 1) {
    historyPage.value = Math.max(plans.length - 1, 0)
  }
})

const getDisplayPlanTitle = (title = '', content = '') => {
  const cleanedTitle = String(title || '')
    .replace(/^#+\s*/, '')
    .replace(/^计划标题[:：]\s*/i, '')
    .trim()

  if (cleanedTitle) return cleanedTitle

  const lines = String(content || '').replace(/\r\n/g, '\n').split('\n').map((line) => line.trim()).filter(Boolean)
  const titleLine = lines.find((line) => /^#\s+/.test(line) || /^计划标题[:：]/.test(line) || /^#\s*计划标题[:：]?/i.test(line))
  return titleLine
    ? String(titleLine).replace(/^#\s*/, '').replace(/^计划标题[:：]\s*/i, '').trim()
    : ''
}

const normalizeTrainingDayHeading = (text = '') =>
  String(text || '')
    .replace(/（\s*周[一二三四五六日天]\s*）/g, '')
    .replace(/\(\s*周[一二三四五六日天]\s*\)/g, '')
    .replace(/（\s*星期[一二三四五六日天]\s*）/g, '')
    .replace(/\(\s*星期[一二三四五六日天]\s*\)/g, '')
    .replace(/\s*[-—–]\s*周[一二三四五六日天]\s*$/g, '')
    .replace(/\s*[-—–]\s*星期[一二三四五六日天]\s*$/g, '')
    .trim()

const normalizePlan = (plan = {}) => ({
  ...plan,
  title: getDisplayPlanTitle(plan.title, plan.content) || plan.title || '',
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

const parseWeeklyDaysLimit = (value) => {
  const match = String(value ?? '').match(/\d+/)
  const parsed = match ? Number(match[0]) : NaN
  if (!Number.isFinite(parsed) || parsed <= 0) return weekdayHeaders.length
  return Math.min(parsed, weekdayHeaders.length)
}

const getPlanWeekdayLimit = (plan) => parseWeeklyDaysLimit(plan?.metadata?.weekly_days)

const getEditWeekdayLimit = () => parseWeeklyDaysLimit(editForm.value.weekly_days)

const getWeekdaysLabel = (plan) => {
  const weekdays = getSelectedWeekdays(plan)
  return weekdays.length ? weekdays.join(' / ') : '尚未选择训练日'
}

const planSubtitle = (plan) => {
  const method = plan?.metadata?.method || '综合训练'
  const duration = plan?.metadata?.daily_duration ? `${plan.metadata.daily_duration} 分钟` : '30 分钟'
  return `围绕 ${method} 制定，单次训练约 ${duration}。`
}

const escapeHtml = (text = '') =>
  String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const formatInlineMarkdown = (text = '') =>
  escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.+?)__/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')

const renderPlanContent = (content = '', opts = {}) => {
  const lines = String(content || '').replace(/\r\n/g, '\n').split('\n')
  const html = []
  let inList = false
  let inNestedList = false
  let inOrderedList = false
  let inParagraph = false
  let inBlockquote = false
  let inTable = false
  let tableHeaderParsed = false
  let inTrainingDayCard = false
  let skippedFirstDayHeading = false

  const closeList = () => {
    if (inNestedList) {
      html.push('</ul></li>')
      inNestedList = false
    }
    if (inList) {
      html.push('</ul>')
      inList = false
    }
    if (inOrderedList) {
      html.push('</ol>')
      inOrderedList = false
    }
  }

  const closeParagraph = () => {
    if (inParagraph) {
      html.push('</p>')
      inParagraph = false
    }
  }

  const closeBlockquote = () => {
    if (inBlockquote) {
      closeParagraph()
      html.push('</blockquote>')
      inBlockquote = false
    }
  }

  const closeTable = () => {
    if (inTable) {
      html.push('</tbody></table>')
      inTable = false
      tableHeaderParsed = false
    }
  }

  const closeTrainingDayCard = () => {
    if (inTrainingDayCard) {
      closeTable()
      closeBlockquote()
      closeList()
      closeParagraph()
      html.push('</section>')
      inTrainingDayCard = false
    }
  }

  const parseTableCells = (value = '') =>
    value
      .split('|')
      .map((cell) => cell.trim())
      .filter(Boolean)

  const appendTableRow = (cells = [], tag = 'td') => {
    html.push('<tr>')
    cells.forEach((cell) => {
      html.push(`<${tag}>${formatInlineMarkdown(cell)}</${tag}>`)
    })
    html.push('</tr>')
  }

  const getNextNonEmptyLine = (startIndex) => {
    for (let nextIndex = startIndex + 1; nextIndex < lines.length; nextIndex += 1) {
      const candidate = lines[nextIndex].trim()
      if (candidate) return candidate
    }
    return ''
  }

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    const rawLine = lines[lineIndex]
    const line = rawLine.trim()

    if (!line) {
      closeTrainingDayCard()
      closeTable()
      closeBlockquote()
      closeList()
      closeParagraph()
      continue
    }

    const tableCells = parseTableCells(line)
    const isTableSeparator = /^[\s|:-]+$/.test(line)
    if ((line.includes('|') && tableCells.length >= 2) || (inTable && isTableSeparator)) {
      closeBlockquote()
      closeList()
      closeParagraph()

      if (!inTable && !isTableSeparator) {
        html.push('<table class="md-table"><thead>')
        appendTableRow(tableCells, 'th')
        html.push('</thead><tbody>')
        inTable = true
        tableHeaderParsed = true
        continue
      }

      if (inTable && isTableSeparator) {
        continue
      }

      if (inTable && tableHeaderParsed) {
        appendTableRow(tableCells, 'td')
        continue
      }
    } else {
      closeTable()
    }

    const headingMatch = line.match(/^(#{1,4})\s+(.+)$/)
    if (headingMatch) {
      const headingText = headingMatch[2].trim()
      if (levelAwareIsTrainingDayHeading(headingText)) {
        closeTrainingDayCard()
        closeBlockquote()
        closeList()
        closeParagraph()
        html.push('<section class="training-day-card">')
        inTrainingDayCard = true
        if (opts.skipFirstDayHeading && !skippedFirstDayHeading) {
          skippedFirstDayHeading = true
        } else {
          const level = Math.min(4, headingMatch[1].length)
          html.push(`<h${level}>${formatInlineMarkdown(normalizeTrainingDayHeading(headingText))}</h${level}>`)
        }
        continue
      }
      closeTrainingDayCard()
      closeBlockquote()
      closeList()
      closeParagraph()
      const level = Math.min(4, headingMatch[1].length)
      html.push(`<h${level}>${formatInlineMarkdown(headingMatch[2].trim())}</h${level}>`)
      continue
    }

    const plainTrainingDayHeading = parseTrainingDayHeadingLine(line)
    if (plainTrainingDayHeading) {
      closeTrainingDayCard()
      closeBlockquote()
      closeList()
      closeParagraph()
      html.push('<section class="training-day-card">')
      inTrainingDayCard = true
      if (opts.skipFirstDayHeading && !skippedFirstDayHeading) {
        skippedFirstDayHeading = true
      } else {
        html.push(`<h3>${formatInlineMarkdown(plainTrainingDayHeading)}</h3>`)
      }
      continue
    }

    if (/^([-*_])\1{2,}$/.test(line)) {
      closeTrainingDayCard()
      closeBlockquote()
      closeList()
      closeParagraph()
      html.push('<hr class="md-divider">')
      continue
    }

    if (/^计划标题[:：]/.test(line)) {
      closeTrainingDayCard()
      closeBlockquote()
      closeList()
      closeParagraph()
      html.push(`<h1>${formatInlineMarkdown(line.replace(/^计划标题[:：]\s*/, ''))}</h1>`)
      continue
    }

    if (/^计划概述[:：]/.test(line)) {
      closeTrainingDayCard()
      closeBlockquote()
      closeList()
      closeParagraph()
      html.push(`<h2>计划概述</h2><p>${formatInlineMarkdown(line.replace(/^计划概述[:：]\s*/, ''))}</p>`)
      continue
    }

    if (/^>\s?/.test(line)) {
      closeList()
      if (!inBlockquote) {
        closeParagraph()
        html.push('<blockquote>')
        inBlockquote = true
      }
      if (!inParagraph) {
        html.push('<p>')
        inParagraph = true
      } else {
        html.push('<br>')
      }
      html.push(formatInlineMarkdown(line.replace(/^>\s?/, '')))
      continue
    }

    if (/^[-*]\s+/.test(line)) {
      closeBlockquote()
      closeParagraph()
      if (!inList) {
        if (inOrderedList) {
          html.push('</ol>')
          inOrderedList = false
        }
        html.push('<ul>')
        inList = true
      }
      const itemText = line.replace(/^[-*]\s+/, '').trim()
      const nextLine = getNextNonEmptyLine(lineIndex)
      const startsNestedGroup = /[:：]$/.test(itemText) && /^[-*]\s+/.test(nextLine)

      if (inNestedList && !startsNestedGroup) {
        html.push(`<li class="nested-list-item">${formatInlineMarkdown(itemText)}</li>`)
        continue
      }

      if (inNestedList) {
        html.push('</ul></li>')
        inNestedList = false
      }

      if (startsNestedGroup) {
        html.push(`<li class="list-group-title">${formatInlineMarkdown(itemText)}<ul class="nested-list">`)
        inNestedList = true
        continue
      }

      html.push(`<li>${formatInlineMarkdown(itemText)}</li>`)
      continue
    }

    if (/^\d+\.\s+/.test(line)) {
      closeBlockquote()
      closeParagraph()
      if (!inOrderedList) {
        if (inList) {
          html.push('</ul>')
          inList = false
        }
        html.push('<ol>')
        inOrderedList = true
      }
      html.push(`<li>${formatInlineMarkdown(line.replace(/^\d+\.\s+/, ''))}</li>`)
      continue
    }

    if (!inParagraph) {
      closeList()
      html.push('<p>')
      inParagraph = true
    } else {
      html.push('<br>')
    }
    html.push(formatInlineMarkdown(line))
  }

  closeTrainingDayCard()
  closeTable()
  closeBlockquote()
  closeList()
  closeParagraph()

  return html.join('')
}

const levelAwareIsTrainingDayHeading = (text = '') =>
  /^训练日\s*[一二三四五六七1234567890]+$/i.test(String(text || '').trim())

const parseTrainingDayHeadingLine = (text = '') => {
  const normalized = String(text || '').trim()
  if (!normalized) return ''

  const match = normalized.match(/^(训练日\s*[一二三四五六七1234567890]+)\s*[:：]?\s*(.*)$/i)
  if (!match) return ''

  const label = normalizeTrainingDayHeading(match[1] || '')
  const suffix = normalizeTrainingDayHeading(match[2] || '')
  return suffix ? `${label}：${suffix}` : label
}

const normalizePlanText = (text = '') =>
  String(text || '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/&nbsp;/g, ' ')
    .replace(/\r\n/g, '\n')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/__(.*?)__/g, '$1')
    .replace(/`(.*?)`/g, '$1')
    .replace(/\[(.*?)\]\(.*?\)/g, '$1')
    .replace(/^#+\s*/gm, '')
    .trim()

const contentSegments = (plan) =>
  removeMarkdownFormat(String(plan?.content || ''))
    .split(/\n+/)
    .map((segment) => segment.trim())
    .filter(Boolean)

const getCleanCellText = (value = '') =>
  removeMarkdownFormat(
    String(value || '')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/&nbsp;/g, ' ')
  )
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .join('\n')

const sessionTitlePattern = /^(第\s*\d+\s*(天|次)|训练日\s*[一二三四五六七1234567]|day\s*\d+|周[一二三四五六日天])[:：]?\s*(.*)$/i

const isSessionTitleLine = (line = '') => sessionTitlePattern.test(line.trim())

const extractTableSessions = (text = '') => {
  const lines = text.split('\n')
  const sessions = []

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index].trim()
    if (!line.includes('|')) continue

    const headerCells = line.split('|').map((cell) => cell.trim()).filter(Boolean)
    const separatorLine = lines[index + 1]?.trim() || ''
    const isHeaderSeparator = /^[\s|:-]+$/.test(separatorLine)
    if (!headerCells.length || !isHeaderSeparator) continue

    const dayIndex = headerCells.findIndex((cell) => /训练日|第.?天|day|星期|周几/i.test(cell))
    const themeIndex = headerCells.findIndex((cell) => /主题|训练主题|项目|内容概览/i.test(cell))
    const durationIndex = headerCells.findIndex((cell) => /时长|时间|分钟/i.test(cell))
    const focusIndex = headerCells.findIndex((cell) => /训练重点|重点|动作|主训练|训练内容/i.test(cell))
    const recoveryIndex = headerCells.findIndex((cell) => /恢复建议|恢复|放松/i.test(cell))

    if ([dayIndex, themeIndex, durationIndex, focusIndex, recoveryIndex].every((value) => value === -1)) continue

    index += 2
    while (index < lines.length) {
      const rowLine = lines[index].trim()
      if (!rowLine.includes('|')) {
        index -= 1
        break
      }
      if (/^[\s|:-]+$/.test(rowLine)) {
        index += 1
        continue
      }

      const cells = rowLine.split('|').map((cell) => cell.trim()).filter(Boolean)
      if (!cells.length) {
        index += 1
        continue
      }

      const dayLabel = dayIndex >= 0 ? getCleanCellText(cells[dayIndex] || '') : ''
      const theme = themeIndex >= 0 ? getCleanCellText(cells[themeIndex] || '') : ''
      const duration = durationIndex >= 0 ? getCleanCellText(cells[durationIndex] || '') : ''
      const focus = focusIndex >= 0 ? getCleanCellText(cells[focusIndex] || '') : ''
      const recovery = recoveryIndex >= 0 ? getCleanCellText(cells[recoveryIndex] || '') : ''

      if (dayLabel || theme || focus) {
        sessions.push({
          dayLabel,
          title: theme || dayLabel,
          duration,
          focus: theme || focus,
          recovery,
          summary: focus || theme || ''
        })
      }
      index += 1
    }
  }

  return sessions
}

const extractBlockSessions = (text = '') => {
  const lines = String(text || '').replace(/\r\n/g, '\n').split('\n')
  const sessions = []
  let current = null

  const pushCurrent = () => {
    if (!current) return
    const summary = current.summaryLines.join('\n').trim()
    if (current.title || summary) {
      sessions.push({
        dayLabel: current.dayLabel,
        title: current.title || current.dayLabel || '',
        duration: current.duration,
        focus: current.focus || current.title || '',
        recovery: current.recovery,
        summary
      })
    }
    current = null
  }

  for (const rawLine of lines) {
    const normalizedLine = removeMarkdownFormat(rawLine).trim()
    if (!normalizedLine) {
      if (current) current.summaryLines.push('')
      continue
    }

    if (/^第\s*\d+\s*周[:：]?$/.test(normalizedLine) || /^##\s*第\s*\d+\s*周/.test(rawLine.trim())) {
      pushCurrent()
      continue
    }

    const titleMatch = normalizedLine.match(sessionTitlePattern)
    if (titleMatch) {
      pushCurrent()
      current = {
        dayLabel: titleMatch[1]?.trim() || '',
        title: titleMatch[3]?.trim() || titleMatch[1]?.trim() || '',
        duration: '',
        focus: '',
        recovery: '',
        summaryLines: []
      }
      continue
    }

    if (!current) continue

    if (/^(训练主题|主题)[:：]/.test(normalizedLine)) {
      current.title = normalizedLine.replace(/^(训练主题|主题)[:：]\s*/, '').trim() || current.title
      continue
    }

    if (/^(建议时长|训练时长|时长|训练时间)[:：]/.test(normalizedLine)) {
      current.duration = normalizedLine.replace(/^(建议时长|训练时长|时长|训练时间)[:：]\s*/, '').trim()
      continue
    }

    if (/^(恢复建议|恢复|放松建议)[:：]/.test(normalizedLine)) {
      current.recovery = normalizedLine.replace(/^(恢复建议|恢复|放松建议)[:：]\s*/, '').trim()
      continue
    }

    if (/^(训练重点|重点|主训练)[:：]/.test(normalizedLine)) {
      current.focus = normalizedLine.replace(/^(训练重点|重点|主训练)[:：]\s*/, '').trim()
    }

    current.summaryLines.push(rawLine)
  }

  pushCurrent()
  return sessions
}

const extractMarkdownSessions = (text = '') => {
  const lines = String(text || '').replace(/\r\n/g, '\n').split('\n')
  const sessions = []
  let current = null

  const pushCurrent = () => {
    if (!current) return
    const summary = current.lines.join('\n').trim()
    if (!summary) {
      current = null
      return
    }

    const titleMatch = summary.match(/(?:^|\n)(?:[-*]\s*)?训练主题[:：]\s*(.+)/)
    const durationMatch = summary.match(/(?:^|\n)(?:[-*]\s*)?(?:建议时长|训练时长|时长|训练时间)[:：]\s*(.+)/)
    const recoveryMatch = summary.match(/(?:^|\n)(?:[-*]\s*)?(?:恢复建议|恢复|放松建议)[:：]\s*(.+)/)
    const focusMatch = summary.match(/(?:^|\n)(?:[-*]\s*)?(?:训练重点|重点|主训练)[:：]\s*(.+)/)

    sessions.push({
      dayLabel: current.dayLabel,
      title: (titleMatch?.[1] || current.title || current.dayLabel || '').trim(),
      duration: (durationMatch?.[1] || '').trim(),
      focus: (focusMatch?.[1] || titleMatch?.[1] || current.title || '').trim(),
      recovery: (recoveryMatch?.[1] || '').trim(),
      summary
    })
    current = null
  }

  for (const rawLine of lines) {
    const trimmedLine = rawLine.trim()
    const normalizedLine = removeMarkdownFormat(trimmedLine).trim()

    if (/^##\s*第\s*\d+\s*周/.test(trimmedLine) || /^第\s*\d+\s*周[:：]?$/.test(normalizedLine)) {
      pushCurrent()
      continue
    }

    const headingMatch = trimmedLine.match(/^#{1,4}\s*(训练日\s*[一二三四五六七1234567]+)\s*(.*)$/i)
    const plainMatch = !headingMatch ? normalizedLine.match(/^(训练日\s*[一二三四五六七1234567]+)[:：]?\s*(.*)$/i) : null
    const titleMatch = headingMatch || plainMatch

    if (titleMatch) {
      pushCurrent()
      current = {
        dayLabel: normalizeTrainingDayHeading(titleMatch[1]?.trim() || ''),
        title: normalizeTrainingDayHeading(titleMatch[2]?.trim() || titleMatch[1]?.trim() || ''),
        lines: [rawLine]
      }
      continue
    }

    if (!current) continue
    current.lines.push(rawLine)
  }

  pushCurrent()
  return sessions
}

const extractPlanSessions = (plan) => {
  const rawContent = String(plan?.content || '')
  const rawText = normalizePlanText(rawContent)
  if (!rawText) return []

  const markdownSessions = extractMarkdownSessions(rawContent)
  if (markdownSessions.length) return markdownSessions

  const blockSessions = extractBlockSessions(rawText)
  if (blockSessions.length) return blockSessions

  const tableSessions = extractTableSessions(rawText)
  if (tableSessions.length) return tableSessions

  return contentSegments(plan).map((segment, index) => ({
    dayLabel: `第 ${index + 1} 次训练`,
    title: `第 ${index + 1} 次训练`,
    duration: '',
    focus: '',
    recovery: '',
    summary: segment
  }))
}

const getRecoveryText = (plan) => {
  const intensity = String(plan?.metadata?.intensity || '')
  if (intensity.includes('高')) return '训练后增加拉伸和补水，第二天注意恢复。'
  if (intensity.includes('中')) return '注意呼吸节奏，并安排轻量恢复。'
  return '保持动作质量，训练后适度放松。'
}

const getEntryTitle = (session, index) => {
  const dayLabel = normalizeTrainingDayHeading(session?.dayLabel || '').replace(/[:：]\s*$/, '')
  const title = normalizeTrainingDayHeading(session?.title || '').replace(/^[：:\s]+/, '').trim()

  if (dayLabel && title && title !== dayLabel) return `${dayLabel}：${title}`
  if (dayLabel) return dayLabel
  if (title) return title
  return `第 ${index + 1} 次训练`
}

const buildTrainingEntries = (plan) => {
  if (!plan) return []

  const weekdays = getSelectedWeekdays(plan)
  if (!weekdays.length) return []

  const start = new Date(plan.start_date || new Date())
  const end = new Date(plan.end_date || addDays(plan.start_date || new Date().toISOString(), 29))
  const sessions = extractPlanSessions(plan)
  const entries = []
  let sessionIndex = 0

  for (const cursor = new Date(start); cursor <= end; cursor.setDate(cursor.getDate() + 1)) {
    const weekday = weekdayHeaders[(cursor.getDay() + 6) % 7]
    if (!weekdays.includes(weekday)) continue

    const session = sessions[sessionIndex] || sessions[sessionIndex % Math.max(sessions.length, 1)] || null

    entries.push({
      date: getDateKey(cursor),
      title: getEntryTitle(session, sessionIndex),
      duration: session?.duration || `${plan?.metadata?.daily_duration || 30} 分钟`,
      focus: session?.focus || `${plan?.metadata?.method || '综合训练'} · ${plan?.goal || '训练目标'}`,
      recovery: session?.recovery || getRecoveryText(plan),
      summary: session?.summary || '按照计划完成今天的训练内容。'
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
  const storedPlanId = Number(localStorage.getItem(getUserActivePlanKey()))
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

const openPlanDetail = (plan) => {
  if (!plan) return
  const detail = typeof plan === 'object'
    ? normalizePlan(plan)
    : normalizePlan(plans.value.find((item) => item.id === Number(plan)) || {})
  if (!detail || !detail.id) return
  planDetail.value = detail
}

const closePlanDetail = () => {
  planDetail.value = null
}

const switchCurrentPlan = (planId) => {
  activePlanId.value = planId
  localStorage.setItem(getUserActivePlanKey(), String(planId))
  boardEntry.value = null
}

const openBoardEntry = (entry) => {
  boardEntry.value = entry
}

const closeBoardEntry = () => {
  boardEntry.value = null
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
  const limit = getPlanWeekdayLimit(weekdayPlan.value)
  if (!weekdayDraft.value.includes(day) && weekdayDraft.value.length >= limit) return
  weekdayDraft.value = weekdayDraft.value.includes(day)
    ? weekdayDraft.value.filter((item) => item !== day)
    : [...weekdayDraft.value, day]
}

const isWeekdayDisabled = (day) => !weekdayDraft.value.includes(day) && weekdayDraft.value.length >= getPlanWeekdayLimit(weekdayPlan.value)

const saveWeekdays = async () => {
  if (!weekdayPlan.value || !weekdayDraft.value.length) return

  try {
    const response = await api.put(`/training/plans/${weekdayPlan.value.id}`, {
      selected_weekdays: [...weekdayDraft.value]
    })
    applyUpdatedPlan(response.plan)
    localStorage.setItem(getUserActivePlanKey(), String(weekdayPlan.value.id))
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
    content: plan.content || '',
    selected_weekdays: [...getSelectedWeekdays(plan)]
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editTargetPlan.value = null
}

const toggleEditWeekday = (day) => {
  const limit = getEditWeekdayLimit()
  if (!editForm.value.selected_weekdays.includes(day) && editForm.value.selected_weekdays.length >= limit) return
  editForm.value.selected_weekdays = editForm.value.selected_weekdays.includes(day)
    ? editForm.value.selected_weekdays.filter((item) => item !== day)
    : [...editForm.value.selected_weekdays, day]
}

const isEditWeekdayDisabled = (day) =>
  !editForm.value.selected_weekdays.includes(day) &&
  editForm.value.selected_weekdays.length >= getEditWeekdayLimit()

const saveEdit = async () => {
  if (!editTargetPlan.value) return

  const payload = {
    title: editForm.value.title,
    goal: editForm.value.goal,
    content: editForm.value.content,
    selected_weekdays: [...editForm.value.selected_weekdays],
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
      localStorage.setItem(getUserActivePlanKey(), String(activePlanId.value))
    } else {
      localStorage.removeItem(getUserActivePlanKey())
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
      localStorage.setItem(getUserActivePlanKey(), String(value))
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
/* ========================================
   动态运动训练主题设计
   Dynamic Sports Training Design
   ======================================== */

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

/* CSS 变量定义 */
.training-plan-page {
  --primary-gradient: linear-gradient(135deg, #0071e3 0%, #0077ed 50%, #42a5f5 100%);
  --primary-gradient-reverse: linear-gradient(135deg, #42a5f5 0%, #0077ed 50%, #0071e3 100%);
  --secondary-gradient: linear-gradient(135deg, #1d1d1f 0%, #86868b 100%);
  --accent-blue: #0071e3;
  --accent-blue-light: #0077ed;
  --accent-sky: #42a5f5;
  --bg-primary: #f5f5f7;
  --bg-secondary: #ffffff;
  --bg-elevated: #ffffff;
  --text-primary: #1d1d1f;
  --text-secondary: #86868b;
  --text-tertiary: #d2d2d7;
  --border-light: rgba(0, 113, 227, 0.12);
  --border-subtle: rgba(0, 0, 0, 0.06);
  --shadow-soft: 0 4px 20px rgba(0, 0, 0, 0.04);
  --shadow-medium: 0 8px 32px rgba(0, 0, 0, 0.06);
  --shadow-glow: 0 8px 32px rgba(0, 113, 227, 0.18);
  --shadow-elevated: 0 12px 40px rgba(0, 113, 227, 0.12);
}

/* 页面基础 */
.training-plan-page {
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--text-primary);
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.page-container {
  max-width: 1440px;
  margin: 0 auto;
  padding: 32px 24px 24px 32px;
}

/* ==================== 头部样式 ==================== */
.page-header {
  background: var(--bg-elevated);
  border-radius: 28px;
  padding: 40px;
  margin-bottom: 40px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-elevated);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--primary-gradient);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 32px;
  position: relative;
  z-index: 1;
}

.header-text {
  flex: 1;
}

.header-label {
  display: inline-block;
  padding: 8px 16px;
  background: var(--primary-gradient);
  color: white;
  border-radius: 24px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 16px;
  animation: slideDown 0.5s ease-out 0.2s both;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 36px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 12px 0;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.header-description {
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin: 0;
  max-width: 600px;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

/* ==================== 按钮样式 ==================== */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 28px;
  border-radius: 16px;
  border: none;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  white-space: nowrap;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 16px;
  background: var(--primary-gradient);
  opacity: 0;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease, opacity 0.4s ease;
}

.btn:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-glow);
}

.btn:hover::before {
  opacity: 0.1;
  transform: scaleX(1);
}

.btn:active {
  transform: translateY(-1px);
}

.btn:active::before {
  opacity: 0.15;
}

.btn-icon {
  width: 18px;
  height: 18px;
  stroke-width: 2;
  stroke: currentColor;
  position: relative;
  z-index: 2;
}

@keyframes currentColor {
  0% { stroke: white; }
  100% { stroke: white; }
}

.btn-primary {
  background: var(--primary-gradient);
  color: white;
  box-shadow: var(--shadow-glow);
  border: none;
}

.btn-day-badge {
  background: #c8e0ff;
  color: #0f3f7d;
  border: none;
  box-shadow: none;
}

.btn-day-badge:hover {
  background: #aed1ff;
  box-shadow: 0 4px 16px rgba(15, 63, 125, 0.15);
}

.btn-day-badge .btn-icon {
  stroke: #0f3f7d;
}

.btn-primary:hover {
  background: var(--primary-gradient-reverse);
  box-shadow: 0 12px 48px rgba(255, 107, 74, 0.25);
}

.btn-primary .btn-icon {
  stroke: white;
  animation: currentColor 0.3s linear;
}

.btn-secondary {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}

.btn-secondary:hover {
  background: rgba(255, 107, 74, 0.08);
  border-color: var(--accent-orange);
}

.btn-outline {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}

.btn-outline:hover {
  background: rgba(255, 107, 74, 0.05);
  border-color: var(--accent-orange);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.08);
  color: #DC2626;
  border: 1px solid rgba(239, 68, 68, 0.15);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: #B91C1C;
}

.btn-icon.btn-icon {
  padding: 10px;
  width: 40px;
  height: 40px;
  border-radius: 12px;
}

.btn.small {
  padding: 10px 20px;
  font-size: 13px;
}

/* ==================== 布局样式 ==================== */
.detail-view {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

.dashboard-view {
  margin-bottom: 32px;
}

.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.dashboard-top {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 24px;
}

.dashboard-bottom,
.dashboard-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.empty-dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-sidebar,
.dashboard-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-main,
.dashboard-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ==================== 卡片基础样式 ==================== */
.plan-card,
.current-plan-card,
.training-content-card,
.history-card,
.calendar-card,
.placeholder-card {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 20px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-soft);
  transition: all 0.3s ease;
}

.plan-card:hover,
.current-plan-card:hover,
.placeholder-card:hover {
  box-shadow: var(--shadow-elevated);
  border-color: var(--accent-orange);
  transform: translateY(-2px);
}

.placeholder-card {
  background: rgba(255, 255, 255, 0.6);
  border: 2px dashed var(--border-light);
}

.placeholder-card:hover {
  background: rgba(255, 255, 255, 0.8);
  border-color: var(--accent-orange);
}

/* ==================== 计划卡片样式 ==================== */
.plan-header {
  margin-bottom: 24px;
}

.plan-badge-row {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.badge-ai {
  background: var(--primary-gradient);
  color: white;
}

.badge-method {
  background: rgba(34, 197, 94, 0.15);
  color: #16A34A;
}

.badge.small {
  padding: 4px 10px;
  font-size: 10px;
}

.plan-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 26px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.plan-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.plan-meta-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.meta-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 18px;
  background: var(--bg-primary);
  border-radius: 20px;
  border: 1px solid var(--border-light);
  transition: all 0.2s ease;
}

.meta-item:hover {
  background: rgba(255, 107, 74, 0.05);
  border-color: var(--accent-orange);
}

.meta-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  color: var(--accent-orange);
}

.meta-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin: 0 0 4px 0;
  font-weight: 600;
}

.meta-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}

/* ==================== 计划内容样式 ==================== */
.plan-content {
  margin-bottom: 24px;
}

.content-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 20px 0;
  color: var(--text-primary);
}

.title-icon {
  width: 20px;
  height: 20px;
  color: var(--accent-orange);
}

.content-body {
  background: var(--bg-primary);
  border-radius: 16px;
  padding: 24px;
  border: 1px solid var(--border-light);
}

.markdown-content {
  color: var(--text-primary);
  line-height: 1.75;
  max-width: 920px;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  font-family: 'Space Grotesk', sans-serif;
  line-height: 1.3;
  color: var(--text-primary);
  margin: 0 0 12px;
}

.markdown-content :deep(h1) {
  font-size: 30px;
  margin-top: 0;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(0, 113, 227, 0.12);
}

.markdown-content :deep(h2) {
  font-size: 22px;
  margin-top: 28px;
  margin-bottom: 14px;
  padding-left: 12px;
  border-left: 4px solid var(--accent-orange);
}

.markdown-content :deep(h3) {
  font-size: 19px;
  margin-top: 22px;
  margin-bottom: 14px;
  padding: 10px 14px;
  background: rgba(0, 113, 227, 0.05);
  border: 1px solid rgba(0, 113, 227, 0.1);
  border-radius: 14px;
}

.markdown-content :deep(.training-day-card) {
  margin: 22px 0 26px;
  padding: 18px 18px 8px;
  background: linear-gradient(180deg, rgba(0, 113, 227, 0.06) 0%, rgba(255, 255, 255, 0.92) 100%);
  border: 1px solid rgba(0, 113, 227, 0.12);
  border-radius: 20px;
  box-shadow: 0 10px 26px rgba(0, 113, 227, 0.08);
}

.markdown-content :deep(.training-day-card h3) {
  margin-top: 0;
  margin-bottom: 16px;
  background: rgba(255, 255, 255, 0.86);
  border-color: rgba(0, 113, 227, 0.14);
}

.markdown-content :deep(.training-day-card ul),
.markdown-content :deep(.training-day-card ol) {
  margin-bottom: 16px;
}

.markdown-content :deep(.training-day-card p:last-child),
.markdown-content :deep(.training-day-card ul:last-child),
.markdown-content :deep(.training-day-card ol:last-child),
.markdown-content :deep(.training-day-card blockquote:last-child),
.markdown-content :deep(.training-day-card table:last-child) {
  margin-bottom: 10px;
}

.markdown-content :deep(h4) {
  font-size: 15px;
  margin-top: 14px;
}

.markdown-content :deep(p) {
  margin: 0 0 12px;
  font-size: 15px;
  line-height: 1.85;
}

.markdown-content :deep(ul) {
  margin: 0 0 18px;
  padding-left: 24px;
}

.markdown-content :deep(.nested-list) {
  margin: 12px 0 4px;
  padding-left: 26px;
}

.markdown-content :deep(li) {
  margin: 0 0 12px;
  font-size: 15px;
  line-height: 1.85;
}

.markdown-content :deep(.list-group-title) {
  margin-bottom: 8px;
  font-weight: 600;
}

.markdown-content :deep(.nested-list-item) {
  margin: 0 0 10px;
  color: rgba(28, 28, 30, 0.9);
}

.markdown-content :deep(strong) {
  font-weight: 700;
  color: #173f34;
}

.markdown-content :deep(code) {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(0, 113, 227, 0.08);
  font-size: 12px;
}

.markdown-content :deep(blockquote) {
  margin: 0 0 14px;
  padding: 12px 14px;
  border-left: 3px solid var(--accent-blue);
  background: rgba(0, 113, 227, 0.05);
  border-radius: 0 12px 12px 0;
}

.markdown-content :deep(ol) {
  margin: 0 0 14px;
  padding-left: 22px;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0 0 16px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--border-light);
  border-radius: 14px;
  overflow: hidden;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-light);
  text-align: left;
  vertical-align: top;
  font-size: 14px;
  line-height: 1.6;
}

.markdown-content :deep(th) {
  background: rgba(0, 113, 227, 0.06);
  font-weight: 700;
}

.markdown-content :deep(tr:last-child td) {
  border-bottom: none;
}

.markdown-content :deep(.md-divider) {
  border: none;
  height: 1px;
  margin: 18px 0 22px;
  background: linear-gradient(90deg, transparent, rgba(0, 113, 227, 0.18), transparent);
}

.entry-markdown-wrapper {
  margin-top: 8px;
}

.entry-markdown {
  width: 100%;
}

.entry-markdown :deep(h1) {
  font-size: 22px;
}

.entry-markdown :deep(h2) {
  font-size: 18px;
  margin-top: 22px;
}

.entry-markdown :deep(h3) {
  font-size: 16px;
  padding: 8px 12px;
}

.entry-markdown :deep(h4) {
  font-size: 14px;
}

.entry-markdown :deep(p),
.entry-markdown :deep(li) {
  font-size: 14px;
  line-height: 1.75;
}

.card-section-divider {
  height: 1px;
  background: var(--border-light);
  margin: 20px 0;
}

.management-intro {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.management-text {
  flex: 1;
}

.management-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text-primary);
}

.management-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.management-create-btn {
  flex-shrink: 0;
}

/* ==================== 卡片头部样式 ==================== */
.card-header {
  margin-bottom: 20px;
}

.history-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.card-header h3 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.plan-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.current-plan-card,
.history-card {
  /* min-height: 160px; */
  max-height: 270px;
  /* overflow: hidden; */
}

.history-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.history-nav-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.history-footer {
  /* margin-top: 3px; */
  display: flex;
  justify-content: flex-end;
}

.card-label {
  font-size: 10px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
  font-weight: 700;
}

.card-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: var(--text-primary);
}

.card-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* ==================== 标签样式 ==================== */
.plan-tags,
.item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.tag {
  display: inline-block;
  padding: 8px 16px;
  background: var(--bg-primary);
  color: var(--text-primary);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid var(--border-light);
}

.tag.small {
  padding: 5px 12px;
  font-size: 11px;
}

/* ==================== 操作按钮组 ==================== */
.plan-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.plan-actions .action-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-left: auto;
}

.action-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.detail-row:last-child {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  border-bottom: none;
  padding-top: 12px;
}

.detail-label {
  font-size: 11px;
  color: var(--text-tertiary);
  margin: 0;
  font-weight: 600;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.detail-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  margin: 0;
  padding: 12px;
  background: var(--bg-primary);
  border-radius: 12px;
}

/* ==================== 弹出训练卡片 ==================== */
.board-entry-overlay {
  position: fixed;
  inset: 0;
  background: rgba(17, 24, 39, 0.35);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 950;
}

.board-entry-card {
  width: min(560px, 100%);
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  border-radius: 24px;
  box-shadow: var(--shadow-elevated);
  padding: 24px;
  animation: modalIn 0.25s ease-out;
}

.board-entry-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.board-entry-header h4 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.board-entry-plan {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.board-entry-close,
.modal-close {
  background: #ffffff;
  flex-shrink: 0;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.board-entry-close svg,
.modal-close svg {
  width: 18px;
  height: 18px;
}

.board-entry-close:hover,
.modal-close:hover {
  color: var(--text-primary);
  background: var(--bg-primary);
}

.empty-icon {
  width: 56px;
  height: 56px;
  color: var(--border-light);
  margin-bottom: 20px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 0.7;
  }
}

.content-empty p {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.6;
}

.empty-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 8px;
}

/* ==================== 日历部分样式 ==================== */
.calendar-section {
  background: var(--bg-elevated);
  border-radius: 24px;
  padding: 28px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-soft);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h3 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: center;
}

.calendar-nav .btn.btn-icon {
  background: transparent !important;
  color: #1d1d1f !important;
  border: none !important;
  box-shadow: none !important;
  width: 40px !important;
  height: 40px !important;
  padding: 0 !important;
}

.calendar-nav .btn.btn-icon:hover {
  background: rgba(0, 113, 227, 0.08) !important;
  color: #1d1d1f !important;
}

.calendar-nav .btn.btn-icon svg {
  display: block !important;
  width: 24px !important;
  height: 24px !important;
  stroke: #1d1d1f !important;
  stroke-width: 2.5 !important;
}

/* ==================== 训练条目样式 ==================== */
.training-entry {
  background: var(--bg-primary);
  border-radius: 20px;
  padding: 24px;
  margin-top: 24px;
  border: 1px solid var(--border-light);
  animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
  color: var(--accent-orange);
  font-weight: 600;
  margin-bottom: 4px;
}

.entry-header h4 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.entry-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

/* ==================== 历史计划样式 ==================== */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 4px 0;
  transition: all 0.2s ease;
}

.history-item:hover {
}

.history-item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.history-item-header h4 {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.item-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

.item-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: var(--text-secondary);
}

/* ==================== 空状态带日历 ==================== */
.empty-state-with-calendar {
  margin-bottom: 32px;
}

/* ==================== 占位卡片样式 ==================== */
.placeholder-illustration {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 24px;
}

.placeholder-illustration svg {
  width: 80px;
  height: 80px;
}

.placeholder-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.placeholder-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.placeholder-content-empty {
  text-align: center;
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.create-btn {
  width: 100%;
  margin-top: 20px;
}

/* ==================== 模态框样式 ==================== */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.2s ease-out;
}

.modal-container {
  background: var(--bg-elevated);
  border-radius: 28px;
  width: 100%;
  max-width: 540px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.25);
  animation: modalIn 0.3s ease-out;
}

@keyframes modalIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-container.wide {
  max-width: 840px;
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.modal-icon {
  width: 24px;
  height: 24px;
  color: var(--accent-orange);
}


.modal-body {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.modal-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 24px 0;
  line-height: 1.6;
}

.modal-footer {
  padding: 20px 32px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* ==================== 训练日选择器 ==================== */
.weekday-selector {
  margin-bottom: 24px;
}

.weekday-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

.edit-weekday-grid {
  margin-top: 4px;
}

.weekday-option {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-light);
  border-radius: 16px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 12px 8px;
  position: relative;
  overflow: hidden;
}

.weekday-option::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: 14px;
  background: var(--primary-gradient);
  opacity: 0;
  transform: scale(0.9);
  transition: all 0.3s ease;
}

.weekday-option:hover {
  border-color: var(--accent-orange);
  background: rgba(255, 107, 74, 0.03);
}

.weekday-option:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.weekday-option.selected {
  border-color: var(--accent-orange);
  background: rgba(255, 107, 74, 0.05);
}

.weekday-option.selected::before {
  opacity: 0.15;
  transform: scale(1);
}

.weekday-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  position: relative;
  z-index: 2;
}

.weekday-check {
  margin-top: 6px;
  width: 16px;
  height: 16px;
  color: white;
}

/* ==================== 表单样式 ==================== */
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-hint {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.label-text {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.form-input,
.form-textarea {
  padding: 14px 16px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  font-family: inherit;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-elevated);
  transition: all 0.2s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--accent-orange);
  box-shadow: 0 0 0 0 3px rgba(255, 107, 74, 0.15);
  background: white;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: var(--text-tertiary);
}

.form-textarea {
  resize: vertical;
  min-height: 140px;
  line-height: 1.6;
}

/* ==================== 日历组件深度样式 ==================== */
:deep(.calendar-box) {
  margin-top: 0;
  padding: 24px;
  border-radius: 20px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-soft);
}

:deep(.calendar-head) {
  display: none;
}

:deep(.calendar-grid) {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

:deep(.calendar-weekday) {
  text-align: center;
  padding: 12px 8px;
  background: var(--bg-primary);
  border-radius: 12px;
  font-weight: 600;
  font-size: 13px;
  color: var(--text-secondary);
}

:deep(.calendar-day) {
  min-height: 120px;
  padding: 14px;
  border-radius: 16px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: all 0.2s ease;
}

:deep(.calendar-day:not(.empty):hover) {
  border-color: var(--accent-orange);
  box-shadow: var(--shadow-medium);
  transform: translateY(-3px);
}

:deep(.calendar-day.empty) {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
}

:deep(.calendar-day.today) {
  background: transparent;
  border-color: var(--border-light);
  color: inherit;
}

:deep(.calendar-day.today .day-number) {
  width: 36px;
  height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 192, 203, 0.35);
  color: #000000;
}

:deep(.calendar-day.today:not(.active) .day-badge),
:deep(.calendar-day.today:not(.active) .day-action) {
  color: inherit;
}

:deep(.calendar-day.today:not(.active) .day-action) {
  background: rgba(255, 255, 255, 0.08);
}

:deep(.calendar-day.active) {
  background: transparent;
  border-color: var(--accent-orange);
}

:deep(.calendar-day.active .day-number) {
  color: var(--text-primary);
}

:deep(.calendar-day.active .day-action) {
  background: #ffffff;
  color: #000000;
}

:deep(.calendar-day.active.today .day-number) {
  background: rgba(255, 107, 74, 0.12);
  color: #000000;
}

:deep(.calendar-day-top) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.day-number) {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

:deep(.day-badge) {
  padding: 4px 10px;
  background: #c8e0ff;
  /* color: white; */
  border-radius: 12px;
  font-size: 10px;
  font-weight: 700;
}

:deep(.day-action) {
  width: 70%;
  padding: 10px;
  border-radius: 10px;
  border: none;
  background: #e4f0ff;
  color: #0f3f7d;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-left: 15%;
  margin-top: 5%;
}

:deep(.day-action:hover) {
  background: #c8e0ff;
  color: #0f3f7d;
  transform: scale(1.02);
}

:deep(.btn-ghost) {
  background: transparent;
  color: var(--text-secondary);
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
}

:deep(.btn-ghost:hover) {
  background: var(--bg-primary);
  color: var(--text-primary);
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 1280px) {
  .empty-dashboard-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .detail-sidebar,
  .dashboard-sidebar {
    order: 2;
  }

  .detail-main,
  .dashboard-main {
    order: 1;
  }
}

@media (max-width: 960px) {
  .dashboard-top,
  .dashboard-bottom,
  .dashboard-right {
    display: flex;
    flex-direction: column;
  }
}

@media (max-width: 992px) {
  .page-container {
    padding: 20px 16px 20px 16px;
  }

  .detail-view {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .dashboard-grid,
  .empty-dashboard-grid {
    gap: 20px;
  }

  .weekday-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-container {
    margin: 10px;
    border-radius: 20px;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 20px;
  }

  .management-intro {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .action-group {
    flex-wrap: wrap;
  }

  .btn.small {
    padding: 12px 16px;
    font-size: 13px;
  }

  .weekday-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
  }

  :deep(.calendar-day) {
    min-height: 100px;
    padding: 10px;
  }

  :deep(.day-number) {
    font-size: 14px;
  }

  :deep(.day-badge) {
    font-size: 9px;
    padding: 3px 6px;
  }

  :deep(.day-action) {
    font-size: 10px;
    padding: 8px;
  }

  .modal-container.wide {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .header-title {
    font-size: 26px;
  }

  .plan-title,
  .card-title {
    font-size: 18px;
  }

  .section-header h3,
  .calendar-title {
    font-size: 16px;
  }

  :deep(.calendar-weekday) {
    font-size: 11px;
    padding: 8px 6px;
  }

  :deep(.day-number) {
    font-size: 13px;
  }

  .tag {
    font-size: 11px;
    padding: 6px 12px;
  }

  .entry-details {
    grid-template-columns: 1fr;
  }

  .placeholder-illustration svg {
    width: 60px;
    height: 60px;
  }

  .placeholder-content-empty svg {
    width: 40px;
    height: 40px;
  }

}
</style>
