<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import { fetchSessionDetail, fetchSessionHistory } from '../services/interview'
import type { SessionDetail, SessionStats } from '../types'
import ScoreCircle from '../components/ScoreCircle.vue'
import { CheckCircle2, AlertTriangle, RotateCcw, MessageCircle, ArrowLeft, FileText } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const store = useInterviewStore()

// 历史模式：通过 route param 或自动加载最近报告
const historySessionId = computed(() => route.params.sessionId as string | undefined)

const historyDetail = ref<SessionDetail | null>(null)
const loading = ref(false)
const error = ref('')
const noHistory = ref(false)

// 是否使用历史数据（非当前面试 Pinia 数据）
const isHistoryMode = computed(() => !!historyDetail.value)
// 当前面试刚结束，Pinia 里有数据
const hasCurrentReport = computed(() => store.interviewStatus === 'ended' && !!store.stats)

onMounted(async () => {
  // 1. 指定了 sessionId → 加载该面试报告
  if (historySessionId.value) {
    loading.value = true
    try {
      historyDetail.value = await fetchSessionDetail(historySessionId.value)
    } catch {
      error.value = '加载失败，该面试记录可能不存在'
    }
    loading.value = false
    return
  }

  // 2. 当前面试刚结束，Pinia 有数据 → 直接用
  if (hasCurrentReport.value) return

  // 3. 没有当前面试数据 → 自动加载最近一次已完成面试
  loading.value = true
  try {
    const sessions = await fetchSessionHistory()
    const completed = sessions.find(s => s.status === 'completed')
    if (completed) {
      historyDetail.value = await fetchSessionDetail(completed.session_id)
    } else {
      noHistory.value = true
    }
  } catch {
    noHistory.value = true
  }
  loading.value = false
})

// 统一数据访问
const reportStats = computed<SessionStats | null>(() => {
  if (isHistoryMode.value) return historyDetail.value?.stats ?? null
  return store.stats
})

const score = computed(() => {
  if (reportStats.value?.avg_score) return Math.round(reportStats.value.avg_score)
  return 0
})

const turnCount = computed(() => reportStats.value?.turn_count || 0)

const styleMap: Record<string, string> = {
  default: '标准模式',
  strict: '地狱高压模式',
  friendly: '温和引导模式',
  technical_deep: '技术深挖模式',
  behavioral: '行为面试模式',
  system_design: '系统设计模式',
  rapid_fire: '快问快答模式',
  project_focused: '项目经验模式',
}

const jobTitle = computed(() => {
  if (isHistoryMode.value) return historyDetail.value?.session?.position || '未知岗位'
  return store.config.jobTitle
})

const styleLabel = computed(() => {
  if (isHistoryMode.value) {
    const style = historyDetail.value?.session?.interview_style || ''
    return styleMap[style] || style
  }
  return styleMap[store.config.style] || store.config.style
})

const evalSummary = computed(() => {
  if (isHistoryMode.value) return historyDetail.value?.session?.eval_summary || ''
  return store.evalSummary
})

const evalStrengths = computed(() => {
  if (isHistoryMode.value) return historyDetail.value?.session?.eval_strengths || ''
  return store.evalStrengths
})

const evalWeaknesses = computed(() => {
  if (isHistoryMode.value) return historyDetail.value?.session?.eval_weaknesses || ''
  return store.evalWeaknesses
})

function retry() {
  if (isHistoryMode.value) {
    const sid = historySessionId.value || historyDetail.value?.session?.session_id
    router.push(`/history/${sid}`)
  } else {
    store.reset()
    router.push('/')
  }
}
</script>

