<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import type { InterviewConfig } from '../types'
import { Play, Volume2, Loader, Upload, Cpu, FileCheck, RefreshCw } from 'lucide-vue-next'
import CatLoading from '../components/CatLoading.vue'
import CustomSelect from '../components/CustomSelect.vue'
import JobTagPicker from '../components/JobTagPicker.vue'
import { ttsPreview, fetchLatestResume } from '../services/interview'
import { isReusableOcrText } from '../utils/ocr'

const router = useRouter()
const store = useInterviewStore()
const loading = computed(() => store.isSettingUp)

// ===== 配置选项定义 =====
const styleOptions = [
  { value: 'default', label: '标准模式', desc: '专业均衡，客观评估', emoji: '📘' },
  { value: 'strict', label: '高压模式', desc: '追问更深，要求更高', emoji: '🎯' },
  { value: 'friendly', label: '温和引导', desc: '更适合练习和热身', emoji: '🌤' },
  { value: 'technical_deep', label: '技术深挖', desc: '关注原理和实现细节', emoji: '🧠' },
  { value: 'behavioral', label: '行为面试', desc: '聚焦经历表达与 STAR', emoji: '🗣' },
  { value: 'system_design', label: '系统设计', desc: '考察架构设计与权衡', emoji: '🏗' },
  { value: 'rapid_fire', label: '快问快答', desc: '强调知识广度和反应速度', emoji: '⚡' },
  { value: 'project_focused', label: '项目追问', desc: '重点深挖项目细节', emoji: '📂' },
]

const typeOptions = [
  { value: 'technical', label: '技术面', desc: '代码能力与技术深度', emoji: '💻' },
  { value: 'hr', label: 'HR面', desc: '职业动机与稳定性', emoji: '🤝' },
  { value: 'manager', label: '主管面', desc: '业务理解与协作能力', emoji: '📋' },
]

const difficultyOptions = [
  { value: 'junior', label: '初级', desc: '基础概念与常见实践', emoji: '🌱' },
  { value: 'mid', label: '中级', desc: '实战经验与原理理解', emoji: '🚀' },
  { value: 'senior', label: '高级', desc: '架构能力与系统思考', emoji: '🧭' },
]
const voiceOptions = [
  { value: 4100, label: '度小雯（臻品女声）' },
  { value: 4117, label: '度小鹿（臻品女声）' },
  { value: 4115, label: '度小贤（臻品男声）' },
  { value: 4003, label: '度逍遥（臻品男声）' },
  { value: 4106, label: '度博文（新闻男声）' },
  { value: 5003, label: '度逍遥（精品男声）' },
  { value: 0, label: '度小美（基础女声）' },
  { value: 1, label: '度小宇（基础男声）' },
]

const speedOptions = [
  { label: '0.5x', spd: 2 },
  { label: '0.75x', spd: 3 },
  { label: '1x', spd: 5 },
  { label: '1.25x', spd: 7 },
  { label: '1.5x', spd: 9 },
  { label: '2x', spd: 12 },
]

const PREVIEW_TEXT = '你好，我是你的AI面试官，准备好开始面试了吗？'

const modelOptions = [
  { value: 'deepseek', label: 'DeepSeek', desc: '深度求索，代码能力强', emoji: '🧠' },
  { value: 'ernie', label: '文心一言', desc: '百度大模型，中文理解优秀', emoji: '🌐' },
  { value: 'ernie-thinking', label: '文心（深度思考）', desc: '开启思维链，回复更慢但更深入', emoji: '🔮' },
  // { value: 'deepseek-reasoner', label: 'DeepSeek R1', desc: '推理模型，逻辑分析强', emoji: '⚡' },
]

// 语音试听
const previewPlaying = ref(false)
const previewLoading = ref(false)
let previewAudioCtx: AudioContext | null = null
let previewSource: AudioBufferSourceNode | null = null

function stopPreview() {
  if (previewSource) {
    try { previewSource.stop() } catch { /* already stopped */ }
    previewSource = null
  }
  previewPlaying.value = false
}

