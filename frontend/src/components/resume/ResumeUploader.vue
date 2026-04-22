<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ChevronDown,
  ClipboardPenLine,
  FileBarChart,
  FileCheck,
  FileText,
  RefreshCw,
  Sparkles,
  Upload,
} from 'lucide-vue-next'
import { useResumeStore } from '../../stores/resume'
import { useInterviewStore } from '../../stores/interview'
import { useResumeQuestionnaireStore } from '../../stores/resumeQuestionnaire'
import { fetchLatestResume } from '../../services/resume'
import { fetchSessionDetail, fetchSessionHistory } from '../../services/interview'
import type { SessionDetail } from '../../types'
import type { ResumeReportContext } from '../../types/resume'
import JobTagPicker from '../JobTagPicker.vue'
import CatLoading from '../CatLoading.vue'
import QuestionnaireForm from './QuestionnaireForm.vue'
import { isReusableOcrText } from '../../utils/ocr'
import { generateQuestionnairePromptContext, hasMeaningfulQuestionnaireData } from '../../utils/prompt-serializer'

const store = useResumeStore()
const interviewStore = useInterviewStore()
const questionnaireStore = useResumeQuestionnaireStore()
const file = ref<File | null>(null)
const jobTitle = ref('')
const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const isQuestionnaireOpen = ref(true)

const existingResumeName = ref('')
const existingOcrText = ref('')
const existingResumeSessionId = ref('')
const reportContextLabel = ref('')
const loadingExisting = ref(true)
const mode = ref<'existing' | 'upload'>('existing')

function buildReportContext(detail: SessionDetail): ResumeReportContext | null {
  const evaluations = detail.stats?.evaluations || []
  const summary = detail.session.eval_summary || ''
  const strengths = detail.session.eval_strengths || ''
  const weaknesses = detail.session.eval_weaknesses || ''

  if (!evaluations.length && !summary && !strengths && !weaknesses) return null

  return {
    sessionId: detail.session.session_id,
    position: detail.session.position,
    avgScore: detail.stats?.avg_score,
    summary,
    strengths,
    weaknesses,
    evaluations,
  }
}

function applyReportContext(detail: SessionDetail) {
  const context = buildReportContext(detail)
  if (!context) return false

  store.setReportContext(context)
  const scoreText = typeof context.avgScore === 'number' ? `，均分 ${context.avgScore.toFixed(1)}` : ''
  reportContextLabel.value = `${context.position || '最近一次面试'}${scoreText}`
  if (!jobTitle.value && detail.session.position) {
    jobTitle.value = detail.session.position
  }
  return true
}

async function loadReportContextForSession(sessionId: string) {
  reportContextLabel.value = ''
  store.setReportContext(null)

  if (!sessionId) return false

  try {
    const detail = await fetchSessionDetail(sessionId)
    return applyReportContext(detail)
  } catch {
    reportContextLabel.value = ''
    store.setReportContext(null)
    return false
  }
}

async function loadLatestReportContext() {
  reportContextLabel.value = ''
  store.setReportContext(null)

  try {
    const sessions = await fetchSessionHistory()
    const completed = sessions.find((session) => session.status === 'completed')
    if (!completed) return

    await loadReportContextForSession(completed.session_id)
  } catch {
    reportContextLabel.value = ''
    store.setReportContext(null)
  }
}

async function loadExistingResumeReportContext() {
  if (!existingResumeSessionId.value) {
    reportContextLabel.value = ''
    store.setReportContext(null)
    return
  }

  await loadReportContextForSession(existingResumeSessionId.value)
}