<template>
  <div class="fade-in min-h-full">
    <!-- 加载/错误状态 -->
    <div v-if="loading" class="ui-empty-state px-6 py-20 text-center text-slate-400 dark:text-white/40">加载中...</div>
    <div v-else-if="error" class="ui-empty-state px-6 py-20 text-center text-red-500">{{ error }}</div>
    <div v-else-if="noHistory" class="ui-empty-state px-6 py-20 text-center">
      <FileText class="w-12 h-12 mx-auto text-slate-300 dark:text-white/20 mb-3" />
      <p class="text-sm text-slate-400 dark:text-white/40 mb-4">暂无评估报告，完成一次面试后这里会显示</p>
      <button @click="router.push('/')"
        class="ui-btn ui-btn-primary px-5 py-2.5 text-sm">
        开始面试
      </button>
    </div>
    <template v-else>
      <!-- 历史模式返回按钮 -->
      <button v-if="isHistoryMode" @click="router.push(`/history/${historySessionId || historyDetail?.session?.session_id}`)"
        class="ui-btn ui-btn-secondary mb-4 px-4 py-2 text-sm">
        <ArrowLeft class="w-4 h-4" /> 返回面试详情
      </button>

      <div class="report-hero ui-card mb-8 flex flex-col justify-between gap-5 p-6 sm:flex-row sm:items-end">
        <div class="relative z-[1]">
          <span class="ui-section-badge">评估报告</span>
          <h2 class="ui-page-title mt-4 text-3xl">面试评估报告</h2>
          <p class="ui-page-subtitle mt-2 font-medium">{{ jobTitle }} · {{ styleLabel }}</p>
          <p class="report-hero__meta mt-3 inline-flex rounded-full px-3 py-1 text-xs font-semibold">
            本次面试共进行了 {{ turnCount }} 轮对话
          </p>
        </div>
        <button @click="retry"
          class="ui-btn ui-btn-secondary report-hero__action mt-1 px-6 py-3">
          <RotateCcw class="w-4 h-4" /> {{ isHistoryMode ? '返回详情' : '重新挑战' }}
        </button>
      </div>

      <!-- 总体评价 -->
      <div v-if="evalSummary" class="report-summary ui-card mb-6 p-5">
        <h3 class="font-bold text-slate-800 dark:text-white text-lg mb-2 flex items-center gap-2">
          <MessageCircle class="w-5 h-5 text-primary" /> AI 面试官总评
        </h3>
        <p class="text-slate-600 dark:text-slate-300 text-sm leading-relaxed">{{ evalSummary }}</p>
      </div>

      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <!-- 综合得分 + 各维度 -->
        <div class="lg:col-span-1 space-y-6">
          <div class="report-score-card ui-card flex flex-col items-center justify-center p-8 text-center">
            <ScoreCircle :score="score" />
            <h3 class="text-xl font-bold text-slate-800 dark:text-white mt-2">综合评分</h3>
          </div>
          <!-- 各维度评分 -->
          <div v-if="reportStats?.evaluations?.length" class="ui-card space-y-3 p-5">
            <div v-for="ev in reportStats.evaluations" :key="ev.dimension" class="report-dimension-row flex items-center gap-3">
              <div class="flex-1 min-w-0">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm font-medium text-slate-700 dark:text-slate-300">{{ ev.dimension }}</span>
                  <span class="text-sm font-bold" :class="ev.score >= 7 ? 'text-emerald-600 dark:text-emerald-400' : ev.score >= 5 ? 'text-amber-600 dark:text-amber-400' : 'text-red-600 dark:text-red-400'">{{ ev.score }}/10</span>
                </div>
                <div class="h-2 rounded-full bg-slate-100 dark:bg-white/10 overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-500"
                    :class="ev.score >= 7 ? 'bg-emerald-500' : ev.score >= 5 ? 'bg-amber-500' : 'bg-red-500'"
                    :style="{ width: ev.score * 10 + '%' }"></div>
                </div>
                <p v-if="ev.comment && !ev.comment.includes('待 AI')" class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ ev.comment }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 优势 + 不足 -->
        <div class="report-insights lg:col-span-2">
          <div class="report-insight report-insight--good rounded-[28px] p-6">
            <h3 class="font-bold text-emerald-800 dark:text-emerald-400 text-lg mb-3 flex items-center gap-2">
              <CheckCircle2 class="w-5 h-5" /> 优势亮点
            </h3>
            <p class="report-insight__body text-sm leading-relaxed">
              {{ evalStrengths || (isHistoryMode ? '暂无数据' : '面试评估生成中...') }}
            </p>
          </div>
          <div class="report-insight report-insight--warn rounded-[28px] p-6">
            <h3 class="font-bold text-amber-800 dark:text-amber-400 text-lg mb-3 flex items-center gap-2">
              <AlertTriangle class="w-5 h-5" /> 改进建议
            </h3>
            <p class="report-insight__body text-sm leading-relaxed">
              {{ evalWeaknesses || (isHistoryMode ? '暂无数据' : '面试评估生成中...') }}
            </p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.report-hero {
  position: relative;
  overflow: hidden;
}