async function playPreview() {
  if (previewPlaying.value) { stopPreview(); return }
  previewLoading.value = true
  try {
    const wavBuffer = await ttsPreview(PREVIEW_TEXT, store.config.voicePer, store.config.voiceSpd)
    if (!previewAudioCtx) previewAudioCtx = new AudioContext()
    const audioBuf = await previewAudioCtx.decodeAudioData(wavBuffer)
    stopPreview()
    previewSource = previewAudioCtx.createBufferSource()
    previewSource.buffer = audioBuf
    previewSource.connect(previewAudioCtx.destination)
    previewSource.onended = () => { previewPlaying.value = false }
    previewSource.start()
    previewPlaying.value = true
  } catch (e: any) {
    console.error('试听失败:', e)
    console.error('试听失败:', e)
    alert('语音试听失败，请确保后端已启动')
  } finally {
    previewLoading.value = false
  }
}

function setStyle(val: string) { store.config.style = val as InterviewConfig['style'] }

function buildStartInterviewErrorMessage(error: unknown): string {
  const message = error instanceof Error ? error.message.trim() : String(error || '').trim()
  if (!message || message === '[object Object]') {
    return '服务连接失败，请确保 Flask 后端已启动。'
  }
  if (/Failed to fetch|NetworkError|Load failed|ERR_CONNECTION_REFUSED/i.test(message)) {
    return '服务连接失败，请确保 Flask 后端已启动。'
  }
  return `面试启动失败：${message}`
}

