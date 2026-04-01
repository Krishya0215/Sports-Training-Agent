<template>
  <div class="chat-page">
    <Navbar />

    <div class="chat-shell">
      <aside class="sidebar card">
        <div class="sidebar-head">
          <div>
            <!-- <p class="sidebar-eyebrow">AI Coach</p> -->
            <h2>最近对话</h2>
          </div>
          <div class="sidebar-actions">
            <button class="icon-btn" type="button" @click="newChat">+</button>
          </div>
        </div>

        <div class="history-list">
          <article
            v-for="(chat, index) in chatHistory"
            :key="`${chat.timestamp}-${index}`"
            class="history-item"
            :class="{ active: currentChat === index }"
          >
            <button type="button" class="history-main" @click="loadChatHistory(index)">
              <strong>{{ shorten(chat.question) }}</strong>
              <span>{{ formatTime(chat.timestamp) }}</span>
            </button>
            <button
              type="button"
              class="history-delete"
              title="Delete chat"
              aria-label="Delete chat"
              @click.stop="deleteChatHistory(index)"
            >
              Delete
            </button>
          </article>
          <p v-if="!chatHistory.length" class="empty-copy">还没有历史对话</p>
        </div>
      </aside>

      <section class="main card">
        <header class="main-head">
          <div>
            <h1>{{ currentChat !== null ? `对话 #${currentChat + 1}` : '开始新对话' }}</h1>
          </div>
          <!-- <button v-if="messages.length" type="button" class="btn btn-secondary" @click="newChat">
            新建对话
          </button> -->
        </header>

        <div ref="messagesContainer" class="messages">
          <div v-if="!messages.length" class="empty-state">
            <div class="empty-badge">AI</div>
            <h3>开始和 AI 教练对话吧！</h3>
            <p>询问有关训练计划、运动恢复方面的问题，AI教练会提供帮助。</p>
            <div class="quick-suggestions">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion"
                type="button"
                class="suggestion-chip"
                @click="sendMessage(suggestion)"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>

          <template v-else>
            <article
              v-for="(message, index) in messages"
              :key="`${message.timestamp}-${index}`"
              class="message-row"
              :class="message.role"
            >
              <div class="avatar">{{ message.role === 'user' ? '我' : 'AI' }}</div>
              <div class="message-card">
                <div
                  v-if="message.role === 'assistant' && (message.thinking || message.progressLogs?.length)"
                  class="thinking-container"
                >
                  <button 
                    type="button" 
                    class="thinking-toggle"
                    @click="message.isThinkingExpanded = !message.isThinkingExpanded"
                  >
                    <span class="thinking-icon">{{ message.isThinkingExpanded ? '▼' : '▶' }}</span>
                    <span class="thinking-label">🧠 生成过程</span>
                  </button>
                  <div v-if="message.isThinkingExpanded" class="thinking-content">
                    <div v-if="message.progressLogs?.length" class="progress-block">
                      <div class="progress-head">
                        <p class="progress-tag">生成进度</p>
                        <span class="progress-count">{{ message.progressLogs.length }} 个步骤</span>
                      </div>
                      <div class="progress-list">
                        <p
                          v-for="(log, logIndex) in message.progressLogs"
                          :key="`${log}-${logIndex}`"
                          class="progress-item"
                        >
                          {{ log }}
                        </p>
                      </div>
                    </div>

                    <!-- <div v-if="message.thinking" class="thinking-block">
                      <p class="progress-tag">教练思路</p>
                      <p v-for="(line, lineIndex) in message.thinking.split('\n')" 
                         :key="lineIndex"
                         class="thinking-line">
                        {{ line }}
                      </p>
                    </div> -->
                  </div>
                </div>

                <div
                  v-if="message.role === 'assistant' && message.scheduler"
                  class="scheduler-card"
                >
                  <div class="scheduler-head">
                    <div>
                      <p class="scheduler-tag">协作分析</p>
                      <h4>{{ getSchedulerHeadline(message.scheduler.coaches.length) }}</h4>
                    </div>
                    <button
                      type="button"
                      class="scheduler-toggle"
                      @click="message.isSchedulerExpanded = !message.isSchedulerExpanded"
                    >
                      {{ message.isSchedulerExpanded ? '收起' : '展开' }}
                    </button>
                  </div>

                  <p v-if="message.scheduler.reasonText" class="scheduler-copy">
                    {{ message.scheduler.reasonText }}
                  </p>

                  <div class="scheduler-chip-row">
                    <span
                      v-for="coach in message.scheduler.coaches"
                      :key="coach.role"
                      class="scheduler-chip"
                    >
                      {{ coach.icon }} {{ coach.name }}
                    </span>
                  </div>

                  <div v-if="message.isSchedulerExpanded" class="scheduler-details">
                    <div class="scheduler-detail-block">
                      <h5>本次关注重点</h5>
                      <ul>
                        <li v-for="signal in message.scheduler.signals" :key="signal">{{ formatSchedulerSignal(signal) }}</li>
                      </ul>
                    </div>

                    <div class="scheduler-detail-block">
                      <h5>协作方式</h5>
                      <div class="scheduler-batches">
                        <span
                          v-for="(batch, batchIndex) in message.scheduler.executionPlan"
                          :key="`${batch.join('-')}-${batchIndex}`"
                          class="scheduler-batch"
                        >
                          {{ formatExecutionBatch(batch, batchIndex) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 显示正常回复 -->
                <template v-if="message.content && !message.planCard">
                  <p v-if="message.role === 'user'" class="message-text user-message-text">{{ message.content }}</p>
                  <div v-else class="message-text markdown-message" v-html="renderMarkdown(message.content)"></div>
                </template>
                <p v-else-if="message.role === 'assistant' && loading" class="message-text loading">
                  <span class="loading-dots">●●●</span>
                </p>

                <div v-if="message.planCard" class="plan-card">
                  <div class="plan-card-head">
                    <div>
                      <p class="plan-tag">AI 生成计划</p>
                      <h3>{{ message.planCard.title }}</h3>
                      <!-- <p class="plan-subtitle">{{ message.planCard.subtitle }}</p> -->
                    </div>                  
                  </div>

                  <div class="plan-sections">
                    <div class="section-item">
                      <div class="section-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                      </div>
                      <div class="section-content">
                        <h5>周期安排</h5>
                        <p>1个月，分4个阶段，循序渐进</p>
                      </div>
                    </div>
                    <div class="section-item">
                      <div class="section-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <path d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                        </svg>
                      </div>
                      <div class="section-content">
                        <h5>训练结构</h5>
                        <p>每周{{ message.planCard.weeklyDays }}天，每次{{ message.planCard.duration }}分钟</p>
                      </div>
                    </div>
                    <div class="section-item">
                      <div class="section-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                          <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                      </div>
                      <div class="section-content">
                        <h5>适合人群</h5>
                        <p>{{ message.planCard.intensity }}强度，适合{{ message.planCard.subtitle.includes('减脂') ? '减脂塑形' : message.planCard.subtitle.includes('增肌') ? '增肌强化' : '健康提升' }}目标</p>
                      </div>
                    </div>
                  </div>

                  <div class="plan-actions">
                    <button type="button" class="btn btn-primary" @click="viewPlanDetails(message.planCard.planId)">
                      <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                        <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                      </svg>
                      查看详情
                    </button>
                  </div>
                </div>

                <time class="message-time">{{ formatTime(message.timestamp) }}</time>
              </div>
            </article>
          </template>
        </div>

        <div class="quick-actions">
          <button type="button" class="quick-btn" @click="quickAction('我想生成一份运动训练计划')">
            <span class="quick-icon">📋</span>
            生成计划
          </button>
          <button type="button" class="quick-btn" @click="openTrainingRecordModal()">
            <span class="quick-icon">📝</span>
            记录训练
          </button>
          <button type="button" class="quick-btn" @click="openDietRecordModal()">
            <span class="quick-icon">🍎</span>
            记录饮食
          </button>
          <button type="button" class="quick-btn" @click="openWeightRecordModal()">
            <span class="quick-icon">⚖️</span>
            记录体重
          </button>
          
        </div>

        <div class="response-mode-card">
          <label class="response-mode-toggle">
            <input v-model="enableMultiAgent" type="checkbox">
            <span class="response-mode-slider"></span>
            <span class="response-mode-copy">
              <strong>使用多智能体协作回答</strong>
              <small>回答更全面，但通常会更耗时。</small>
            </span>
          </label>
        </div>

        <footer class="input-bar">
          <textarea
            ref="inputRef"
            v-model="inputMessage"
            rows="1"
            placeholder="输入你想问AI 教练的问题.."
            @keydown.enter.prevent="handleEnter"
          />
          <button type="button" class="send-btn" :disabled="loading || !inputMessage.trim()" @click="sendMessage()">
            发送
          </button>
        </footer>
      </section>
    </div>

    <div v-if="showPlanPreviewModal" class="modal-mask" @click.self="closePlanPreviewModal">
      <div class="modal-card plan-modal">
        <button type="button" class="modal-close" @click="closePlanPreviewModal">✕</button>
        <template v-if="previewPlan">
          <div class="plan-modal-head">
            <div>
              <p class="plan-tag">AI 生成计划</p>
              <!-- <h2>{{ previewPlan.title }}</h2> -->
              <!-- <p class="modal-copy">{{ previewPlan.goal || 'AI generated training plan' }}</p> -->
            </div>
            <div class="plan-meta">
              <span>{{ previewPlan.metadata?.weekly_days || 'TBD' }}天/周</span>
              <span>{{ previewPlan.metadata?.daily_duration || 'TBD' }}分钟/次</span>
              <span>{{ previewPlan.metadata?.intensity || 'TBD' }}</span>
            </div>
          </div>

          <section class="modal-section">
            <!-- <h3>计划详情</h3> -->
            <div class="markdown-content preview-markdown" v-html="renderPlanContent(previewPlan.content)"></div>
          </section>

          <section class="modal-section">
            <h3>Select training days</h3>
            <p class="modal-copy">Choose the weekdays you want to train on for this plan.</p>
            <p class="modal-copy">You can select up to {{ getPreviewWeekdayLimit() }} training days.</p>
            <div class="weekday-grid">
              <button
                v-for="day in weekdayOptions"
                :key="day"
                type="button"
                class="weekday-chip"
                :class="{ active: previewWeekdays.includes(day) }"
                :disabled="isPreviewWeekdayDisabled(day)"
                @click="togglePreviewWeekday(day)"
              >
                {{ day }}
              </button>
            </div>
          </section>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closePlanPreviewModal">Cancel</button>
            <button
              type="button"
              class="btn btn-primary"
              :disabled="!previewWeekdays.length || planPreviewLoading"
              @click="savePreviewWeekdays"
            >
              Save
            </button>
          </div>
        </template>
      </div>
    </div>

    <div v-if="showQuestionnaireModal" class="modal-mask" @click.self="closeQuestionnaireModal">
      <div class="modal-card questionnaire-modal">
        <button type="button" class="modal-close" @click="closeQuestionnaireModal">✕</button>
        
        <div class="questionnaire-header-modal">
          <div>
            <p class="coach-tag">AI 教练</p>
            <h2>{{ currentQuestionnaireQuestion.title }}</h2>
            <p class="modal-copy">{{ currentQuestionnaireQuestion.subtitle }}</p>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${((questionnaireStepIndex + 1) / questionnaireQuestions.length) * 100}%` }"></div>
          </div>
        </div>

        <div class="questionnaire-content">
          <div class="options-grid">
            <button
              v-for="option in currentQuestionnaireQuestion.options"
              :key="option.value"
              class="option-card"
              :class="{ selected: currentQuestionnaireQuestion.answer === option.value }"
              @click="selectQuestionnaireOption(option.value)"
            >
              <span>{{ option.label }}</span>
            </button>
          </div>

          <div v-if="currentQuestionnaireQuestion.key === 'injury' && currentQuestionnaireQuestion.answer === 'other'" class="form-field">
            <label for="injury-detail-modal">请输入具体伤病情况</label>
            <textarea
              id="injury-detail-modal"
              v-model.trim="questionnaireData.injury_detail"
              rows="3"
              placeholder="例如：膝盖疼痛、腰部不适、肩部活动受限"
            />
          </div>
        </div>

        <div class="modal-actions">
          <button 
            type="button" 
            class="btn btn-secondary" 
            :disabled="questionnaireStepIndex === 0 || loading" 
            @click="prevQuestionnaireStep"
          >
            上一步
          </button>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="!questionnaireCanProceed || loading"
            @click="nextQuestionnaireStep"
          >
            {{ questionnaireStepIndex === questionnaireQuestions.length - 1 ? (loading ? '正在生成...' : '生成计划') : '下一步' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="showTrainingRecordModal" class="modal-mask" @click.self="closeTrainingRecordModal">
      <div class="modal-card plan-modal record-modal">
        <button type="button" class="modal-close" @click="closeTrainingRecordModal">✕</button>

        <div class="record-modal-head">
          <div>
            <p class="coach-tag">训练记录</p>
            <h2>记录今天的训练表现</h2>
            <p class="modal-copy">填写训练类型、时长和身体反馈，方便后续分析训练节奏与恢复状态。</p>
          </div>
        </div>

        <form @submit.prevent="submitTrainingRecord">
          <section class="modal-section">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="training-type">训练类型</label>
                <select id="training-type" v-model="trainingRecordData.training_type" class="form-input">
                  <option value="">请选择</option>
                  <option value="力量训练">力量训练</option>
                  <option value="有氧训练">有氧训练</option>
                  <option value="跑步">跑步</option>
                  <option value="HIIT">HIIT</option>
                  <option value="瑜伽拉伸">瑜伽拉伸</option>
                  <option value="球类运动">球类运动</option>
                  <option value="其他">其他</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label" for="training-duration">训练时长</label>
                <input
                  id="training-duration"
                  v-model.number="trainingRecordData.duration"
                  class="form-input"
                  type="number"
                  min="1"
                  max="600"
                  placeholder="分钟"
                >
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="training-intensity">训练强度</label>
              <select id="training-intensity" v-model="trainingRecordData.intensity" class="form-input">
                <option value="">请选择</option>
                <option value="低">低</option>
                <option value="中">中</option>
                <option value="高">高</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">疲劳程度</label>
              <div class="range-selector">
                <button
                  v-for="level in [1, 2, 3, 4, 5]"
                  :key="`fatigue-${level}`"
                  type="button"
                  class="fatigue-option"
                  :class="{ selected: trainingRecordData.fatigue_level === level }"
                  @click="trainingRecordData.fatigue_level = level"
                >
                  {{ level }}
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">疼痛程度</label>
              <div class="range-selector">
                <button
                  v-for="level in [0, 1, 2, 3, 4, 5]"
                  :key="`pain-${level}`"
                  type="button"
                  class="pain-option"
                  :class="{ selected: trainingRecordData.pain_level === level }"
                  @click="trainingRecordData.pain_level = level"
                >
                  {{ level }}
                </button>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="training-notes">备注</label>
              <textarea
                id="training-notes"
                v-model.trim="trainingRecordData.notes"
                class="form-textarea"
                rows="4"
                placeholder="例如：今天状态不错，下肢发力感明显，右膝有轻微不适"
              />
            </div>
          </section>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeTrainingRecordModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="savingTrainingRecord">
              {{ savingTrainingRecord ? '保存中...' : '保存训练记录' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showDietRecordModal" class="modal-mask" @click.self="closeDietRecordModal">
      <div class="modal-card plan-modal record-modal">
        <button type="button" class="modal-close" @click="closeDietRecordModal">✕</button>

        <div class="record-modal-head">
          <div>
            <p class="coach-tag">饮食记录</p>
            <h2>记录今天吃了什么</h2>
            <p class="modal-copy">记录餐别、食物和大致营养信息，后续更容易结合训练安排做饮食建议。</p>
          </div>
        </div>

        <form @submit.prevent="submitDietRecord">
          <section class="modal-section">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="meal-type">餐别</label>
                <select id="meal-type" v-model="dietRecordData.meal_type" class="form-input">
                  <option value="">请选择</option>
                  <option value="早餐">早餐</option>
                  <option value="午餐">午餐</option>
                  <option value="晚餐">晚餐</option>
                  <option value="加餐">加餐</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label" for="diet-calories">热量</label>
                <input
                  id="diet-calories"
                  v-model.number="dietRecordData.calories"
                  class="form-input"
                  type="number"
                  min="0"
                  placeholder="kcal"
                >
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="food-content">食物内容</label>
              <textarea
                id="food-content"
                v-model.trim="dietRecordData.food_content"
                class="form-textarea"
                rows="4"
                placeholder="例如：鸡胸肉沙拉、米饭半碗、无糖酸奶"
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="diet-protein">蛋白质</label>
              <input
                id="diet-protein"
                v-model.number="dietRecordData.protein"
                class="form-input"
                type="number"
                min="0"
                step="0.1"
                placeholder="克"
              >
            </div>

            <div class="form-group">
              <label class="form-label" for="diet-notes">备注</label>
              <textarea
                id="diet-notes"
                v-model.trim="dietRecordData.notes"
                class="form-textarea"
                rows="3"
                placeholder="例如：训练后 30 分钟内进食，今天饮水偏少"
              />
            </div>
          </section>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeDietRecordModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="savingDietRecord">
              {{ savingDietRecord ? '保存中...' : '保存饮食记录' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showWeightRecordModal" class="modal-mask" @click.self="closeWeightRecordModal">
      <div class="modal-card plan-modal record-modal">
        <button type="button" class="modal-close" @click="closeWeightRecordModal">✕</button>

        <div class="record-modal-head">
          <div>
            <p class="coach-tag">体重记录</p>
            <h2>记录体重与围度变化</h2>
            <p class="modal-copy">把体重、体脂和围度记下来，后面更容易判断减脂、增肌或维持阶段的趋势。</p>
          </div>
        </div>

        <form @submit.prevent="submitWeightRecord">
          <section class="modal-section">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label" for="weight-value">体重</label>
                <input
                  id="weight-value"
                  v-model.number="weightRecordData.weight"
                  class="form-input weight-input"
                  type="number"
                  min="0"
                  step="0.1"
                  placeholder="kg"
                >
              </div>

              <div class="form-group">
                <label class="form-label" for="body-fat-value">体脂率</label>
                <input
                  id="body-fat-value"
                  v-model.number="weightRecordData.body_fat"
                  class="form-input"
                  type="number"
                  min="0"
                  max="100"
                  step="0.1"
                  placeholder="%"
                >
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">围度信息</label>
              <div class="measure-inputs">
                <div>
                  <label for="chest-circumference">胸围</label>
                  <input
                    id="chest-circumference"
                    v-model.number="weightRecordData.chest_circumference"
                    class="form-input"
                    type="number"
                    min="0"
                    step="0.1"
                    placeholder="cm"
                  >
                </div>

                <div>
                  <label for="waist-circumference">腰围</label>
                  <input
                    id="waist-circumference"
                    v-model.number="weightRecordData.waist_circumference"
                    class="form-input"
                    type="number"
                    min="0"
                    step="0.1"
                    placeholder="cm"
                  >
                </div>

                <div>
                  <label for="hip-circumference">臀围</label>
                  <input
                    id="hip-circumference"
                    v-model.number="weightRecordData.hip_circumference"
                    class="form-input"
                    type="number"
                    min="0"
                    step="0.1"
                    placeholder="cm"
                  >
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label" for="weight-notes">备注</label>
              <textarea
                id="weight-notes"
                v-model.trim="weightRecordData.notes"
                class="form-textarea"
                rows="3"
                placeholder="例如：晨起空腹测量，昨晚睡眠一般"
              />
            </div>
          </section>

          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="closeWeightRecordModal">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="savingWeightRecord">
              {{ savingWeightRecord ? '保存中...' : '保存体重记录' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import api from '../api'

const router = useRouter()
const route = useRoute()

const CHAT_HISTORY_STORAGE_KEY = 'sports-training-chat-history'
const ACTIVE_PLAN_KEY = 'sports-training-active-plan-id'
const PENDING_PROMPT_KEY = 'pendingTrainingPrompt'
const MULTI_AGENT_MODE_KEY = 'sports-training-use-multi-agent'

// 获取当前用户的聊天历史存储 key
const getUserChatHistoryKey = () => {
  const userInfo = JSON.parse(localStorage.getItem('user') || 'null')
  const userId = userInfo?.id || 'anonymous'
  return `${CHAT_HISTORY_STORAGE_KEY}-${userId}`
}

// 获取用户的 active plan 存储 key
const getUserActivePlanKey = () => {
  const userInfo = JSON.parse(localStorage.getItem('user') || 'null')
  const userId = userInfo?.id || 'anonymous'
  return `${ACTIVE_PLAN_KEY}-${userId}`
}

// 获取用户的多智能体模式存储 key
const getUserMultiAgentModeKey = () => {
  const userInfo = JSON.parse(localStorage.getItem('user') || 'null')
  const userId = userInfo?.id || 'anonymous'
  return `${MULTI_AGENT_MODE_KEY}-${userId}`
}

const suggestions = [
  '我想生成一份运动训练计划',
  '帮我安排今天的训练内容',
  '我最近恢复不太好，怎么办？',
  '帮我分析一下训练节奏'
]

const weekdayOptions = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

const messages = ref([])
const chatHistory = ref([])
const currentChat = ref(null)
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const inputRef = ref(null)
const pendingPlanContext = ref(null)
const enableMultiAgent = ref(true)

const showPlanPreviewModal = ref(false)
const previewPlan = ref(null)
const previewWeekdays = ref([])
const planPreviewLoading = ref(false)

const showQuestionnaireModal = ref(false)
const questionnaireStepIndex = ref(0)
const questionnaireData = ref({
  goal: '',
  method: '',
  weekly_days: '',
  daily_duration: '',
  intensity: '',
  injury: '',
  injury_detail: ''
})

// 记录模态框相关状态
const showTrainingRecordModal = ref(false)
const showDietRecordModal = ref(false)
const showWeightRecordModal = ref(false)
const savingTrainingRecord = ref(false)
const savingDietRecord = ref(false)
const savingWeightRecord = ref(false)

// 训练记录表单数据
const trainingRecordData = ref({
  training_type: '',
  duration: 30,
  intensity: '',
  fatigue_level: 3,
  pain_level: 0,
  notes: ''
})

// 饮食记录表单数据
const dietRecordData = ref({
  meal_type: '',
  food_content: '',
  calories: '',
  protein: '',
  notes: ''
})

// 体重记录表单数据
const weightRecordData = ref({
  weight: '',
  body_fat: '',
  chest_circumference: '',
  waist_circumference: '',
  hip_circumference: '',
  notes: ''
})

const questionnaireQuestions = [
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

const shorten = (text = '') => (text.length > 22 ? `${text.slice(0, 22)}...` : text)

const formatTime = (value) => {
  if (!value) return ''
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getToday = () => new Date().toISOString().split('T')[0]

const addDays = (dateString, days) => {
  const date = new Date(dateString)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

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
    .replace(/\*\*|__/g, '')               // 移除孤立的粗体标记
    .replace(/(^|\s)[*_](\s|$)/g, '$1$2')   // 移除前后有空格的单个*或_
    .replace(/\n{3,}/g, '\n\n')           // 多个换行符减少为两个
    .replace(/\s{2,}/g, ' ')              // 多个空格合并为一个
    .replace(/^\s+|\s+$/g, '')            // 去除首尾空格
    .trim()

  return cleaned
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

const renderMarkdown = (content = '') => {
  const lines = String(content || '').replace(/\r\n/g, '\n').split('\n')
  const html = []
  let inList = false
  let inParagraph = false

  const closeList = () => {
    if (inList) {
      html.push('</ul>')
      inList = false
    }
  }

  const closeParagraph = () => {
    if (inParagraph) {
      html.push('</p>')
      inParagraph = false
    }
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()

    if (!line) {
      closeList()
      closeParagraph()
      continue
    }

    const headingMatch = line.match(/^(#{1,4})\s+(.+)$/)
    if (headingMatch) {
      closeList()
      closeParagraph()
      const level = Math.min(4, headingMatch[1].length)
      html.push(`<h${level}>${formatInlineMarkdown(headingMatch[2].trim())}</h${level}>`)
      continue
    }

    if (/^([-*_])\1{2,}$/.test(line)) {
      closeList()
      closeParagraph()
      html.push('<hr class="md-divider">')
      continue
    }

    if (/^[-*]\s+/.test(line)) {
      closeParagraph()
      if (!inList) {
        html.push('<ul>')
        inList = true
      }
      html.push(`<li>${formatInlineMarkdown(line.replace(/^[-*]\s+/, ''))}</li>`)
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

  closeList()
  closeParagraph()

  return html.join('')
}

const levelAwareIsTrainingDayHeading = (text = '') =>
  /^训练日\s*[一二三四五六七1234567890]+$/i.test(String(text || '').trim())

const renderPlanContent = (content = '') => {
  const lines = String(content || '').replace(/\r\n/g, '\n').split('\n')
  const html = []
  let inList = false
  let inOrderedList = false
  let inParagraph = false
  let inBlockquote = false
  let inTable = false
  let tableHeaderParsed = false
  let inTrainingDayCard = false

  const closeList = () => {
    if (inList) { html.push('</ul>'); inList = false }
    if (inOrderedList) { html.push('</ol>'); inOrderedList = false }
  }
  const closeParagraph = () => { if (inParagraph) { html.push('</p>'); inParagraph = false } }
  const closeBlockquote = () => { if (inBlockquote) { closeParagraph(); html.push('</blockquote>'); inBlockquote = false } }
  const closeTable = () => { if (inTable) { html.push('</tbody></table>'); inTable = false; tableHeaderParsed = false } }
  const closeTrainingDayCard = () => {
    if (inTrainingDayCard) { closeTable(); closeBlockquote(); closeList(); closeParagraph(); html.push('</section>'); inTrainingDayCard = false }
  }

  const parseTableCells = (v = '') => v.split('|').map(c => c.trim()).filter(Boolean)
  const appendTableRow = (cells = [], tag = 'td') => {
    html.push('<tr>')
    cells.forEach(c => html.push(`<${tag}>${formatInlineMarkdown(c)}</${tag}>`))
    html.push('</tr>')
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()

    if (!line) { closeTrainingDayCard(); closeTable(); closeBlockquote(); closeList(); closeParagraph(); continue }

    const tableCells = parseTableCells(line)
    const isTableSeparator = /^[\s|:-]+$/.test(line)
    if ((line.includes('|') && tableCells.length >= 2) || (inTable && isTableSeparator)) {
      closeBlockquote(); closeList(); closeParagraph()
      if (!inTable && !isTableSeparator) {
        html.push('<table class="md-table"><thead>'); appendTableRow(tableCells, 'th'); html.push('</thead><tbody>')
        inTable = true; tableHeaderParsed = true; continue
      }
      if (inTable && isTableSeparator) continue
      if (inTable && tableHeaderParsed) { appendTableRow(tableCells, 'td'); continue }
    } else { closeTable() }

    const headingMatch = line.match(/^(#{1,4})\s+(.+)$/)
    if (headingMatch) {
      const headingText = headingMatch[2].trim()
      if (levelAwareIsTrainingDayHeading(headingText)) {
        closeTrainingDayCard(); closeBlockquote(); closeList(); closeParagraph()
        html.push('<section class="training-day-card">'); inTrainingDayCard = true
        const level = Math.min(4, headingMatch[1].length)
        html.push(`<h${level}>${formatInlineMarkdown(headingText)}</h${level}>`); continue
      }
      closeTrainingDayCard(); closeBlockquote(); closeList(); closeParagraph()
      const level = Math.min(4, headingMatch[1].length)
      html.push(`<h${level}>${formatInlineMarkdown(headingText)}</h${level}>`); continue
    }

    if (/^([-*_])\1{2,}$/.test(line)) {
      closeTrainingDayCard(); closeBlockquote(); closeList(); closeParagraph()
      html.push('<hr class="md-divider">'); continue
    }

    if (/^计划标题[:：]/.test(line)) {
      closeTrainingDayCard(); closeBlockquote(); closeList(); closeParagraph()
      html.push(`<h1>${formatInlineMarkdown(line.replace(/^计划标题[:：]\s*/, ''))}</h1>`); continue
    }

    if (/^计划概述[:：]/.test(line)) {
      closeTrainingDayCard(); closeBlockquote(); closeList(); closeParagraph()
      html.push(`<h2>计划概述</h2><p>${formatInlineMarkdown(line.replace(/^计划概述[:：]\s*/, ''))}</p>`); continue
    }

    if (/^>\s?/.test(line)) {
      closeList()
      if (!inBlockquote) { closeParagraph(); html.push('<blockquote>'); inBlockquote = true }
      if (!inParagraph) { html.push('<p>'); inParagraph = true } else { html.push('<br>') }
      html.push(formatInlineMarkdown(line.replace(/^>\s?/, ''))); continue
    }

    if (/^[-*]\s+/.test(line)) {
      closeBlockquote(); closeParagraph()
      if (!inList) { if (inOrderedList) { html.push('</ol>'); inOrderedList = false }; html.push('<ul>'); inList = true }
      html.push(`<li>${formatInlineMarkdown(line.replace(/^[-*]\s+/, ''))}</li>`); continue
    }

    if (/^\d+\.\s+/.test(line)) {
      closeBlockquote(); closeParagraph()
      if (!inOrderedList) { if (inList) { html.push('</ul>'); inList = false }; html.push('<ol>'); inOrderedList = true }
      html.push(`<li>${formatInlineMarkdown(line.replace(/^\d+\.\s+/, ''))}</li>`); continue
    }

    if (!inParagraph) { closeList(); html.push('<p>'); inParagraph = true } else { html.push('<br>') }
    html.push(formatInlineMarkdown(line))
  }

  closeTrainingDayCard(); closeTable(); closeBlockquote(); closeList(); closeParagraph()
  return html.join('')
}

const normalizeMessage = (message = {}) => ({
  role: message.role || 'assistant',
  content: message.content || '',
  thinking: removeMarkdownFormat(message.thinking || ''), // 清理思考过程（总是AI生成）
  isThinkingExpanded: message.isThinkingExpanded !== undefined ? message.isThinkingExpanded : false, // 思考过程是否展开
  progressLogs: Array.isArray(message.progressLogs) ? message.progressLogs : [],
  scheduler: message.scheduler || null,
  isSchedulerExpanded: message.isSchedulerExpanded !== undefined ? message.isSchedulerExpanded : true,
  timestamp: message.timestamp ? new Date(message.timestamp) : new Date(),
  planCard: message.planCard || null,
  planQuestionnaire: Boolean(message.planQuestionnaire)
})

const isPlanLikeAssistantMessage = (message = {}) => {
  if (message.role !== 'assistant') return false
  const content = String(message.content || '')
  return Boolean(
    message.planCard ||
    isTrainingPlanContent(content) ||
    /(^|\n)##\s*第\d+周/.test(content) ||
    /(^|\n)###\s*训练日\d+/.test(content)
  )
}

const sanitizeConversation = (conversation = [], fallbackQuestion = '', fallbackAnswer = '', fallbackTimestamp = null) => {
  const normalizedConversation = (Array.isArray(conversation) ? conversation : [])
    .map((message) => normalizeMessage(message))

  let sanitized = [...normalizedConversation]

  if (!sanitized.some((message) => message.role === 'user') && fallbackQuestion) {
    sanitized.unshift(
      normalizeMessage({
        role: 'user',
        content: fallbackQuestion,
        timestamp: fallbackTimestamp
      })
    )
  }

  sanitized = sanitized.filter((message, index, list) => {
    if (message.role !== 'assistant' || message.planCard || !isPlanLikeAssistantMessage(message)) {
      return true
    }

    for (let nextIndex = index + 1; nextIndex < list.length; nextIndex += 1) {
      const nextMessage = list[nextIndex]
      if (nextMessage.role === 'user') break
      if (nextMessage.role === 'assistant' && nextMessage.planCard) {
        return false
      }
    }

    return true
  })

  if (!sanitized.some((message) => message.role === 'assistant') && fallbackAnswer) {
    sanitized.push(
      normalizeMessage({
        role: 'assistant',
        content: fallbackAnswer,
        timestamp: fallbackTimestamp
      })
    )
  }

  return sanitized
}

const normalizeChatHistory = (history = []) =>
  history.map((item) => {
    // 确保conversation字段存在
    let conversation = []
    
    if (Array.isArray(item.conversation)) {
      conversation = sanitizeConversation(item.conversation, item.question, item.answer, item.timestamp)
    } else if (item.question && item.answer) {
      // 如果没有conversation但有question和answer，自动从中构造对话
      conversation = sanitizeConversation(
        [
          {
            role: 'user',
            content: item.question,
            timestamp: item.timestamp
          },
          {
            role: 'assistant',
            content: item.answer,
            thinking: item.thinking || '',
            timestamp: item.timestamp
          }
        ],
        item.question,
        item.answer,
        item.timestamp
      )
    }
    
    return {
      ...item,
      timestamp: item.timestamp ? new Date(item.timestamp) : new Date(),
      conversation
    }
  })

const saveChatHistoryToLocal = () => {
  try {
    const sanitizedHistory = chatHistory.value.map((item) => ({
      ...item,
      conversation: sanitizeConversation(item.conversation, item.question, item.answer, item.timestamp)
    }))
    localStorage.setItem(getUserChatHistoryKey(), JSON.stringify(sanitizedHistory))
  } catch (error) {
    console.error('保存聊天记录失败:', error)
  }
}

const loadChatHistoryFromLocal = () => {
  try {
    const raw = localStorage.getItem(getUserChatHistoryKey())
    if (!raw) return []
    return normalizeChatHistory(JSON.parse(raw))
  } catch (error) {
    console.error('读取本地聊天记录失败:', error)
    return []
  }
}

// 清除当前用户的聊天历史
const clearChatHistoryLocal = () => {
  try {
    localStorage.removeItem(getUserChatHistoryKey())
  } catch (error) {
    console.error('清除聊天记录失败:', error)
  }
}

const getDisplayPlanTitle = (title = '') =>
  String(title || '')
    .replace(/^#+\s*/, '')
    .replace(/^计划标题[:：]\s*/i, '')
    .trim()

const normalizeTrainingDayHeading = (text = '') =>
  String(text || '')
    .replace(/（\s*周[一二三四五六日天]\s*）/g, '')
    .replace(/\(\s*周[一二三四五六日天]\s*\)/g, '')
    .replace(/（\s*星期[一二三四五六日天]\s*）/g, '')
    .replace(/\(\s*星期[一二三四五六日天]\s*\)/g, '')
    .replace(/\s*[-—–]\s*周[一二三四五六日天]\s*$/g, '')
    .replace(/\s*[-—–]\s*星期[一二三四五六日天]\s*$/g, '')
    .trim()

const extractPlanTitleFromContent = (content = '', fallback = 'AI Training Plan') => {
  const text = String(content || '').replace(/\r\n/g, '\n')
  const lines = text.split('\n').map((line) => line.trim()).filter(Boolean)

  const explicitTitleLine = lines.find((line) =>
    /^#\s+/.test(line) ||
    /^计划标题[:：]/.test(line) ||
    /^#\s*计划标题[:：]?/i.test(line)
  )

  if (explicitTitleLine) {
    const cleaned = getDisplayPlanTitle(explicitTitleLine.replace(/^#\s*/, ''))
    if (cleaned) return cleaned
  }

  return getDisplayPlanTitle(fallback) || 'AI Training Plan'
}

const schedulerSignalLabels = {
  planning: '更需要先明确训练目标、周期安排和整体节奏',
  technique: '需要补充动作细节、发力方式和执行要点',
  recovery: '需要兼顾身体恢复、伤痛规避和训练调整'
}

const formatSchedulerSignal = (signal = '') =>
  schedulerSignalLabels[signal] || '系统补充了与你问题相关的专项建议'

const getCoachDisplayName = (agentId = '') => {
  if (agentId === 'planning') return '训练规划教练'
  if (agentId === 'technique') return '技术指导教练'
  if (agentId === 'recovery') return '运动康复教练'
  return agentId
}

const getSchedulerHeadline = (coachCount = 0) =>
  coachCount > 1 ? `${coachCount} 位教练一起为你整理了这份建议` : 'AI 教练为你整理了这份建议'

const formatExecutionBatch = (batch = [], batchIndex = 0) => {
  const coachNames = batch.map((agentId) => {
    if (agentId === 'planning') return '训练规划教练'
    if (agentId === 'technique') return '技术指导教练'
    if (agentId === 'recovery') return '运动康复教练'
    return agentId
  }).join('、')

  if (batchIndex === 0) return `先由 ${coachNames} 给出基础判断`
  return `再由 ${coachNames} 补充细节与调整建议`
}

const buildSchedulerViewModel = (scheduler = {}, coaches = []) => {
  const signals = Array.isArray(scheduler?.signals) ? scheduler.signals : []
  const executionPlan = Array.isArray(scheduler?.execution_plan) ? scheduler.execution_plan : []
  const safeCoaches = Array.isArray(coaches) ? coaches : []
  const reasonText = signals.length
    ? '为了让建议更完整、也更贴合你的情况，这次由不同方向的教练一起参与了分析。'
    : ''

  return {
    signals,
    executionPlan,
    coaches: safeCoaches.map((coach) => ({
      name: coach.name || getCoachDisplayName(coach.role) || '教练',
      icon: coach.icon || '🤖',
      role: coach.role || coach.name || 'coach'
    })),
    reasonText
  }
}

const buildVisibleThinking = (thinking = '', progressLogs = []) => {
  const cleanedThinking = removeMarkdownFormat(thinking || '').trim()
  if (cleanedThinking) return cleanedThinking

  const normalizedLogs = Array.isArray(progressLogs)
    ? progressLogs.map((item) => String(item || '').trim()).filter(Boolean)
    : []

  if (!normalizedLogs.length) return ''

  return normalizedLogs.map((item) => `- ${item}`).join('\n')
}

const stripSchedulerSection = (content = '') => {
  const text = String(content || '')
  return text.replace(
    /^##\s+🧠\s*调度说明[\s\S]*?(?=\n##\s|$)/,
    ''
  ).trim()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const newChat = () => {
  messages.value = []
  currentChat.value = null
}

const deleteChatHistory = (index) => {
  if (!window.confirm('确定删除这条对话记录吗？')) return

  chatHistory.value.splice(index, 1)

  if (currentChat.value === index) {
    messages.value = []
    currentChat.value = null
    return
  }

  if (currentChat.value !== null && currentChat.value > index) {
    currentChat.value -= 1
  }
}

const loadChatHistory = (index) => {
  currentChat.value = index
  const chat = chatHistory.value[index]
  messages.value = sanitizeConversation(chat?.conversation || [], chat?.question, chat?.answer, chat?.timestamp)
  scrollToBottom()
}

const buildPlanTitle = (planContext = null) => {
  const goal = planContext?.questionnaire?.goal || 'AI Training Plan'
  return `${goal}`
}

const buildPlanPayloadFromMessage = (message, planContext = null) => {
  const questionnaire = planContext?.questionnaire || {}
  const content = message?.content || ''
  const startDate = getToday()

  return {
    title: extractPlanTitleFromContent(content, buildPlanTitle(planContext)),
    content,
    created_from_ai: true,
    goal: questionnaire.goal || 'AI 教练推荐',
    start_date: startDate,
    end_date: addDays(startDate, 29),
    metadata: questionnaire,
    source_prompt: planContext?.prompt || '',
    ai_response: content,
    selected_weekdays: []
  }
}

const createPlanCardMessage = (savedPlan, planContext = null) => {
  const questionnaire = planContext?.questionnaire || savedPlan?.metadata || {}
  const content = savedPlan?.content || ''

  // 提取结构化的计划摘要
  const extractStructuredSummary = (text) => {
    if (!text) return '计划内容待生成。'

    // 清理Markdown格式
    const cleaned = removeMarkdownFormat(text)
    const lines = cleaned.split('\n').map(line => line.trim()).filter(line => line.length > 0)

    // 查找阶段标题（包含"第X周"、"阶段"等关键词）
    const phaseLines = lines.filter(line =>
      line.includes('第') && line.includes('周') ||
      line.includes('阶段') ||
      /^(第一周|第二周|第三周|第四周)/.test(line)
    )

    // 查找训练日内容（包含"训练日"、"Day"、"训练主题"等）
    const trainingDayLines = lines.filter(line =>
      line.includes('训练日') ||
      line.includes('训练主题') ||
      line.includes('训练时长') ||
      line.includes('训练内容')
    )

    // 构建结构化摘要
    let summary = ''

    if (phaseLines.length > 0) {
      // 添加阶段概述
      summary += `计划包含 ${phaseLines.length} 个训练阶段：\n`
      phaseLines.slice(0, 3).forEach((phase) => {
        summary += `• ${phase}\n`
      })
      if (phaseLines.length > 3) {
        summary += `• ... 等 ${phaseLines.length} 个阶段\n`
      }
    }

    if (trainingDayLines.length > 0) {
      summary += `\n包含 ${Math.min(trainingDayLines.length, 5)} 个训练日安排，涵盖：\n`
      // 提取训练主题关键词
      const themes = trainingDayLines.slice(0, 3).map(line => {
        // 尝试提取主题
        if (line.includes('训练主题')) {
          const match = line.match(/训练主题[:：]\s*(.+)/)
          return match ? match[1].slice(0, 20) : line.slice(0, 30)
        }
        return line.slice(0, 30)
      })
      themes.forEach(theme => {
        summary += `• ${theme}${theme.length >= 30 ? '...' : ''}\n`
      })
    }

    // 如果未提取到结构，使用前3行作为摘要
    if (!summary && lines.length > 0) {
      summary = lines.slice(0, 3).join('\n')
      if (summary.length > 120) {
        summary = summary.slice(0, 120) + '...'
      }
    }

    // 如果仍然为空，使用默认摘要
    if (!summary) {
      summary = '已为您生成个性化的训练计划，包含详细的阶段划分和每日训练安排。'
    }

    return summary.trim()
  }

  const summary = extractStructuredSummary(content)

  return normalizeMessage({
    role: 'assistant',
    content: '',
    timestamp: new Date(),
    planCard: {
      planId: savedPlan.id,
      title: getDisplayPlanTitle(savedPlan.title || ''),
      subtitle: removeMarkdownFormat(questionnaire.goal || 'AI generated plan'),
      weeklyDays: questionnaire.weekly_days || 'TBD',
      duration: questionnaire.daily_duration || 'TBD',
      intensity: questionnaire.intensity || 'TBD',
      summary: summary
    }
  })
}

const createPlanFromAiResponse = async (message, planContext = null) => {
  const response = await api.post('/training/plans', buildPlanPayloadFromMessage(message, planContext))
  if (!response?.plan?.id) {
    throw new Error('训练计划生成失败')
  }
  return response.plan
}

const extractAnswer = (response) => response?.answer || response?.content || response?.response || '我已经收到你的问题，但暂时没有生成有效回复。'

const isErrorLikeResponse = (content = '') => {
  const text = String(content || '').trim()
  if (!text) return true

  const errorMarkers = [
    '网络连接出现问题',
    '请求处理超时',
    '处理您的请求时出现错误',
    '消息发送失败',
    'ssl连接错误',
    '系统错误',
    '请稍后重试',
    '技术信息：'
  ]

  return errorMarkers.some((marker) => text.includes(marker))
}

// 检测内容是否为训练计划
const isTrainingPlanContent = (content = '') => {
  const cleanedText = removeMarkdownFormat(String(content)).toLowerCase()
  const trainingPlanKeywords = [
    '训练计划', '训练日', '每周', '第一周', '第二周', '第三周', '第四周',
    '训练内容', '训练目标', '恢复建议', '训练时长', '训练强度'
  ]
  return trainingPlanKeywords.some(keyword => cleanedText.includes(keyword.toLowerCase()))
}

const shouldCreateTrainingPlan = (content = '', planContext = null) => {
  if (isErrorLikeResponse(content)) return false
  if (planContext) return true
  return isTrainingPlanContent(content)
}

// 从训练计划内容中提取简要总结
const extractTrainingSummary = (content = '') => {
  const cleanedText = removeMarkdownFormat(String(content)).trim()
  if (!cleanedText) return '已为您生成训练计划。'

  // 尝试提取第一句（到第一个句号、感叹号或问号为止）
  const firstSentenceMatch = cleanedText.match(/^[^。！？]+[。！？]/)
  if (firstSentenceMatch) {
    const firstSentence = firstSentenceMatch[0]
    // 如果第一句包含训练计划关键词，直接返回
    if (firstSentence.includes('训练计划') || firstSentence.includes('训练安排')) {
      return firstSentence
    }
    // 如果第一句太长（超过50字符），截断
    if (firstSentence.length > 50) {
      return firstSentence.slice(0, 50) + '...'
    }
    return firstSentence
  }

  // 如果没有找到完整的句子，检查是否包含训练计划相关内容
  if (cleanedText.includes('训练计划') || cleanedText.includes('训练安排') || isTrainingPlanContent(cleanedText)) {
    // 返回简短的默认消息
    return '已为您生成个性化的训练计划，请查看下方的训练计划卡片获取详细信息。'
  }

  // 否则取前80个字符作为简要总结
  return cleanedText.length > 80 ? cleanedText.slice(0, 80) + '...' : cleanedText
}

const updateCurrentConversation = (question, assistantMessage) => {
  if (currentChat.value !== null && chatHistory.value[currentChat.value]) {
    const target = chatHistory.value[currentChat.value]
    target.conversation = sanitizeConversation(
      [
        ...(target.conversation || []),
        normalizeMessage({ role: 'user', content: question, timestamp: new Date() }),
        assistantMessage
      ],
      question,
      assistantMessage.content,
      new Date()
    )
    target.question = question
    target.answer = assistantMessage.content
    target.timestamp = new Date()
    return
  }

  chatHistory.value.unshift({
    question,
    answer: assistantMessage.content,
    timestamp: new Date(),
    conversation: sanitizeConversation(
      [
        normalizeMessage({ role: 'user', content: question, timestamp: new Date() }),
        assistantMessage
      ],
      question,
      assistantMessage.content,
      new Date()
    )
  })
  currentChat.value = 0
}

const replacePlanConversationMessage = (conversation = [], message, updatedMessage, fallbackQuestion = '') => {
  const nextConversation = [...(conversation || [])]
  let idx = nextConversation.findIndex((item) => item.timestamp?.getTime?.() === message.timestamp?.getTime?.())

  if (idx < 0) {
    for (let i = nextConversation.length - 1; i >= 0; i -= 1) {
      if (nextConversation[i].role === 'assistant' && isPlanLikeAssistantMessage(nextConversation[i])) {
        idx = i
        break
      }
    }
  }

  if (idx < 0) {
    nextConversation.push(updatedMessage)
  } else {
    nextConversation.splice(idx, 1, updatedMessage)
  }

  return sanitizeConversation(nextConversation, fallbackQuestion, updatedMessage.content, updatedMessage.timestamp)
}

const buildUserProfileForQuery = (question, planContext = null) => {
  const questionnaire = planContext?.questionnaire || {}
  const injury =
    questionnaire.injury === 'other'
      ? questionnaire.injury_detail
      : questionnaire.injury

  return {
    source: planContext ? 'training_questionnaire' : 'chat',
    question,
    goal: questionnaire.goal || '',
    preferred_method: questionnaire.method || '',
    weekly_days: questionnaire.weekly_days || '',
    daily_duration: questionnaire.daily_duration || '',
    intensity: questionnaire.intensity || '',
    injury_status: injury || ''
  }
}

const shouldUseMultiAgentQuery = (question, planContext = null) => {
  if (!enableMultiAgent.value) return false
  if (planContext?.questionnaire) return true

  const normalizedQuestion = String(question || '').toLowerCase()
  const multiAgentKeywords = [
    '计划',
    '规划',
    '安排',
    '训练日',
    '动作',
    '姿势',
    '技术',
    '疲劳',
    '恢复',
    '康复',
    '伤',
    '痛',
    '风险',
    '安全',
    '评估'
  ]

  return multiAgentKeywords.some((keyword) => normalizedQuestion.includes(keyword))
}

const sendMessage = async (text = null, options = {}) => {
  const question = text || inputMessage.value.trim()
  const planContext = options.planContext || pendingPlanContext.value
  const useMultiAgent = shouldUseMultiAgentQuery(question, planContext)
  const userProfile = buildUserProfileForQuery(question, planContext)
  if (!question || loading.value) return

  messages.value.push(normalizeMessage({ role: 'user', content: question, timestamp: new Date() }))
  inputMessage.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    // 添加助手消息占位符
    const assistantMessageIndex = messages.value.length
    messages.value.push(normalizeMessage({
      role: 'assistant',
      content: '',
      thinking: '',
      timestamp: new Date()
    }))
    
    // 流式接收思考过程和答案
    let thinkingContent = ''
    let answerContent = ''
    let schedulerInfo = null
    let progressLogs = []

    await api.queryStream(
      question,
      (chunk, type, data) => {
        if (type === 'thinking') {
          // 如果是第一次收到思考内容，自动展开思考过程
          if (thinkingContent === '') {
            messages.value[assistantMessageIndex].isThinkingExpanded = true
          }
          thinkingContent += chunk
          messages.value[assistantMessageIndex].thinking = removeMarkdownFormat(thinkingContent)
        } else if (type === 'progress_log') {
          if (data?.message) {
            progressLogs = [...progressLogs, data.message]
            messages.value[assistantMessageIndex].progressLogs = progressLogs
          }
        } else if (type === 'scheduler') {
          schedulerInfo = buildSchedulerViewModel(data?.scheduler, data?.coaches)
          messages.value[assistantMessageIndex].scheduler = schedulerInfo
          messages.value[assistantMessageIndex].isSchedulerExpanded = true
        } else if (type === 'answer') {
          answerContent += chunk
          messages.value[assistantMessageIndex].content = answerContent
        }
        scrollToBottom()
      },
      async (type) => {
        if (type !== 'answer') return
        const finalAnswerContent = schedulerInfo ? stripSchedulerSection(answerContent) : answerContent
        // 流式完成
        const assistantMessage = normalizeMessage({
          role: 'assistant',
          content: finalAnswerContent,
          thinking: buildVisibleThinking(thinkingContent, progressLogs),
          progressLogs,
          scheduler: schedulerInfo,
          isThinkingExpanded: messages.value[assistantMessageIndex]?.isThinkingExpanded || false,
          isSchedulerExpanded: messages.value[assistantMessageIndex]?.isSchedulerExpanded ?? true,
          timestamp: new Date()
        })
        
        messages.value[assistantMessageIndex] = assistantMessage
        updateCurrentConversation(question, assistantMessage)
        
        // 如果存在planContext或者内容看起来像训练计划，则生成卡片
        if (shouldCreateTrainingPlan(answerContent, planContext || null)) {
          // 异步处理plan生成，不阻塞消息流
          generatePlanAsync(assistantMessage, planContext || null)
        }
      },
      (error) => {
        // 移除占位符
        messages.value.splice(assistantMessageIndex, 1)
        console.error('发送消息失败', error)
        messages.value.push(
          normalizeMessage({
            role: 'assistant',
            content: '消息发送失败，请稍后重试。',
            timestamp: new Date()
          })
        )
      },
      {
        useMultiAgent,
        userProfile
      }
    )

    await scrollToBottom()
  } catch (error) {
    console.error('发送消息异常', error)
  } finally {
    loading.value = false
  }
}

// 异步处理plan生成，不阻塞消息流
const generatePlanAsync = async (message, planContext) => {
  try {
    const savedPlan = await createPlanFromAiResponse(message, planContext)
    const planCardMessage = createPlanCardMessage(savedPlan, planContext)

    // 创建更新后的消息对象 - 用简短总结替换完整训练计划文本，并添加卡片
    const updatedMessage = normalizeMessage({
      ...message,
      content: '',
      planCard: planCardMessage.planCard
    })

    // 更新messages数组中的对应消息（确保响应式更新）
    const index = messages.value.findIndex((msg) => msg.timestamp?.getTime?.() === message.timestamp?.getTime?.())
    if (index !== -1) {
      messages.value.splice(index, 1, updatedMessage)
    }

    pendingPlanContext.value = null
    sessionStorage.removeItem(PENDING_PROMPT_KEY)

    // 更新对话历史中的这条消息
    if (currentChat.value !== null && chatHistory.value[currentChat.value]) {
      const target = chatHistory.value[currentChat.value]
      target.conversation = replacePlanConversationMessage(
        target.conversation || [],
        message,
        updatedMessage,
        target.question || ''
      )
      // 同步更新 answer 字段
      target.answer = updatedMessage.content
      target.timestamp = new Date()
    }
  } catch (error) {
    console.error('训练计划生成失败:', error)
  }
}

const generatePlan = async (message) => {
  try {
    const savedPlan = await createPlanFromAiResponse(message)
    const planCardMessage = createPlanCardMessage(savedPlan)

    // 创建更新后的消息对象 - 清除原文内容，仅保留卡片
    const updatedMessage = normalizeMessage({
      ...message,
      content: '',
      planCard: planCardMessage.planCard
    })

    // 更新messages数组中的对应消息（确保响应式更新）
    const index = messages.value.findIndex((msg) => msg.timestamp?.getTime?.() === message.timestamp?.getTime?.())
    if (index !== -1) {
      messages.value.splice(index, 1, updatedMessage)
    }

    if (currentChat.value !== null && chatHistory.value[currentChat.value]) {
      const target = chatHistory.value[currentChat.value]
      target.conversation = replacePlanConversationMessage(
        target.conversation || [],
        message,
        updatedMessage,
        target.question || ''
      )
      target.answer = updatedMessage.content
      target.timestamp = new Date()
    }
    await scrollToBottom()
  } catch (error) {
    console.error('训练计划生成失败:', error)
    window.alert('训练计划生成失败，请稍后重试。')
  }
}

const normalizePreviewPlan = (plan) => ({
  ...plan,
  metadata: plan?.metadata || {},
  selected_weekdays: Array.isArray(plan?.selected_weekdays) ? plan.selected_weekdays : []
})

const parseWeeklyDaysLimit = (value) => {
  const match = String(value ?? '').match(/\d+/)
  const parsed = match ? Number(match[0]) : NaN
  if (!Number.isFinite(parsed) || parsed <= 0) return weekdayOptions.length
  return Math.min(parsed, weekdayOptions.length)
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

const getPreviewWeekdayLimit = () => parseWeeklyDaysLimit(previewPlan.value?.metadata?.weekly_days)

const isPreviewWeekdayDisabled = (day) =>
  !previewWeekdays.value.includes(day) && previewWeekdays.value.length >= getPreviewWeekdayLimit()

const closePlanPreviewModal = () => {
  showPlanPreviewModal.value = false
  previewPlan.value = null
  previewWeekdays.value = []
}

const viewPlanDetails = async (planId) => {
  planPreviewLoading.value = true
  try {
    const response = await api.get(`/training/plans/${planId}`)
    previewPlan.value = normalizePreviewPlan(response)
    previewWeekdays.value = [...previewPlan.value.selected_weekdays]
    showPlanPreviewModal.value = true
  } catch (error) {
    console.error('读取训练计划详情失败:', error)
    window.alert('训练计划详情加载失败，请稍后重试。')
  } finally {
    planPreviewLoading.value = false
  }
}

const togglePreviewWeekday = (day) => {
  const limit = getPreviewWeekdayLimit()
  if (!previewWeekdays.value.includes(day) && previewWeekdays.value.length >= limit) return
  previewWeekdays.value = previewWeekdays.value.includes(day)
    ? previewWeekdays.value.filter((item) => item !== day)
    : [...previewWeekdays.value, day]
}

const savePreviewWeekdays = async () => {
  if (!previewPlan.value || !previewWeekdays.value.length) return

  planPreviewLoading.value = true
  try {
    await api.put(`/training/plans/${previewPlan.value.id}`, {
      selected_weekdays: [...previewWeekdays.value]
    })
    localStorage.setItem(getUserActivePlanKey(), String(previewPlan.value.id))
    closePlanPreviewModal()
    router.push({ name: 'TrainingPlan' })
  } catch (error) {
    console.error('保存训练日失败', error)
    window.alert('保存训练日失败，请稍后重试。')
  } finally {
    planPreviewLoading.value = false
  }
}

const quickAction = (action) => {
  if (action === '我想生成一份运动训练计划') {
    showQuestionnaireModal.value = true
    questionnaireStepIndex.value = 0
    return
  }

  inputMessage.value = action
  nextTick(() => inputRef.value?.focus())
}

const currentQuestionnaireQuestion = computed(() => {
  const question = questionnaireQuestions[questionnaireStepIndex.value]
  return {
    ...question,
    answer: questionnaireData.value[question.key]
  }
})

const questionnaireCanProceed = computed(() => {
  if (!currentQuestionnaireQuestion.value.answer) return false
  if (currentQuestionnaireQuestion.value.key === 'injury' && currentQuestionnaireQuestion.value.answer === 'other') {
    return Boolean(questionnaireData.value.injury_detail)
  }
  return true
})

const selectQuestionnaireOption = (value) => {
  questionnaireData.value[currentQuestionnaireQuestion.value.key] = value
}

const prevQuestionnaireStep = () => {
  if (questionnaireStepIndex.value > 0) questionnaireStepIndex.value -= 1
}

const buildTrainingPrompt = () => {
  const injuryText =
    questionnaireData.value.injury === 'other'
      ? `其他伤病：${questionnaireData.value.injury_detail}`
      : questionnaireData.value.injury
  const weeklyTrainingDayTemplate = buildWeeklyTrainingDayTemplate(questionnaireData.value.weekly_days)

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
    `- 训练目标：${questionnaireData.value.goal}`,
    `- 偏好训练方式：${questionnaireData.value.method}`,
    `- 每周训练天数：${questionnaireData.value.weekly_days} 天`,
    `- 单次训练时长：${questionnaireData.value.daily_duration} 分钟`,
    `- 可接受强度：${questionnaireData.value.intensity}`,
    `- 伤病情况：${injuryText}`
  ].join('\n')
}

const buildTrainingRequestMessage = () => {
  const weeklyDays = questionnaireData.value.weekly_days || '未设置'
  const injuryText =
    questionnaireData.value.injury === 'other'
      ? questionnaireData.value.injury_detail
      : questionnaireData.value.injury

  return [
    `请根据我的问卷生成一个 1 个月训练计划。`,
    `目标：${questionnaireData.value.goal || '未设置'}`,
    `方式：${questionnaireData.value.method || '未设置'}`,
    `频率：每周 ${weeklyDays} 天`,
    `时长：每次 ${questionnaireData.value.daily_duration || '未设置'} 分钟`,
    `强度：${questionnaireData.value.intensity || '未设置'}`,
    `伤病情况：${injuryText || '无伤病困扰'}`
  ].join('\n')
}

const nextQuestionnaireStep = async () => {
  if (!questionnaireCanProceed.value || loading.value) return

  if (questionnaireStepIndex.value < questionnaireQuestions.length - 1) {
    questionnaireStepIndex.value += 1
    return
  }

  // 生成训练计划
  const prompt = buildTrainingPrompt()
  const requestMessage = buildTrainingRequestMessage()
  pendingPlanContext.value = {
    prompt,
    requestMessage,
    questionnaire: { ...questionnaireData.value },
    createdAt: new Date().toISOString()
  }

  // 关闭问卷弹窗
  showQuestionnaireModal.value = false

  // 发送消息生成计划
  await sendMessage(requestMessage, { planContext: pendingPlanContext.value })
}

const closeQuestionnaireModal = () => {
  showQuestionnaireModal.value = false
  questionnaireStepIndex.value = 0
  questionnaireData.value = {
    goal: '',
    method: '',
    weekly_days: '',
    daily_duration: '',
    intensity: '',
    injury: '',
    injury_detail: ''
  }
}

// 训练记录模态框
const openTrainingRecordModal = () => {
  showTrainingRecordModal.value = true
  resetTrainingRecordForm()
}

const closeTrainingRecordModal = () => {
  showTrainingRecordModal.value = false
}

const resetTrainingRecordForm = () => {
  trainingRecordData.value = {
    training_type: '',
    duration: 30,
    intensity: '',
    fatigue_level: 3,
    pain_level: 0,
    notes: ''
  }
}

const submitTrainingRecord = async () => {
  if (!trainingRecordData.value.training_type) {
    alert('请选择训练类型')
    return
  }

  savingTrainingRecord.value = true

  try {
    await api.post('/training/records', {
      date: new Date().toISOString().split('T')[0],
      training_type: trainingRecordData.value.training_type,
      duration: trainingRecordData.value.duration,
      intensity: trainingRecordData.value.intensity,
      fatigue_level: trainingRecordData.value.fatigue_level,
      pain_level: trainingRecordData.value.pain_level,
      notes: trainingRecordData.value.notes,
      completion_status: 'completed'
    })

    alert('训练记录已保存！')
    closeTrainingRecordModal()
    resetTrainingRecordForm()
  } catch (error) {
    alert('保存失败：' + error.message)
  } finally {
    savingTrainingRecord.value = false
  }
}

// 饮食记录模态框
const openDietRecordModal = () => {
  showDietRecordModal.value = true
  resetDietRecordForm()
}

const closeDietRecordModal = () => {
  showDietRecordModal.value = false
}

const resetDietRecordForm = () => {
  dietRecordData.value = {
    meal_type: '',
    food_content: '',
    calories: '',
    protein: '',
    notes: ''
  }
}

const submitDietRecord = async () => {
  if (!dietRecordData.value.meal_type || !dietRecordData.value.food_content) {
    alert('请填写餐别和食物内容')
    return
  }

  savingDietRecord.value = true

  try {
    await api.post('/daily/records', {
      date: new Date().toISOString().split('T')[0],
      meal_type: dietRecordData.value.meal_type,
      food_content: dietRecordData.value.food_content,
      calories: dietRecordData.value.calories,
      protein: dietRecordData.value.protein,
      notes: dietRecordData.value.notes
    })

    alert('饮食记录已保存！')
    closeDietRecordModal()
    resetDietRecordForm()
  } catch (error) {
    alert('保存失败：' + error.message)
  } finally {
    savingDietRecord.value = false
  }
}

// 体重记录模态框
const openWeightRecordModal = () => {
  showWeightRecordModal.value = true
  resetWeightRecordForm()
}

const closeWeightRecordModal = () => {
  showWeightRecordModal.value = false
}

const resetWeightRecordForm = () => {
  weightRecordData.value = {
    weight: '',
    body_fat: '',
    chest_circumference: '',
    waist_circumference: '',
    hip_circumference: '',
    notes: ''
  }
}

const submitWeightRecord = async () => {
  if (!weightRecordData.value.weight) {
    alert('请输入体重')
    return
  }

  savingWeightRecord.value = true

  try {
    await api.post('/weight/records', {
      date: new Date().toISOString().split('T')[0],
      weight: weightRecordData.value.weight,
      body_fat: weightRecordData.value.body_fat,
      chest_circumference: weightRecordData.value.chest_circumference,
      waist_circumference: weightRecordData.value.waist_circumference,
      hip_circumference: weightRecordData.value.hip_circumference,
      notes: weightRecordData.value.notes
    })

    alert('体重记录已保存！')
    closeWeightRecordModal()
    resetWeightRecordForm()
  } catch (error) {
    alert('保存失败：' + error.message)
  } finally {
    savingWeightRecord.value = false
  }
}

const handleEnter = (event) => {
  if (!event.shiftKey) {
    sendMessage()
  }
}

const loadPendingPrompt = () => {
  try {
    const raw = sessionStorage.getItem(PENDING_PROMPT_KEY)
    return raw ? JSON.parse(raw) : null
  } catch (error) {
    console.error('读取待发送训练prompt失败:', error)
    return null
  }
}

onMounted(async () => {
  try {
    const savedMode = localStorage.getItem(getUserMultiAgentModeKey())
    if (savedMode !== null) {
      enableMultiAgent.value = savedMode === 'true'
    }
  } catch (error) {
    console.error('读取多智能体模式失败:', error)
  }

  const localHistory = loadChatHistoryFromLocal()
  if (localHistory.length) {
    chatHistory.value = localHistory
  } else {
    try {
      const response = await api.getChatHistory()
      chatHistory.value = normalizeChatHistory(response?.history || [])
    } catch (error) {
      console.error('读取聊天历史失败:', error)
    }
  }

  if (route.query.autoPlan === '1') {
    const pendingPrompt = loadPendingPrompt()
    if (pendingPrompt?.prompt) {
      pendingPlanContext.value = pendingPrompt
      await sendMessage(pendingPrompt.requestMessage || pendingPrompt.prompt, { planContext: pendingPrompt })
      router.replace({ name: 'Chat' })
    }
  }
})

watch(enableMultiAgent, (value) => {
  try {
    localStorage.setItem(getUserMultiAgentModeKey(), String(value))
  } catch (error) {
    console.error('保存多智能体模式失败:', error)
  }
})

watch(
  chatHistory,
  () => {
    saveChatHistoryToLocal()
  },
  { deep: true }
)
</script>

<style scoped>
.chat-page {
  min-height: 100vh;
  background: var(--color-bg);
}

.chat-shell {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 16px 40px;
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr);
  gap: 24px;
}

.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 28px;
  box-shadow: 0 24px 60px var(--color-shadow);
}

.sidebar {
  padding: 22px 18px;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 132px);
}

.sidebar-head,
.main-head,
.plan-card-head,
.plan-modal-head,
.modal-actions,
.sidebar-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 5px;
}

.sidebar-head,
.main-head,
.plan-card-head,
.plan-modal-head {
  align-items: flex-start;
}

.sidebar-eyebrow,
.main-eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.sidebar h2,
.main-head h1,
.plan-card h3,
.plan-modal h2 {
  margin: 0;
  color: var(--color-text-primary);
}

.sidebar-actions {
  justify-content: flex-end;
}

.icon-btn,
.btn,
.suggestion-chip,
.quick-btn,
.send-btn,
.history-main,
.history-delete,
.inline-plan-btn,
.weekday-chip {
  border: none;
  cursor: pointer;
  font: inherit;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: var(--color-bg);
  color: var(--color-text-primary);
}

.icon-btn.danger {
  background: rgba(239, 68, 68, 0.12);
  color: #0056b3;
}

.history-list {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: auto;
}

.history-item {
  padding: 14px;
  border-radius: 18px;
  background: var(--color-bg);
  color: var(--color-text-primary);
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.history-main {
  flex: 1;
  padding: 0;
  text-align: left;
  background: transparent;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.history-delete {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.12);
  color: #0056b3;
  font-size: 12px;
  font-weight: 600;
}

.history-item.active {
  background: linear-gradient(135deg, rgba(52, 199, 89, 0.18), rgba(52, 199, 89, 0.08));
}

.history-main span,
.empty-copy,
.message-time,
.plan-subtitle,
.modal-copy {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.main {
  min-height: calc(100vh - 132px);
  display: flex;
  flex-direction: column;
  padding: 24px;
}

.messages {
  flex: 1;
  overflow: auto;
  padding-right: 4px;
}

.empty-state {
  min-height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 14px;
}

.empty-badge {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-hover));
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 800;
}

.quick-suggestions,
.quick-actions,
.plan-meta,
.weekday-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.suggestion-chip,
.quick-btn,
.plan-meta span,
.weekday-chip {
  padding: 10px 14px;
  border-radius: 999px;
  background: var(--color-bg);
  color: var(--color-text-primary);
  font-weight: 600;
}

.weekday-chip:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.message-row {
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}

.message-row.user {
  grid-template-columns: minmax(0, 1fr) 44px;
}

.message-row.user .avatar {
  order: 2;
}

.message-row.user .message-card {
  order: 1;
  /* background: linear-gradient(135deg, #0d2b50, var(--color-accent)); */
  background: #c2d8ee;
  color: #000000;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-bg);
  color: var(--color-text-primary);
  display: grid;
  place-items: center;
  font-weight: 800;
}

.message-card {
  background: var(--color-bg);
  border-radius: 24px;
  padding: 18px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.message-text,
.plan-summary {
  margin: 0;
  line-height: 1.7;
  white-space: pre-wrap;
}

.markdown-message {
  white-space: normal;
}

.markdown-message :deep(h1),
.markdown-message :deep(h2),
.markdown-message :deep(h3),
.markdown-message :deep(h4) {
  margin: 0 0 12px;
  line-height: 1.3;
  color: var(--color-text-primary);
}

.markdown-message :deep(h1) {
  font-size: 28px;
}

.markdown-message :deep(h2) {
  font-size: 22px;
  margin-top: 22px;
}

.markdown-message :deep(h3) {
  font-size: 18px;
  margin-top: 18px;
}

.markdown-message :deep(h4) {
  font-size: 15px;
  margin-top: 12px;
}

.markdown-message :deep(p) {
  margin: 0 0 12px;
}

.markdown-message :deep(ul) {
  margin: 0 0 12px;
  padding-left: 20px;
}

.markdown-message :deep(li) {
  margin: 0 0 8px;
}

.markdown-message :deep(code) {
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(0, 113, 227, 0.08);
  font-size: 13px;
}

.markdown-message :deep(.md-divider) {
  border: none;
  height: 1px;
  margin: 18px 0 22px;
  background: linear-gradient(90deg, transparent, rgba(0, 113, 227, 0.22), transparent);
}

/* ==================== 计划详情弹窗 markdown-content 样式 ==================== */
.markdown-content {
  color: var(--color-text-primary);
  line-height: 1.75;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  line-height: 1.3;
  color: var(--color-text-primary);
  margin: 0 0 12px;
}

.markdown-content :deep(h1) {
  font-size: 28px;
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
  border-left: 4px solid var(--color-accent);
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

.markdown-content :deep(li) {
  margin: 0 0 12px;
  font-size: 15px;
  line-height: 1.85;
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
  border-left: 3px solid var(--color-accent);
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
  border: 1px solid rgba(23, 63, 52, 0.08);
  border-radius: 14px;
  overflow: hidden;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(23, 63, 52, 0.08);
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

.inline-plan-btn {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(52, 199, 89, 0.14);
  color: var(--color-accent);
  font-weight: 700;
}

.plan-card {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.plan-tag {
  margin: 0 0 8px;
  color: var(--color-accent);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.plan-badge {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(52, 199, 89, 0.12);
  color: var(--color-accent);
  font-weight: 700;
}

.plan-head-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.plan-meta-icons {
  display: flex;
  gap: 16px;
}

.meta-icon-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 600;
}

.meta-icon {
  width: 16px;
  height: 16px;
  stroke-width: 2;
  color: var(--color-accent);
}


.summary-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 12px;
  color: var(--color-text-primary);
  font-size: 15px;
  font-weight: 700;
}

.summary-icon {
  width: 18px;
  height: 18px;
  stroke-width: 1.8;
  color: var(--color-accent);
}

.summary-content {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  padding: 14px;
}

.summary-text {
  margin: 0;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: var(--color-text-primary);
}

.plan-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: var(--color-bg);
  border-radius: 16px;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: var(--color-accent);
  flex-shrink: 0;
  margin-top: 2px;
}

.section-icon svg {
  width: 100%;
  height: 100%;
  stroke-width: 1.8;
}

.section-content h5 {
  margin: 0 0 4px;
  color: var(--color-text-primary);
  font-size: 14px;
  font-weight: 700;
}

.section-content p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.action-hint {
  margin-top: 8px;
  color: var(--color-text-secondary);
  font-size: 12px;
  text-align: center;
  width: 100%;
}

.plan-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.btn-icon {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  vertical-align: middle;
}

.quick-actions {
  margin-top: 18px;
}

.response-mode-card {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 18px;
  background: rgba(0, 113, 227, 0.05);
  border: 1px solid rgba(0, 113, 227, 0.12);
}

.response-mode-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.response-mode-toggle input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.response-mode-slider {
  position: relative;
  width: 46px;
  height: 28px;
  border-radius: 999px;
  background: rgba(134, 134, 139, 0.35);
  transition: background 0.2s ease;
  flex-shrink: 0;
}

.response-mode-slider::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.16);
  transition: transform 0.2s ease;
}

.response-mode-toggle input:checked + .response-mode-slider {
  background: var(--color-accent);
}

.response-mode-toggle input:checked + .response-mode-slider::after {
  transform: translateX(18px);
}

.response-mode-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  color: var(--color-text-primary);
}

.response-mode-copy strong {
  font-size: 14px;
}

.response-mode-copy small {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.input-bar {
  margin-top: 20px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: end;
}

.input-bar textarea {
  min-height: 56px;
  max-height: 180px;
  resize: vertical;
  padding: 16px 18px;
  border-radius: 20px;
  border: 1px solid rgba(23, 63, 52, 0.12);
  background: var(--color-bg);
  font: inherit;
  color: var(--color-text-primary);
}

.send-btn,
.btn {
  padding: 12px 18px;
  border-radius: 16px;
  font-weight: 700;
}

.btn-primary,
.send-btn {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-hover));
  color: #fff;
  box-shadow: 0 14px 28px rgba(0, 113, 227, 0.22);
}

.btn-secondary {
  background: var(--color-bg);
  color: var(--color-text-primary);
}

.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(12, 24, 20, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 40;
}

.modal-card {
  width: min(920px, 100%);
  max-height: 88vh;
  overflow: auto;
  position: relative;
  border-radius: 30px;
  background: linear-gradient(180deg, var(--color-surface), var(--color-bg));
  box-shadow: 0 28px 70px rgba(12, 24, 20, 0.22);
}

.plan-modal {
  padding: 32px;
}

.questionnaire-modal {
  padding: 32px;
  display: flex;
  flex-direction: column;
}

.questionnaire-header-modal {
  margin-bottom: 28px;
}

.questionnaire-header-modal .coach-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  background: rgba(97, 82, 223, 0.08);
  color: var(--color-accent);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 14px;
}

.questionnaire-header-modal h2 {
  margin: 0 0 10px;
  font-size: 28px;
  line-height: 1.3;
  color: var(--color-text-primary);
}

.questionnaire-header-modal .modal-copy {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 15px;
}

.progress-bar {
  margin-top: 20px;
  height: 4px;
  background: var(--color-bg);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent), var(--color-accent-hover));
  transition: width 0.3s ease;
}

.questionnaire-content {
  flex: 1;
  margin-bottom: 24px;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.option-card {
  border: 1px solid var(--color-bg);
  background: #fff;
  border-radius: 18px;
  min-height: 80px;
  padding: 16px 14px;
  text-align: center;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
  cursor: pointer;
}

.option-card:hover {
  transform: translateY(-2px);
  border-color: rgba(54, 209, 149, 0.5);
  box-shadow: 0 10px 24px rgba(52, 199, 137, 0.12);
}

.option-card.selected {
  border-color: var(--color-accent);
  background: linear-gradient(135deg, rgba(0, 113, 227, 0.12), rgba(0, 113, 227, 0.04));
  color: var(--color-accent);
  box-shadow: 0 10px 24px rgba(0, 113, 227, 0.12);
}

.form-field {
  margin-top: 20px;
}

.form-field label {
  display: block;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.form-field textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--color-bg);
  border-radius: 16px;
  background: var(--color-bg);
  font: inherit;
  color: var(--color-text-primary);
  resize: vertical;
}

.form-field textarea:focus {
  outline: none;
  border-color: rgba(52, 199, 89, 0.5);
  background: #fff;
}

.modal-close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--color-bg);
  color: var(--color-text-primary);
  font-size: 24px;
  cursor: pointer;
}

.modal-section {
  margin-top: 20px;
  padding: 22px;
  border-radius: 24px;
  background: #fff;
  border: 1px solid rgba(23, 63, 52, 0.08);
}

.modal-section h3 {
  margin: 0 0 12px;
}

.preview-markdown {
  color: var(--color-text-primary);
}

.weekday-grid {
  margin-top: 14px;
}

.weekday-chip.active {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-hover));
  color: #fff;
}

.modal-actions {
  margin-top: 22px;
  justify-content: flex-end;
}

/* 思考过程样式 */
.thinking-container {
  margin-bottom: 14px;
  padding: 14px;
  background: linear-gradient(135deg, rgba(97, 82, 223, 0.08), rgba(52, 199, 89, 0.04));
  border-radius: 16px;
  border-left: 3px solid var(--color-accent);
}

.thinking-toggle {
  width: 100%;
  padding: 0;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--color-accent);
  font-weight: 600;
  font-size: 14px;
  transition: color 0.2s ease;
}

.thinking-toggle:hover {
  color: var(--color-accent);
}

.thinking-icon {
  display: inline-block;
  transition: transform 0.2s ease;
  font-size: 12px;
}

.thinking-label {
  flex: 1;
  text-align: left;
}

.thinking-content {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(97, 82, 223, 0.2);
  font-size: 13px;
  color: var(--color-accent);
  line-height: 1.6;
  display: grid;
  gap: 14px;
}

.thinking-line {
  margin: 6px 0;
  white-space: pre-wrap;
}

.progress-block,
.thinking-block {
  padding: 0;
}

.progress-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.progress-tag {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #173f34;
}

.progress-count {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.progress-list {
  margin-top: 10px;
  display: grid;
  gap: 8px;
}

.progress-item {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text-secondary);
}

.scheduler-card {
  margin-bottom: 14px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(0, 113, 227, 0.05);
  border: 1px solid rgba(0, 113, 227, 0.12);
}

.scheduler-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.scheduler-tag {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.scheduler-head h4 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text-primary);
}

.scheduler-toggle {
  border: none;
  background: transparent;
  color: var(--color-accent);
  font-weight: 700;
  cursor: pointer;
}

.scheduler-copy {
  margin: 10px 0 0;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.scheduler-chip-row {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.scheduler-chip,
.scheduler-batch {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #fff;
  color: var(--color-text-primary);
  border: 1px solid rgba(0, 113, 227, 0.12);
  font-size: 13px;
  font-weight: 600;
}

.scheduler-details {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(0, 113, 227, 0.12);
  display: grid;
  gap: 14px;
}

.scheduler-detail-block h5 {
  margin: 0 0 8px;
  font-size: 14px;
  color: var(--color-text-primary);
}

.scheduler-detail-block ul {
  margin: 0;
  padding-left: 20px;
  color: var(--color-text-secondary);
}

.scheduler-detail-block li {
  margin-bottom: 6px;
  line-height: 1.6;
}

.scheduler-batches {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 加载状态样式 */
.message-text.loading {
  font-style: italic;
  color: #999;
}

.loading-dots {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@media (max-width: 1024px) {
  .chat-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    min-height: auto;
  }

  .main {
    min-height: auto;
  }
}

@media (max-width: 720px) {
  .chat-shell,
  .main,
  .plan-modal {
    padding-left: 14px;
    padding-right: 14px;
  }

  .main-head,
  .plan-modal-head,
  .modal-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .input-bar {
    grid-template-columns: 1fr;
  }
}

/* 快速操作按钮图标样式 */
.quick-icon {
  font-size: 16px;
  margin-right: 6px;
}

/* 记录模态框样式 */
.record-modal {
  max-width: 500px;
}

.record-modal-head {
  margin-bottom: 10px;
}

.record-modal-head .coach-tag {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  background: rgba(0, 113, 227, 0.08);
  color: var(--color-accent);
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 14px;
}

.record-modal-head h2 {
  margin: 0 0 10px;
  font-size: 28px;
  line-height: 1.3;
  color: var(--color-text-primary);
}

.record-modal-head .modal-copy {
  margin: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
}

.range-selector {
  display: flex;
  gap: 8px;
}

.fatigue-option,
.pain-option {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.fatigue-option.selected,
.pain-option.selected {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.fatigue-option:hover,
.pain-option:hover {
  border-color: #4CAF50;
}

.measure-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.measure-inputs > div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.measure-inputs > div label {
  font-size: 12px;
  color: #666;
}

.weight-input {
  font-size: 18px;
  text-align: center;
}

@media (max-width: 720px) {
  .record-modal {
    padding: 24px 18px;
  }

  .form-row,
  .measure-inputs {
    grid-template-columns: 1fr;
  }

  .range-selector {
    flex-wrap: wrap;
  }
}
</style>
