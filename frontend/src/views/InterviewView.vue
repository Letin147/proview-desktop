<script lang="ts">
export default { name: 'InterviewView' }
</script>

<script setup lang="ts">
import { ref, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '../stores/interview'
import AiVisualization from '../components/AiVisualization.vue'
import ChatPanel from '../components/ChatPanel.vue'
import CatLoading from '../components/CatLoading.vue'

const router = useRouter()
const store = useInterviewStore()
const aiViz = ref<InstanceType<typeof AiVisualization> | null>(null)
const chatPanel = ref<InstanceType<typeof ChatPanel> | null>(null)
const ending = ref(false)
const endingChoice = ref<'save' | 'discard'>('save')
const showEndDialog = ref(false)
const endError = ref('')

onMounted(async () => {
  if (store.shouldRedirectInterviewToReport) {
    router.replace('/report')
    return
  }

  if (!store.canEnterInterviewRoom) {
    router.replace('/')
    return
  }

  aiViz.value?.startTimer()
})

onActivated(() => {
  if (store.shouldRedirectInterviewToReport) {
    router.replace('/report')
    return
  }

  if (!store.canEnterInterviewRoom) {
    router.replace('/')
    return
  }

  if (store.aiState !== 'idle' && !store.isResponding && !store.isEnding) {
    store.setAiState('idle')
  }
})

async function openEndDialog() {
  chatPanel.value?.stopVoicePlayback()
  aiViz.value?.stopTimer()
  store.setAiState('idle')
  endError.value = ''
  showEndDialog.value = true
}

function closeEndDialog() {
  showEndDialog.value = false
  endError.value = ''
  if (store.canEnterInterviewRoom) {
    aiViz.value?.startTimer()
  }
}

async function confirmEnd(saveHistory: boolean) {
  ending.value = true
  endingChoice.value = saveHistory ? 'save' : 'discard'
  endError.value = ''

  try {
    const result = await store.endSession(saveHistory)
    showEndDialog.value = false
    if (saveHistory && result?.saved !== false) {
      router.push('/report')
      return
    }
    window.alert(result?.message || '本次面试未保存，评估报告不会生成。')
    router.replace('/')
  } catch (error: any) {
    endError.value = error?.message || '结束面试失败，请稍后重试'
    aiViz.value?.startTimer()
  } finally {
    ending.value = false
  }
}
</script>

<template>
  <div class="interview-room relative flex h-[calc(100vh-6rem)] flex-col gap-6 fade-in md:flex-row">
    <CatLoading
      v-if="ending"
      variant="corner"
      :message="endingChoice === 'save' ? '正在保存面试历史并生成评估报告' : '正在结束本次面试'"
      :stage="store.thinkingStage"
      :thinking-text="store.thinkingText"
    />

    <AiVisualization ref="aiViz" @end-interview="openEndDialog" />
    <ChatPanel ref="chatPanel" />

    <div v-if="showEndDialog" class="interview-end-shell absolute inset-0 z-30 flex items-center justify-center px-4">
      <div class="interview-end-card ui-card w-full max-w-lg p-6">
        <h3 class="text-xl font-bold text-slate-900 dark:text-white">结束面试</h3>
        <p class="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">
          你可以选择保存本次面试历史，保存后才会生成评估报告；如果不保存，本次对话和报告都会被释放，不占用数据库空间。
        </p>

        <div class="interview-end-note ui-card-soft mt-4 px-4 py-3 text-sm text-slate-600 dark:text-slate-300">
          保存本次面试后会继续生成评估报告并跳转到报告页；不保存则直接结束本次面试，不保留报告内容。
        </div>

        <p v-if="endError" class="mt-3 text-sm text-rose-500">{{ endError }}</p>

        <div class="mt-6 flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            class="interview-end-btn interview-end-btn--ghost flex-1"
            @click="closeEndDialog"
          >
            继续面试
          </button>
          <button
            type="button"
            class="interview-end-btn interview-end-btn--danger flex-1"
            @click="confirmEnd(false)"
          >
            不保存，直接结束
          </button>
          <button
            type="button"
            class="interview-end-btn interview-end-btn--primary flex-1 disabled:cursor-not-allowed disabled:opacity-50"
            @click="confirmEnd(true)"
          >
            保存并生成报告
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.interview-room {
  isolation: isolate;
}

.interview-end-shell {
  background: rgba(5, 10, 20, 0.36);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.interview-end-card {
  position: relative;
  overflow: hidden;
}

.interview-end-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 16% 14%, rgba(59, 130, 246, 0.1), transparent 26%),
    radial-gradient(circle at 84% 18%, rgba(99, 102, 241, 0.1), transparent 22%);
  pointer-events: none;
}

.interview-end-note {
  background: var(--ui-surface-3);
}

.interview-end-btn {
  border-radius: 1rem;
  border: 1px solid var(--ui-border-default);
  padding: 0.9rem 1rem;
  font-size: 0.9rem;
  font-weight: 700;
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    color 180ms ease,
    box-shadow 180ms ease;
}

.interview-end-btn--ghost {
  background: var(--ui-surface-raised);
  color: var(--ui-text-secondary);
}

.interview-end-btn--ghost:hover {
  border-color: var(--ui-border-strong);
  color: var(--ui-text-primary);
  background: var(--ui-surface-1);
}

.interview-end-btn--danger {
  border-color: rgba(244, 63, 94, 0.22);
  background: var(--ui-danger-soft);
  color: var(--ui-danger);
}

.interview-end-btn--danger:hover {
  background: rgba(244, 63, 94, 0.18);
}

.interview-end-btn--primary {
  border-color: rgba(59, 130, 246, 0.2);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.94), rgba(79, 70, 229, 0.94));
  color: white;
  box-shadow: var(--ui-shadow-accent);
}

.interview-end-btn--primary:hover {
  box-shadow: var(--ui-shadow-accent-hover);
  filter: brightness(1.02);
}
</style>