async function startInterview() {
  if (!store.config.jobTitle.trim()) { alert('请输入目标岗位'); return }
  try {
    await store.startInterview()
    router.push('/interview')
  } catch (e: any) {
    alert(buildStartInterviewErrorMessage(e))
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  store.setUploadedResume(input.files?.[0] || null)
}

function clearHistoryResume() {
  store.clearResumeSelection()
}

// 进入配置页时，自动加载用户最近的简历（如果当前没有已加载的简历）
onMounted(async () => {
  if (store.config.resumeSelection === 'none') return
  if (store.config.resumeFile || store.config.resumeOcrText) return
  try {
    const resume = await fetchLatestResume()
    const latestOcrText = resume?.ocr_result || ''
    if (isReusableOcrText(latestOcrText)) {
      store.setReusedResume(latestOcrText, {
        fileName: resume?.file_name || '历史简历',
        sourceSessionId: resume?.session_id,
        selection: 'auto-latest',
      })
    }
  } catch { /* 静默 */ }
})
</script>

<template>
  <div class="setup-page fade-in min-h-full max-w-5xl mx-auto">
    <CatLoading
      v-if="loading"
      variant="corner"
      message="AI 面试官正在准备中"
      :stage="store.thinkingStage"
      :thinking-text="store.thinkingText"
    />

    <section class="setup-hero ui-card mb-8">
      <div class="relative z-[1] min-w-0 flex-1">
        <span class="ui-section-badge">面试配置</span>
        <h2 class="ui-page-title mt-4 text-3xl sm:text-4xl">配置专属面试房间</h2>
        <p class="ui-page-subtitle mt-3 max-w-2xl text-sm font-medium leading-6">
          保留当前面试流程与逻辑，只将配置页升级为更完整的渐变、玻璃和卡片层次，让模型、简历、题型和语音设置更清晰。
        </p>
      </div>
      <div class="setup-hero__stats relative z-[1] grid shrink-0 grid-cols-2 gap-3">
        <div class="setup-stat-card">
          <p class="setup-stat-card__label">预设风格</p>
          <p class="setup-stat-card__value">{{ styleOptions.length }}</p>
        </div>
        <div class="setup-stat-card">
          <p class="setup-stat-card__label">面试轮次</p>
          <p class="setup-stat-card__value">{{ typeOptions.length }}</p>
        </div>
      </div>
    </section>

    <div
      v-if="false && loading"
      class="mb-6 rounded-3xl border border-indigo-200 bg-white/90 p-5 shadow-lg shadow-indigo-100/60 backdrop-blur dark:border-indigo-500/20 dark:bg-slate-950/80 dark:shadow-transparent"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div class="min-w-0">
          <div class="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-white">
            <Loader class="h-4 w-4 animate-spin text-primary" />
            AI 面试官正在准备中
          </div>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            初始化过程已经改成局部加载，你仍然可以继续查看和调整表单；如果想切换配置，可以直接取消本次初始化。          </p>
          <p v-if="store.thinkingStage" class="mt-3 text-xs font-medium text-primary">{{ store.thinkingStage }}</p>
        </div>
        <button
          type="button"
          @click="store.cancelSetup"
          class="inline-flex shrink-0 items-center justify-center rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-red-300 hover:text-red-500 dark:border-white/10 dark:text-slate-300 dark:hover:border-red-500/30 dark:hover:text-red-400"
        >
          取消初始化        </button>
      </div>

      <div
        v-if="store.thinkingText"
        class="mt-4 max-h-48 overflow-y-auto rounded-2xl bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-600 dark:bg-white/5 dark:text-slate-300"
      >
        {{ store.thinkingText }}
      </div>
    </div>

    <form @submit.prevent="startInterview" class="setup-form space-y-6">

      <!-- 第一行：大模型 + 简历 -->
      <section class="setup-section">
        <div class="setup-section__head">
          <span class="ui-section-badge"><Cpu class="h-3.5 w-3.5" /> 模型与简历</span>
          <p class="setup-section__hint">先确定提问引擎，再决定 AI 可参考的候选人信息。</p>
        </div>
        <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div class="config-card setup-card setup-card--blue">
          <label class="config-label"><Cpu class="w-3.5 h-3.5 inline -mt-0.5" /> AI 大模型</label>
          <div class="flex flex-wrap gap-2">
            <button v-for="m in modelOptions" :key="m.value" type="button"
              @click="store.config.modelProvider = m.value"
              class="chip-btn" :class="store.config.modelProvider === m.value ? 'chip-active' : 'chip-idle'">
              <span>{{ m.emoji }}</span> {{ m.label }}
            </button>
          </div>
          <p class="text-helper mt-1">{{ modelOptions.find(m => m.value === store.config.modelProvider)?.desc }}</p>
        </div>
        <div class="config-card setup-card setup-card--rose">
          <label class="config-label">
            <Upload class="w-3.5 h-3.5 inline -mt-0.5" /> 上传简历
            <span class="text-helper font-normal ml-1">PDF / Word(.docx) / Markdown / TXT / 图片</span>
          </label>
          <!-- 已加载历史简历 -->
          <div v-if="store.config.resumeOcrText && !store.config.resumeFile" class="flex items-center gap-3">
            <div class="setup-file-state flex-1 min-w-0 flex items-center gap-2 px-3 py-2.5 rounded-2xl">
              <FileCheck class="w-4 h-4 text-green-600 dark:text-green-400 shrink-0" />
              <span class="text-sm text-green-700 dark:text-green-400 truncate">已加载: {{ store.config.resumeFileName || '历史简历' }}</span>
            </div>
            <button type="button" @click="clearHistoryResume"
              class="ui-btn ui-btn-secondary shrink-0 px-3 py-2.5 text-xs font-medium whitespace-nowrap">
              <RefreshCw class="w-3.5 h-3.5" /> 改为上传其他简历
            </button>
          </div>
          <!-- 正常文件上传 -->
          <input v-else type="file" accept=".pdf,.docx,.md,.markdown,.txt,.png,.jpg,.jpeg,.bmp,.webp,.heic,.heif" @change="onFileChange"
            class="setup-file-input w-full text-sm cursor-pointer" />
        </div>
        </div>
      </section>

      <!-- 目标岗位（独占一行，标签默认展开） -->
      <section class="setup-section">
        <div class="setup-section__head">
          <span class="ui-section-badge">岗位画像</span>
          <p class="setup-section__hint">岗位标签和 JD 决定追问维度与评分基准。</p>
        </div>
        <div class="config-card setup-card">
        <label class="config-label">目标岗位</label>
        <JobTagPicker v-model="store.config.jobTitle" :default-expanded="true" />
        </div>

      <div class="config-card setup-card">
        <label class="config-label">岗位要求 / 职位描述（可选）</label>
        <textarea
          v-model="store.config.jobRequirements"
          class="config-input min-h-[140px] resize-y"
          placeholder="可粘贴岗位职责、技术栈要求、年限要求、加分项等。AI 会把这部分作为考察重点和评分基准，不会当成候选人已经具备的经历。"
        />
        <p class="text-helper mt-2">建议直接粘贴 JD 原文，尤其是核心职责、必备技能、经验年限和加分项。</p>
      </div>
      </section>

      <!-- 第二行：面试轮次 + 难度 -->
      <section class="setup-section">
        <div class="setup-section__head">
          <span class="ui-section-badge">面试编排</span>
          <p class="setup-section__hint">轮次、难度和面试风格共同决定提问节奏与压迫感。</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="config-card setup-card setup-card--violet">
          <label class="config-label">面试轮次</label>
          <div class="flex flex-wrap gap-2">
            <button v-for="t in typeOptions" :key="t.value" type="button"
              @click="store.config.interviewType = t.value"
              class="chip-btn" :class="store.config.interviewType === t.value ? 'chip-active' : 'chip-idle'">
              <span>{{ t.emoji }}</span> {{ t.label }}
            </button>
          </div>
          <p class="text-helper mt-1">{{ typeOptions.find(t => t.value === store.config.interviewType)?.desc }}</p>
        </div>
        <div class="config-card setup-card setup-card--amber">
          <label class="config-label">难度级别</label>
          <div class="flex flex-wrap gap-2">
            <button v-for="d in difficultyOptions" :key="d.value" type="button"
              @click="store.config.difficulty = d.value"
              class="chip-btn" :class="store.config.difficulty === d.value ? 'chip-active' : 'chip-idle'">
              <span>{{ d.emoji }}</span> {{ d.label }}
            </button>
          </div>
          <p class="text-helper mt-1">{{ difficultyOptions.find(d => d.value === store.config.difficulty)?.desc }}</p>
        </div>
        </div>

      <!-- 第三行：面试风格（卡片网格） -->
      <div class="config-card setup-card">
        <label class="config-label">面试风格</label>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          <button v-for="s in styleOptions" :key="s.value" type="button"
            @click="setStyle(s.value)"
            class="style-card-btn"
            :class="store.config.style === s.value ? 'style-card-active' : 'style-card-idle'">
            <div class="text-lg mb-1">{{ s.emoji }}</div>
            <div class="style-card-title">{{ s.label }}</div>
            <div class="style-card-desc">{{ s.desc }}</div>
          </button>
        </div>
      </div>
      </section>

      <!-- 第四行：功能开关 -->
      <section class="setup-section">
        <div class="setup-section__head">
          <span class="ui-section-badge"><Volume2 class="h-3.5 w-3.5" /> 训练与语音</span>
          <p class="setup-section__hint">功能开关、音色与语速全部保留原交互，只统一视觉表达。</p>
        </div>
        <div class="config-card setup-card">
        <label class="config-label">训练功能</label>
        <div class="flex flex-wrap gap-4">
          <label class="setup-toggle inline-flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" v-model="store.config.featureDeep"
              class="w-4 h-4 rounded border-slate-300 text-primary focus:ring-2 focus:ring-indigo-500/30" />
            <span class="text-secondary-label">🔍 简历压力深挖</span>
            <span class="text-helper">连环追问，识别注水</span>
          </label>
          <label class="setup-toggle inline-flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" v-model="store.config.featureVad"
              class="w-4 h-4 rounded border-slate-300 text-primary focus:ring-2 focus:ring-indigo-500/30" />
            <span class="text-secondary-label">🆘 柔性防卡壳</span>
            <span class="text-helper">卡壳时给予提示引导</span>
          </label>
        </div>
      </div>

      <!-- 第五行：语音设置 -->
      <div class="config-card setup-card">
        <label class="config-label"><Volume2 class="w-3.5 h-3.5 inline -mt-0.5" /> AI 面试官语音</label>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span class="text-helper block mb-1.5">音色</span>
            <CustomSelect
              v-model="store.config.voicePer"
              :options="voiceOptions"
              placeholder="选择音色"
            />
          </div>
          <div>
            <span class="text-helper block mb-1.5">语速</span>
            <div class="flex gap-1.5 flex-wrap">
              <button v-for="s in speedOptions" :key="s.spd" type="button" @click="store.config.voiceSpd = s.spd"
                class="chip-btn text-xs" :class="store.config.voiceSpd === s.spd ? 'chip-active' : 'chip-idle'">
                {{ s.label }}
              </button>
            </div>
          </div>
        </div>
        <button type="button" @click="playPreview" :disabled="previewLoading"
          class="setup-preview-btn mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all disabled:opacity-50 border"
          :class="previewPlaying
            ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200 dark:border-red-500/30'
            : 'bg-indigo-50 dark:bg-primary/5 text-indigo-600 dark:text-indigo-400 border-indigo-200 dark:border-indigo-500/30 hover:bg-indigo-100 dark:hover:bg-primary/10 dark:hover:border-indigo-400/50'">
          <Loader v-if="previewLoading" class="w-4 h-4 animate-spin" />
          <Volume2 v-else class="w-4 h-4" />
          {{ previewLoading ? '加载中...' : previewPlaying ? '停止试听' : '试听当前语音' }}
        </button>
      </div>
      </section>

      <!-- 开始按钮 -->
      <section class="setup-submit ui-card">
        <div class="setup-submit__copy">
          <h3 class="text-lg font-extrabold text-slate-900 dark:text-white">准备开始沉浸式面试</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">
            所有配置和按钮行为都沿用当前产品逻辑。开始后会按照现有流程初始化房间；如果已选择简历，则会继续按原流程解析并进入面试界面。
          </p>
        </div>
        <button type="submit" :disabled="loading"
          class="setup-cta w-full text-white font-bold py-4 rounded-2xl transition-all flex items-center justify-center gap-2 disabled:opacity-50">
          <Play class="w-5 h-5 relative z-[1]" />
          <span class="relative z-[1]">{{ loading ? '系统初始化中...' : '开始沉浸式面试' }}</span>
          <span class="setup-cta__glow" aria-hidden="true"></span>
          <span class="setup-cta__shine" aria-hidden="true"></span>
        </button>
        <button
          v-if="loading"
          type="button"
          @click="store.cancelSetup"
          class="ui-btn ui-btn-secondary w-full py-3"
        >
          取消当前初始化
        </button>
      </section>
    </form>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.setup-page {
  padding-bottom: 1rem;
}

.setup-hero {
  position: relative;
  display: flex;
  gap: 1.5rem;
  align-items: stretch;
  justify-content: space-between;
  padding: 1.75rem;
  overflow: hidden;
}

.setup-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.12), transparent 30%),
    radial-gradient(circle at 88% 12%, rgba(244, 114, 182, 0.12), transparent 28%),
    linear-gradient(135deg, rgba(255, 248, 238, 0.4), rgba(239, 246, 255, 0.18));
  pointer-events: none;
}

