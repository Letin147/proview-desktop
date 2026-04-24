<script setup lang="ts">
import { ref } from 'vue'
import { ChevronRight, FilePlus, Upload } from 'lucide-vue-next'
import ResumeImportModal from '../components/resume-builder/ResumeImportModal.vue'
import { useRouter } from 'vue-router'
import { useResumeBuilderStore } from '../stores/resumeBuilder'

const router = useRouter()
const store = useResumeBuilderStore()
const showImportModal = ref(false)

/**
 * 新建空白简历
 */
function createBlankResume() {
  // 清空当前文档，加载默认模板
  store.clearDraft()
  store.loadDraft()  // 加载默认数据
  router.push('/resume-builder')
}

/**
 * 导入现有简历
 */
function openImportModal() {
  showImportModal.value = true
}

/**
 * 导入成功后的回调
 */
function handleImportSuccess() {
  showImportModal.value = false
  // 跳转到编辑器
  router.push('/resume-builder')
}
</script>

<template>
  <div class="resume-entry-page fade-in">
    <section class="resume-entry-hero ui-card">
      <div class="resume-entry-hero__copy">
        <span class="ui-section-badge">简历生成</span>
        <h1 class="ui-page-title mt-4 text-4xl">从草稿到成稿，先选你的起点</h1>
        <p class="ui-page-subtitle mt-3 text-base font-medium">
          你可以直接新建一份空白简历，也可以导入旧简历让 AI 帮你完成内容提取与版式整理。
        </p>
      </div>

      <div class="resume-entry-hero__stats">
        <div class="resume-entry-stat">
          <span class="resume-entry-stat__label">入口数量</span>
          <strong class="resume-entry-stat__value">2</strong>
          <span class="resume-entry-stat__desc">空白创建 / 智能导入</span>
        </div>
        <div class="resume-entry-stat">
          <span class="resume-entry-stat__label">适用方式</span>
          <strong class="resume-entry-stat__value">双路径</strong>
          <span class="resume-entry-stat__desc">新用户和旧简历迁移都能直接开始</span>
        </div>
      </div>
    </section>

    <section class="resume-entry-grid">
      <button type="button" class="resume-entry-card resume-entry-card--primary ui-card ui-card-interactive" @click="createBlankResume">
        <div class="resume-entry-card__head">
          <div class="resume-entry-card__icon resume-entry-card__icon--primary">
            <FilePlus class="h-8 w-8" />
          </div>
          <span class="resume-entry-card__badge">推荐起点</span>
        </div>
        <h3 class="resume-entry-card__title">新建空白简历</h3>
        <p class="resume-entry-card__desc">从零开始搭建内容结构，适合想重新梳理经历、重做表达和版式的人。</p>
        <div class="resume-entry-card__tags">
          <span class="resume-entry-card__tag">快速开始</span>
          <span class="resume-entry-card__tag">模板驱动</span>
          <span class="resume-entry-card__tag">结构可控</span>
        </div>
        <div class="resume-entry-card__foot">
          <span>立即进入编辑器</span>
          <ChevronRight class="h-4 w-4" />
        </div>
      </button>

      <button type="button" class="resume-entry-card resume-entry-card--accent ui-card ui-card-interactive" @click="openImportModal">
        <div class="resume-entry-card__head">
          <div class="resume-entry-card__icon resume-entry-card__icon--accent">
            <Upload class="h-8 w-8" />
          </div>
          <span class="resume-entry-card__badge resume-entry-card__badge--accent">AI 辅助</span>
        </div>
        <h3 class="resume-entry-card__title">导入现有简历</h3>
        <p class="resume-entry-card__desc">上传旧简历后自动抽取内容，再进入编辑器继续改写、优化和重组版面。</p>
        <div class="resume-entry-card__tags">
          <span class="resume-entry-card__tag">智能解析</span>
          <span class="resume-entry-card__tag">自动排版</span>
          <span class="resume-entry-card__tag">迁移旧稿</span>
        </div>
        <div class="resume-entry-card__foot">
          <span>打开导入面板</span>
          <ChevronRight class="h-4 w-4" />
        </div>
      </button>
    </section>

    <!-- 导入弹窗 -->
    <ResumeImportModal
      v-if="showImportModal"
      @success="handleImportSuccess"
      @cancel="showImportModal = false"
    />
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.resume-entry-page {
  min-height: 100%;
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 0 2rem;
}

.resume-entry-hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.75fr);
  gap: 1.25rem;
  padding: 1.8rem;
}

.resume-entry-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 12% 18%, rgba(59, 130, 246, 0.14), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(99, 102, 241, 0.12), transparent 24%),
    linear-gradient(135deg, rgba(59, 130, 246, 0.05), transparent 72%);
  pointer-events: none;
}