onMounted(async () => {
  const localOcr = interviewStore.config.resumeOcrText || ''
  if (isReusableOcrText(localOcr)) {
    existingOcrText.value = localOcr
    existingResumeName.value = interviewStore.config.resumeFileName || '面试中的简历'
    existingResumeSessionId.value = (
      interviewStore.config.resumeSourceSessionId
      || interviewStore.lastSavedSessionId
      || interviewStore.currentSessionId
      || ''
    )
    jobTitle.value = interviewStore.config.jobTitle || ''
    await loadExistingResumeReportContext()
    loadingExisting.value = false
    return
  }

  try {
    const resume = await fetchLatestResume()
    const latestOcrText = resume?.ocr_result || ''
    if (isReusableOcrText(latestOcrText)) {
      existingOcrText.value = latestOcrText
      existingResumeName.value = resume?.file_name || '历史简历'
      existingResumeSessionId.value = resume?.session_id || ''
      await loadExistingResumeReportContext()
    }
  } catch {
    // ignore
  }

  if (!existingOcrText.value) {
    await loadLatestReportContext()
  }
  loadingExisting.value = false
})

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  file.value = input.files?.[0] || null
  if (file.value) mode.value = 'upload'
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const dropped = e.dataTransfer?.files?.[0]
  if (dropped) {
    file.value = dropped
    mode.value = 'upload'
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

async function switchToUpload() {
  mode.value = 'upload'
  file.value = null
  await loadLatestReportContext()
}

async function switchToExisting() {
  mode.value = 'existing'
  file.value = null
  await loadExistingResumeReportContext()
}

function syncQuestionnaireContext() {
  if (hasMeaningfulQuestionnaireData(questionnaireStore.formData)) {
    store.setQuestionnaireContext(generateQuestionnairePromptContext(questionnaireStore.formData))
    return
  }

  store.setQuestionnaireContext(null)
}

function startAnalyze() {
  syncQuestionnaireContext()
  const finalJobTitle = jobTitle.value.trim() || questionnaireStore.formData.targetRole.trim()

  if (mode.value === 'existing' && existingOcrText.value) {
    store.analyzeFromOcr(existingOcrText.value, finalJobTitle)
  } else if (mode.value === 'upload' && file.value) {
    store.analyzeResume(file.value, finalJobTitle)
  } else if (file.value) {
    store.analyzeResume(file.value, finalJobTitle)
  }
}

const canStartAnalyze = computed(() => {
  if (store.phase === 'analyzing') return false
  if (file.value) return true
  if (mode.value === 'existing') return !!existingOcrText.value
  return false
})

const hasQuestionnaireContent = computed(() => hasMeaningfulQuestionnaireData(questionnaireStore.formData))

const questionnaireHighlights = computed(() => {
  const items: string[] = []
  const meaningfulExperienceCount = questionnaireStore.formData.workExperiences.filter((exp) => (
    exp.companyName.trim()
    || exp.jobTitle.trim()
    || exp.outcomeImprovement?.trim()
    || exp.implicitOutcomes?.length
  )).length
  if (questionnaireStore.formData.targetRole.trim()) items.push(questionnaireStore.formData.targetRole.trim())
  if (questionnaireStore.formData.optimizationGoals.length) items.push(`${questionnaireStore.formData.optimizationGoals.length} 项优化重点`)
  if (questionnaireStore.formData.hasJd && questionnaireStore.formData.jdContent?.trim()) items.push('已补充 JD')
  if (meaningfulExperienceCount) items.push(`${meaningfulExperienceCount} 段经历补充`)
  return items.slice(0, 4)
})
</script>

<template>
  <div class="relative">
    <CatLoading
      v-if="store.phase === 'analyzing'"
      variant="corner"
      :blocking="false"
      :thinking-text="store.thinkingText"
      :stage="store.thinkingStage || '正在分析当前输入内容'"
      :message="store.skipOcr ? 'AI 正在分析历史简历' : '正在提取简历内容并进行 AI 分析'"
    />

    <div v-if="loadingExisting" class="flex items-center justify-center py-16 text-slate-400 dark:text-slate-500">
      <RefreshCw class="mr-2 h-5 w-5 animate-spin" /> 检查已有简历与报告中...
    </div>

    <div v-else class="space-y-6">
      <div v-if="existingOcrText && mode === 'existing'" class="existing-card">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 dark:bg-emerald-900/30">
            <FileCheck class="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-slate-700 dark:text-white/90">{{ existingResumeName }}</p>
            <p class="text-xs text-slate-400 dark:text-slate-500">已解析，可直接优化</p>
          </div>
        </div>
        <button
          @click="switchToUpload"
          class="mt-3 flex items-center gap-1 text-xs text-primary hover:underline"
        >
          <Upload class="h-3 w-3" />
          上传其他简历
        </button>
      </div>

      <div v-if="store.reportContext" class="report-card">
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 dark:bg-indigo-900/30">
            <FileBarChart class="h-5 w-5 text-primary" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-slate-700 dark:text-white/90">已附加面试评估报告</p>
            <p class="truncate text-xs text-slate-400 dark:text-slate-500">{{ reportContextLabel || '将结合最近一次面试反馈优化简历' }}</p>
          </div>
        </div>
      </div>

      <div v-if="!existingOcrText || mode === 'upload'">
        <button
          v-if="existingOcrText && mode === 'upload'"
          @click="switchToExisting"
          class="mb-3 flex items-center gap-1 text-xs text-primary hover:underline"
        >
          <FileCheck class="h-3 w-3" />
          使用已有简历“{{ existingResumeName }}”
        </button>

        <div
          class="upload-zone"
          :class="{ 'drag-active': isDragging }"
          @dragover.prevent="isDragging = true"
          @dragleave="isDragging = false"
          @drop.prevent="onDrop"
          @click="triggerFileInput"
        >
          <input
            ref="fileInput"
            type="file"
            accept=".pdf,.docx,.md,.markdown,.txt,.jpg,.jpeg,.png,.bmp,.webp,.heic,.heif"
            class="hidden"
            @change="onFileChange"
          />
          <div v-if="!file" class="flex flex-col items-center gap-2 text-slate-400 dark:text-slate-500">
            <Upload class="h-8 w-8" />
            <p class="text-sm">拖拽简历到此处，或点击上传</p>
            <p class="text-xs">支持 PDF / Word(.docx) / Markdown / TXT / 图片</p>
          </div>
          <div v-else class="flex items-center gap-3">
            <FileText class="h-6 w-6 text-primary" />
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-slate-700 dark:text-white/90">{{ file.name }}</p>
              <p class="text-xs text-slate-400">{{ (file.size / 1024).toFixed(0) }} KB</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <label class="mb-2 block text-sm font-medium text-slate-600 dark:text-slate-300">目标岗位（可选）</label>
        <JobTagPicker v-model="jobTitle" />
      </div>

      <button
        @click="startAnalyze"
        :disabled="!canStartAnalyze"
        class="flex w-full items-center justify-center gap-2 rounded-xl py-3 font-bold text-white transition-all"
        :class="canStartAnalyze
          ? 'bg-primary shadow-md hover:bg-indigo-700 hover:shadow-lg'
          : 'cursor-not-allowed bg-slate-300 dark:bg-slate-700'"
      >
        <Sparkles class="h-4 w-4" />
        开始优化简历
      </button>

      <div class="mt-2 flex items-center justify-center text-xs text-slate-400 dark:text-slate-500">
        不填写问卷也可以直接优化。下面的意向问卷仅作为额外偏好输入。
      </div>

      <p v-if="store.error" class="text-center text-sm text-red-500">{{ store.error }}</p>

      <section class="questionnaire-shell">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="min-w-0">
            <div class="inline-flex items-center gap-2 rounded-full border border-amber-200/80 bg-amber-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-amber-700 dark:border-amber-400/20 dark:bg-amber-400/10 dark:text-amber-200">
              <ClipboardPenLine class="h-3.5 w-3.5" />
              可选意向问卷
            </div>
            <h3 class="mt-3 text-lg font-bold text-slate-800 dark:text-white">告诉 AI 你更想突出什么</h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              这里填写的内容会作为优化偏好注入，帮助 AI 更贴近你的目标岗位、成果表达和风格要求。
            </p>
          </div>
          <button
            type="button"
            class="toggle-questionnaire"
            @click="isQuestionnaireOpen = !isQuestionnaireOpen"
          >
            <span>{{ isQuestionnaireOpen ? '收起问卷' : '展开填写' }}</span>
            <ChevronDown class="h-4 w-4 transition-transform" :class="isQuestionnaireOpen ? 'rotate-180' : ''" />
          </button>
        </div>

        <div class="mt-4 flex flex-wrap items-center gap-2">
          <span class="summary-pill" :class="hasQuestionnaireContent ? 'summary-pill-active' : 'summary-pill-idle'">
            {{ hasQuestionnaireContent ? '已填写偏好' : '暂未填写偏好' }}
          </span>
          <span v-for="item in questionnaireHighlights" :key="item" class="summary-pill">
            {{ item }}
          </span>
          <span v-if="!questionnaireHighlights.length" class="summary-pill summary-pill-idle">
            可选补充求职方向、JD、成果表达、风格要求
          </span>
        </div>

        <Transition name="questionnaire-expand">
          <div v-if="isQuestionnaireOpen" class="mt-5">
            <QuestionnaireForm @optimize-now="startAnalyze" />
          </div>
        </Transition>
      </section>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.existing-card,
.report-card {
  @apply rounded-2xl border p-4;
}

.existing-card {
  background: rgba(16, 185, 129, 0.04);
  border-color: rgba(16, 185, 129, 0.2);
}

.report-card {
  background: rgba(79, 70, 229, 0.04);
  border-color: rgba(79, 70, 229, 0.18);
}

.dark .existing-card {
  background: rgba(16, 185, 129, 0.06);
  border-color: rgba(16, 185, 129, 0.15);
}

.dark .report-card {
  background: rgba(79, 70, 229, 0.08);
  border-color: rgba(99, 102, 241, 0.2);
}

.upload-zone {
  @apply cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition-all;
  border-color: rgb(203, 213, 225);
}

.upload-zone:hover {
  border-color: var(--color-primary);
  background: rgba(79, 70, 229, 0.03);
}

.dark .upload-zone {
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .upload-zone:hover {
  border-color: var(--color-primary);
  background: rgba(79, 70, 229, 0.06);
}

.drag-active {
  border-color: var(--color-primary) !important;
  background: rgba(79, 70, 229, 0.06) !important;
}

.questionnaire-shell {
  @apply rounded-[28px] border p-5 sm:p-6;
  background:
    radial-gradient(circle at top right, rgba(251, 191, 36, 0.14), transparent 26%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(248, 250, 252, 0.94) 100%);
  border-color: rgba(226, 232, 240, 0.92);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.05);
}

.dark .questionnaire-shell {
  background:
    radial-gradient(circle at top right, rgba(250, 204, 21, 0.1), transparent 26%),
    linear-gradient(180deg, rgba(14, 18, 28, 0.96) 0%, rgba(8, 11, 19, 0.96) 100%);
  border-color: rgba(255, 255, 255, 0.08);
}

.toggle-questionnaire {
  @apply inline-flex items-center justify-center gap-2 rounded-2xl border px-4 py-2.5 text-sm font-semibold transition-colors;
  border-color: rgba(79, 70, 229, 0.16);
  color: rgb(79, 70, 229);
  background: rgba(79, 70, 229, 0.08);
}

.toggle-questionnaire:hover {
  background: rgba(79, 70, 229, 0.14);
}

.dark .toggle-questionnaire {
  border-color: rgba(129, 140, 248, 0.18);
  color: rgb(199, 210, 254);
  background: rgba(99, 102, 241, 0.12);
}

.summary-pill {
  @apply inline-flex items-center rounded-full px-3 py-1.5 text-xs font-medium;
  background: rgba(241, 245, 249, 0.95);
  color: rgb(71, 85, 105);
}

.summary-pill-active {
  background: rgba(16, 185, 129, 0.14);
  color: rgb(5, 150, 105);
}

.summary-pill-idle {
  background: rgba(226, 232, 240, 0.88);
  color: rgb(100, 116, 139);
}

.dark .summary-pill {
  background: rgba(255, 255, 255, 0.06);
  color: rgb(203, 213, 225);
}

.dark .summary-pill-active {
  background: rgba(16, 185, 129, 0.16);
  color: rgb(110, 231, 183);
}

.dark .summary-pill-idle {
  background: rgba(255, 255, 255, 0.05);
  color: rgb(148, 163, 184);
}

.questionnaire-expand-enter-active,
.questionnaire-expand-leave-active {
  transition: all 0.24s ease;
}

.questionnaire-expand-enter-from,
.questionnaire-expand-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