.setup-hero__stats {
  min-width: 200px;
}

.setup-stat-card {
  padding: 1rem 1.1rem;
  border-radius: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.55);
  background: rgba(255, 255, 255, 0.66);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.setup-stat-card__label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #94a3b8;
}

.setup-stat-card__value {
  margin-top: 0.55rem;
  font-size: 2rem;
  line-height: 1;
  font-weight: 900;
  letter-spacing: -0.04em;
  color: #1e293b;
}

.setup-section__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.setup-section__hint {
  font-size: 0.82rem;
  font-weight: 500;
  color: #64748b;
}

.config-card {
  @apply rounded-[26px] border p-5 transition-all;
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.86) 0%, rgba(248, 250, 252, 0.94) 100%);
  border-color: rgba(226, 232, 240, 0.92);
  box-shadow:
    0 18px 42px rgba(15, 23, 42, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.config-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 240ms ease;
  pointer-events: none;
}

.setup-card--blue::before {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), transparent 62%);
}

.setup-card--rose::before {
  background: linear-gradient(135deg, rgba(244, 114, 182, 0.1), transparent 62%);
}

.setup-card--violet::before {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), transparent 62%);
}

.setup-card--amber::before {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.12), transparent 62%);
}

.config-card:hover {
  transform: translateY(-2px);
  border-color: rgba(129, 140, 248, 0.34);
  box-shadow: 0 24px 48px rgba(79, 70, 229, 0.1);
}