.resume-entry-hero__copy,
.resume-entry-hero__stats {
  position: relative;
  z-index: 1;
}

.resume-entry-hero__stats {
  display: grid;
  gap: 0.9rem;
  align-content: end;
}

.resume-entry-stat {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  border-radius: 1.45rem;
  border: 1px solid var(--ui-border-subtle);
  background: var(--ui-surface-raised);
  padding: 1rem 1.05rem;
  box-shadow: var(--ui-shadow-sm);
}

.resume-entry-stat__label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ui-text-muted);
}

.resume-entry-stat__value {
  font-size: 1.55rem;
  font-weight: 900;
  color: var(--ui-text-primary);
}

.resume-entry-stat__desc {
  font-size: 0.82rem;
  line-height: 1.65;
  color: var(--ui-text-secondary);
}

.resume-entry-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.1rem;
  margin-top: 1.25rem;
}

.resume-entry-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 320px;
  padding: 1.55rem;
  text-align: left;
}

.resume-entry-card::before {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.92;
  pointer-events: none;
}

.resume-entry-card--primary::before {
  background:
    radial-gradient(circle at 16% 16%, rgba(59, 130, 246, 0.08), transparent 24%),
    linear-gradient(135deg, rgba(59, 130, 246, 0.02), transparent 70%);
}

.resume-entry-card--accent::before {
  background:
    radial-gradient(circle at 18% 18%, rgba(6, 182, 212, 0.1), transparent 26%),
    radial-gradient(circle at 82% 14%, rgba(99, 102, 241, 0.08), transparent 24%),
    linear-gradient(135deg, rgba(14, 165, 233, 0.04), transparent 72%);
}

.resume-entry-card__head,
.resume-entry-card__title,
.resume-entry-card__desc,
.resume-entry-card__tags,
.resume-entry-card__foot {
  position: relative;
  z-index: 1;
}

.resume-entry-card__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.resume-entry-card__icon {
  display: inline-flex;
  width: 4rem;
  height: 4rem;
  align-items: center;
  justify-content: center;
  border-radius: 1.35rem;
  border: 1px solid var(--ui-border-subtle);
  background: var(--ui-surface-raised);
}

.resume-entry-card__icon--primary {
  color: #325fda;
  background: rgba(59, 130, 246, 0.12);
  border-color: rgba(59, 130, 246, 0.18);
}

.resume-entry-card__icon--accent {
  color: #0f6fc6;
  background: rgba(14, 165, 233, 0.12);
  border-color: rgba(14, 165, 233, 0.2);
}

.resume-entry-card__badge {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  border: 1px solid rgba(99, 102, 241, 0.18);
  background: var(--ui-accent-soft);
  padding: 0.4rem 0.8rem;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ui-accent-strong);
}

.resume-entry-card__badge--accent {
  border-color: rgba(14, 165, 233, 0.2);
  background: rgba(14, 165, 233, 0.1);
  color: #0369a1;
}

.resume-entry-card__title {
  margin-top: 1.4rem;
  font-size: 1.45rem;
  font-weight: 900;
  color: var(--ui-text-primary);
}

.resume-entry-card__desc {
  margin-top: 0.8rem;
  font-size: 0.95rem;
  line-height: 1.75;
  color: var(--ui-text-secondary);
}

.resume-entry-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: auto;
  padding-top: 1.35rem;
}

.resume-entry-card__tag {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  border: 1px solid var(--ui-border-subtle);
  background: var(--ui-surface-3);
  padding: 0.38rem 0.75rem;
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--ui-text-secondary);
}

.resume-entry-card__foot {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 1rem;
  font-size: 0.82rem;
  font-weight: 800;
  color: var(--ui-accent-strong);
}

.dark .resume-entry-hero::before {
  background:
    radial-gradient(circle at 12% 18%, rgba(59, 130, 246, 0.16), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(99, 102, 241, 0.18), transparent 24%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.18), transparent 72%);
}

.dark .resume-entry-stat {
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(255, 255, 255, 0.08);
}

.dark .resume-entry-card__icon {
  background: rgba(15, 23, 42, 0.82);
  border-color: rgba(255, 255, 255, 0.08);
}

.dark .resume-entry-card__badge--accent {
  color: #7dd3fc;
  background: rgba(14, 165, 233, 0.16);
}

@media (max-width: 960px) {
  .resume-entry-hero,
  .resume-entry-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .resume-entry-hero {
    padding: 1.35rem;
  }

  .resume-entry-card {
    min-height: unset;
    padding: 1.25rem;
  }
}
</style>
