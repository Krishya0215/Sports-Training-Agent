/**
 * 流式响应持久化 composable
 * 支持跨页面恢复 AI 生成进度
 */
import { ref, onMounted, onUnmounted } from 'vue'
import * as chatDB from '../utils/chatPersistence.js'

const STORAGE_KEY = 'sports-training-user-id'

export function useStreamingPersistence() {
  // 从 localStorage 获取用户 ID
  const getUserId = () => {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    return user?.id || 'anonymous'
  }

  const userId = getUserId()
  const currentUser = JSON.parse(localStorage.getItem('user') || 'null')

  // 状态
  const isIncompleteGeneration = ref(false)
  const loading = ref(false)

  // 当前会话 ID
  const currentConversationId = ref(`conv-${userId}-${Date.now()}`)

  /**
   * 保存消息到 IndexedDB
   */
  const saveMessage = async (message) => {
    try {
      await chatDB.saveMessage({
        ...message,
        userId,
        conversationId: currentConversationId.value
      })
    } catch (error) {
      console.error('保存消息失败:', error)
    }
  }

  /**
   * 保存用户消息
   */
  const saveUserMessage = async (content) => {
    await saveMessage({
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    })
  }

  /**
   * 保存助手消息块
   */
  const saveAssistantChunk = async (content, type) => {
    await saveMessage({
      role: 'assistant',
      content,
      type,
      timestamp: new Date().toISOString(),
      completed: false
    })
  }

  /**
   * 标记助手消息为完成
   */
  const markAssistantComplete = async (content, type) => {
    await saveMessage({
      role: 'assistant',
      content,
      type,
      timestamp: new Date().toISOString(),
      completed: true
    })

    // 清除流式状态
    await clearStreamingState()
  }

  /**
   * 保存流式生成状态
   */
  const saveStreamingState = async (generating) => {
    try {
      await chatDB.saveStreamingState({
        userId,
        conversationId: currentConversationId.value,
        generating,
        question: '',
        startedAt: new Date().toISOString()
      })

      isIncompleteGeneration.value = await chatDB.hasIncompleteGeneration(userId)
    } catch (error) {
      console.error('保存流式状态失败:', error)
    }
  }

  /**
   * 清除流式生成状态
   */
  const clearStreamingState = async () => {
    try {
      await chatDB.saveStreamingState({
        userId,
        conversationId: currentConversationId.value,
        generating: false,
        completed: true,
        updatedAt: new Date().toISOString()
      })

      isIncompleteGeneration.value = false
    } catch (error) {
      console.error('清除流式状态失败:', error)
    }
  }

  /**
   * 加载用户的消息历史
   */
  const loadUserMessages = async () => {
    try {
      const messages = await chatDB.getUserMessages(userId)

      // 检查是否有未完成的生成
      const hasIncomplete = await chatDB.hasIncompleteGeneration(userId)
      isIncompleteGeneration.value = hasIncomplete

      return messages
    } catch (error) {
      console.error('加载消息失败:', error)
      return []
    }
  }

  /**
   * 继续未完成的生成（轮询）
   */
  const pollIncompleteGeneration = async () => {
    const state = await chatDB.getStreamingState(userId)

    if (!state || state.completed) {
      isIncompleteGeneration.value = false
      return
    }

    // 检查是否过期（超过10分钟视为过期）
    const updatedAt = new Date(state.updatedAt)
    const now = new Date()
    const diffMinutes = (now - updatedAt) / (1000 * 60)

    if (diffMinutes > 10) {
      await chatDB.clearStreamingState(userId)
      isIncompleteGeneration.value = false
      return
    }

    // 显示未完成提示
    isIncompleteGeneration.value = true
  }

  /**
   * 清除未完成的生成状态
   */
  const clearIncompleteState = async () => {
    await clearStreamingState()
    await chatDB.clearStreamingState(userId)
    isIncompleteGeneration.value = false
  }

  // 页面挂载时检查
  onMounted(async () => {
    await pollIncompleteGeneration()
  })

  return {
    userId,
    currentConversationId,
    isIncompleteGeneration,
    loading,
    saveMessage,
    saveUserMessage,
    saveAssistantChunk,
    markAssistantComplete,
    saveStreamingState,
    clearStreamingState,
    loadUserMessages,
    pollIncompleteGeneration,
    clearIncompleteState
  }
}