.config-card:hover::before {
  opacity: 1;
}

.config-label {
  @apply block text-sm font-bold mb-3;
  position: relative;
  z-index: 1;
  color: #334155;
}

.config-input {
  @apply w-full px-4 py-3 rounded-2xl border outline-none transition-all;
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.82);
  border-color: rgba(203, 213, 225, 0.92);
  color: #0f172a;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.config-input::placeholder {
  color: #94a3b8;
}

.config-input:focus {
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.48);
}

.chip-btn {
  @apply px-3 py-2 rounded-2xl border text-sm font-medium transition-all inline-flex items-center gap-1.5;
  position: relative;
  z-index: 1;
}

.chip-active {
  border-color: rgba(99, 102, 241, 0.4);
  color: #4338ca;
  background:
    linear-gradient(135deg, rgba(224, 231, 255, 0.92), rgba(239, 246, 255, 0.82), rgba(252, 231, 243, 0.72));
  box-shadow: 0 12px 24px rgba(99, 102, 241, 0.12);
}

.chip-idle {
  border-color: rgba(226, 232, 240, 0.92);
  color: #475569;
  background: rgba(255, 255, 255, 0.72);
}

.chip-idle:hover {
  transform: translateY(-1px);
  border-color: rgba(129, 140, 248, 0.3);
  background: rgba(255, 255, 255, 0.9);
}

