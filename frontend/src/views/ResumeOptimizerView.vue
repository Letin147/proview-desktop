<script setup lang="ts">
import { useResumeStore } from '../stores/resume'
import { useResumeQuestionnaireStore } from '../stores/resumeQuestionnaire'
import ResumeUploader from '../components/resume/ResumeUploader.vue'
import ResumeWorkspace from '../components/resume/ResumeWorkspace.vue'
import CatLoading from '../components/CatLoading.vue'
import { RotateCcw, CheckCircle } from 'lucide-vue-next'

const store = useResumeStore()
const questionnaireStore = useResumeQuestionnaireStore()

function handleReset() {
  store.reset()
  questionnaireStore.reset()
}
</script>

<template>
  <div class="min-h-[80vh]">
    <CatLoading
      v-if="store.phase === 'exporting'"
      variant="corner"
      :blocking="false"
      message="正在导出优化后的简历"
      stage="你仍然可以继续查看当前优化结果"
    />

    <ResumeUploader v-if="store.phase === 'upload' || store.phase === 'analyzing'" />

    <ResumeWorkspace v-else-if="store.phase === 'review' || store.phase === 'exporting'" />

    <div v-else-if="store.phase === 'done'" class="resume-optimizer-done ui-card fade-in">
      <div class="resume-optimizer-done__icon">
        <CheckCircle class="h-8 w-8" />
      </div>
      <span class="ui-section-badge">导出完成</span>
      <h2 class="resume-optimizer-done__title">优化后的简历已导出</h2>
      <p class="resume-optimizer-done__desc">PDF 已下载到本地，你可以继续返回再优化另一份简历。</p>
      <button
        @click="handleReset"
        class="ui-btn ui-btn-primary resume-optimizer-done__action"
      >
        <RotateCcw class="h-4 w-4" />
        优化另一份简历
      </button>
    </div>
  </div>
</template>

<style scoped>
.resume-optimizer-done {
  position: relative;
  display: flex;
  min-height: 80vh;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  overflow: hidden;
  padding: 2rem;
  text-align: center;
}

.resume-optimizer-done::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 22% 20%, rgba(59, 130, 246, 0.12), transparent 28%),
    radial-gradient(circle at 78% 16%, rgba(99, 102, 241, 0.12), transparent 24%),
    linear-gradient(180deg, rgba(59, 130, 246, 0.03), transparent 72%);
  pointer-events: none;
}

.resume-optimizer-done__icon,
.resume-optimizer-done__title,
.resume-optimizer-done__desc,
.resume-optimizer-done__action,
.ui-section-badge {
  position: relative;
  z-index: 1;
}

.resume-optimizer-done__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 5.5rem;
  height: 5.5rem;
  border-radius: 9999px;
  border: 1px solid rgba(16, 185, 129, 0.18);
  background: linear-gradient(180deg, rgba(236, 253, 245, 0.98), rgba(209, 250, 229, 0.92));
  color: #0f766e;
  box-shadow: var(--ui-shadow-sm);
}

.resume-optimizer-done__title {
  font-size: clamp(1.8rem, 2.4vw, 2.3rem);
  font-weight: 900;
  letter-spacing: -0.03em;
  color: var(--ui-text-primary);
}

.resume-optimizer-done__desc {
  max-width: 32rem;
  color: var(--ui-text-secondary);
  line-height: 1.75;
}

.resume-optimizer-done__action {
  min-width: 12rem;
}

:global(html.dark) .resume-optimizer-done__icon {
  border-color: rgba(16, 185, 129, 0.22);
  background: linear-gradient(180deg, rgba(6, 78, 59, 0.42), rgba(6, 95, 70, 0.22));
  color: #6ee7b7;
}
</style>