.report-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 14% 20%, rgba(59, 130, 246, 0.12), transparent 28%),
    radial-gradient(circle at 88% 16%, rgba(99, 102, 241, 0.1), transparent 24%);
  pointer-events: none;
}

.report-hero__meta {
  position: relative;
  z-index: 1;
  color: var(--ui-accent-strong);
  background: var(--ui-accent-soft);
  border: 1px solid var(--ui-border-subtle);
}

.report-hero__action {
  position: relative;
  z-index: 1;
}

.report-summary {
  position: relative;
  overflow: hidden;
  border-color: var(--ui-border-default);
  background:
    linear-gradient(180deg, var(--ui-surface-raised) 0%, var(--ui-surface-2) 100%);
}

.report-summary::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 14% 20%, rgba(59, 130, 246, 0.12), transparent 26%),
    linear-gradient(135deg, rgba(59, 130, 246, 0.06), rgba(99, 102, 241, 0.04), transparent 70%);
  pointer-events: none;
}

.report-score-card {
  min-height: 260px;
}

.report-dimension-row {
  padding: 0.8rem 0.9rem;
  border-radius: 1rem;
  background: var(--ui-surface-2);
  border: 1px solid var(--ui-border-default);
}

.report-insights {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  align-content: start;
  align-self: start;
}

.report-insight {
  position: relative;
  overflow: hidden;
  border: 1px solid transparent;
  background: linear-gradient(180deg, var(--ui-surface-raised) 0%, var(--ui-surface-1) 100%);
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.06);
}

.report-insight::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.9;
}

.report-insight__body {
  position: relative;
  z-index: 1;
  color: var(--ui-text-secondary);
}

.report-insight--good {
  border-color: rgba(16, 185, 129, 0.18);
}

.report-insight--good::before {
  background:
    radial-gradient(circle at 12% 18%, rgba(16, 185, 129, 0.16), transparent 28%),
    linear-gradient(180deg, rgba(16, 185, 129, 0.06), transparent 76%);
}

.report-insight--warn {
  border-color: rgba(245, 158, 11, 0.18);
}

.report-insight--warn::before {
  background:
    radial-gradient(circle at 12% 18%, rgba(245, 158, 11, 0.14), transparent 28%),
    linear-gradient(180deg, rgba(245, 158, 11, 0.05), transparent 76%);
}

.dark .report-dimension-row {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .report-summary {
  background:
    linear-gradient(180deg, rgba(19, 20, 28, 0.96) 0%, rgba(10, 11, 20, 0.92) 100%);
}

.dark .report-summary::before {
  background:
    radial-gradient(circle at 14% 20%, rgba(99, 102, 241, 0.14), transparent 28%),
    linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(99, 102, 241, 0.06), transparent 70%);
}

.dark .report-insight__body {
  color: rgba(226, 232, 240, 0.82);
}

.dark .report-insight--good {
  border-color: rgba(16, 185, 129, 0.18);
}

.dark .report-insight--good::before {
  background:
    radial-gradient(circle at 12% 18%, rgba(16, 185, 129, 0.16), transparent 30%),
    linear-gradient(180deg, rgba(16, 185, 129, 0.06), transparent 78%);
}

.dark .report-insight--warn {
  border-color: rgba(245, 158, 11, 0.18);
}

.dark .report-insight--warn::before {
  background:
    radial-gradient(circle at 12% 18%, rgba(245, 158, 11, 0.14), transparent 30%),
    linear-gradient(180deg, rgba(245, 158, 11, 0.05), transparent 78%);
}
</style>