.style-card-btn {
  @apply rounded-2xl border p-3 text-left transition-all;
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.68);
  border-color: rgba(226, 232, 240, 0.9);
}

.style-card-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 220ms ease;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(139, 92, 246, 0.12), rgba(244, 114, 182, 0.1));
  pointer-events: none;
}

.style-card-active {
  border-color: rgba(99, 102, 241, 0.42);
  box-shadow:
    0 0 0 1px rgba(129, 140, 248, 0.22),
    0 16px 30px rgba(99, 102, 241, 0.1);
}

.style-card-active::before,
.style-card-btn:hover::before {
  opacity: 1;
}

.style-card-idle:hover {
  transform: translateY(-2px);
  border-color: rgba(129, 140, 248, 0.32);
  background: rgba(255, 255, 255, 0.9);
}

.style-card-title {
  @apply text-sm font-bold;
  position: relative;
  color: #334155;
}

.style-card-desc {
  @apply text-xs mt-0.5;
  position: relative;
  color: #94a3b8;
}

.setup-file-state {
  border: 1px solid rgba(16, 185, 129, 0.26);
  background: rgba(236, 253, 245, 0.9);
}

.setup-file-input {
  color: #64748b;
}

.setup-file-input::file-selector-button {
  margin-right: 0.75rem;
  padding: 0.7rem 1rem;
  border: 0;
  border-radius: 9999px;
  font-size: 0.84rem;
  font-weight: 700;
  color: #4338ca;
  background: rgba(99, 102, 241, 0.1);
  transition: background-color 180ms ease;
}

.setup-file-input:hover::file-selector-button {
  background: rgba(99, 102, 241, 0.18);
}

.setup-toggle {
  padding: 0.75rem 0.9rem;
  border-radius: 1rem;
  border: 1px solid rgba(226, 232, 240, 0.82);
  background: rgba(255, 255, 255, 0.66);
}

.setup-preview-btn {
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.08);
}

.setup-submit {
  position: relative;
  overflow: hidden;
  padding: 1.5rem;
}

.setup-submit::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 12% 12%, rgba(56, 189, 248, 0.1), transparent 24%),
    radial-gradient(circle at 88% 18%, rgba(244, 114, 182, 0.1), transparent 24%);
  pointer-events: none;
}

.setup-submit__copy {
  position: relative;
  z-index: 1;
  margin-bottom: 1rem;
}

.setup-cta {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.35);
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
  box-shadow:
    0 20px 44px rgba(59, 130, 246, 0.22),
    0 12px 28px rgba(236, 72, 153, 0.18);
}

.setup-cta:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow:
    0 24px 48px rgba(59, 130, 246, 0.26),
    0 14px 30px rgba(236, 72, 153, 0.2);
}

.setup-cta__glow {
  position: absolute;
  inset: -30%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.24), transparent 55%);
  opacity: 0.42;
  animation: setup-cta-breathe 3.2s ease-in-out infinite;
}

.setup-cta__shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(110deg, transparent 0%, rgba(255, 255, 255, 0.42) 46%, transparent 72%);
  transform: translateX(-140%);
  animation: setup-cta-shine 4.2s ease-in-out infinite;
}

@keyframes setup-cta-breathe {
  0%,
  100% {
    transform: scale(0.94);
    opacity: 0.34;
  }
  50% {
    transform: scale(1.02);
    opacity: 0.56;
  }
}

@keyframes setup-cta-shine {
  0% {
    transform: translateX(-140%);
  }
  50%,
  100% {
    transform: translateX(140%);
  }
}

.text-helper {
  @apply text-xs;
  position: relative;
  z-index: 1;
  color: #94a3b8;
}

.text-secondary-label {
  @apply text-sm;
  position: relative;
  z-index: 1;
  color: #475569;
}

select.config-input {
  @apply dark:[&>option]:bg-slate-900;
}

.dark .setup-hero::before {
  background:
    radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.14), transparent 30%),
    radial-gradient(circle at 88% 12%, rgba(244, 114, 182, 0.12), transparent 28%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.24), rgba(49, 46, 129, 0.18));
}

.dark .setup-stat-card {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
}

.dark .setup-stat-card__label,
.dark .setup-section__hint,
.dark .text-helper {
  color: #94a3b8;
}

.dark .setup-stat-card__value,
.dark .config-label,
.dark .style-card-title {
  color: rgba(255, 255, 255, 0.96);
}

.dark .config-card {
  background:
    linear-gradient(180deg, rgba(12, 15, 23, 0.9) 0%, rgba(10, 12, 20, 0.94) 100%);
  border-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.28);
}

.dark .config-card:hover {
  border-color: rgba(129, 140, 248, 0.24);
  box-shadow: 0 24px 42px rgba(0, 0, 0, 0.38);
}

.dark .config-input,
.dark .style-card-btn,
.dark .chip-idle,
.dark .setup-toggle {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.88);
}

.dark .config-input::placeholder,
.dark .style-card-desc {
  color: rgba(255, 255, 255, 0.38);
}

.dark .config-input:focus {
  border-color: rgba(129, 140, 248, 0.5);
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.18);
}

.dark .chip-active {
  color: #c4b5fd;
  border-color: rgba(129, 140, 248, 0.42);
  background: linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(67, 56, 202, 0.32), rgba(131, 24, 67, 0.24));
}

.dark .chip-idle:hover,
.dark .style-card-idle:hover {
  border-color: rgba(129, 140, 248, 0.3);
  background: rgba(255, 255, 255, 0.07);
}

.dark .style-card-active {
  border-color: rgba(129, 140, 248, 0.42);
  box-shadow: 0 0 0 1px rgba(129, 140, 248, 0.18);
}

.dark .text-secondary-label {
  color: #cbd5e1;
}

.dark .setup-file-state {
  border-color: rgba(16, 185, 129, 0.24);
  background: rgba(6, 78, 59, 0.24);
}

.dark .setup-file-input {
  color: #94a3b8;
}

.dark .setup-file-input::file-selector-button {
  color: #c4b5fd;
  background: rgba(99, 102, 241, 0.18);
}

.dark .setup-submit::before {
  background:
    radial-gradient(circle at 12% 12%, rgba(56, 189, 248, 0.12), transparent 24%),
    radial-gradient(circle at 88% 18%, rgba(244, 114, 182, 0.12), transparent 24%);
}

@media (max-width: 767px) {
  .setup-hero {
    flex-direction: column;
  }

  .setup-hero__stats {
    min-width: 0;
  }
}
</style>
