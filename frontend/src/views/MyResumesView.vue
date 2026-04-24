<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import {
  ChevronLeft,
  ChevronRight,
  Copy,
  Download,
  ExternalLink,
  Eye,
  FileText,
  FileUser,
  FolderOpen,
  Loader,
  RotateCcw,
  Trash2,
  X,
  ZoomIn,
  ZoomOut,
} from 'lucide-vue-next'
import {
  deleteMyResume,
  fetchMyResumes,
  getResumeFileUrl,
  getResumePreviewUrl,
  type ResumeRecord,
} from '../services/interview'

const resumes = ref<ResumeRecord[]>([])
const loading = ref(true)
const deletingId = ref<number | null>(null)
const previewResume = ref<ResumeRecord | null>(null)
const previewPage = ref(0)
const previewZoom = ref(1)
const isDesktop = typeof window !== 'undefined' && Boolean(window.proviewDesktop?.isDesktop)

const PREVIEW_MIN_ZOOM = 1
const PREVIEW_MAX_ZOOM = 3
const PREVIEW_ZOOM_STEP = 0.25

async function loadResumes() {
  loading.value = true
  try {
    resumes.value = await fetchMyResumes()
  } finally {
    loading.value = false
  }
}

onMounted(loadResumes)

const previewableCount = computed(() => resumes.value.filter(record => record.can_preview !== false).length)

const previewImages = computed(() => {
  const resume = previewResume.value
  if (!resume || resume.can_preview === false) return []
  if (resume.preview_image_urls?.length) return resume.preview_image_urls
  return [getResumePreviewUrl(resume.id, 1)]
})

const activePreviewUrl = computed(() => previewImages.value[previewPage.value] || '')
const previewZoomed = computed(() => previewZoom.value > PREVIEW_MIN_ZOOM)
const previewZoomPercent = computed(() => Math.round(previewZoom.value * 100))

function formatTime(value: string) {
  if (!value) return '未知时间'
  try {
    const date = new Date(value)
    return `${date.toLocaleDateString('zh-CN')} ${date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })}`
  } catch {
    return value
  }
}

function formatKind(record: ResumeRecord) {
  switch (record.file_kind) {
    case 'pdf':
      return 'PDF'
    case 'docx':
      return 'Word'
    case 'doc':
      return 'DOC'
    case 'image':
      return '图片'
    default:
      return '文件'
  }
}

function previewPageLabel(record: ResumeRecord) {
  const count = record.preview_page_count || 0
  if (record.can_preview === false) return '暂无预览'
  if (count <= 1) return `${formatKind(record)} 预览`
  return `${count} 页预览`
}

function previewCover(record: ResumeRecord) {
  if (record.can_preview === false) return ''
  return record.preview_cover_url || getResumePreviewUrl(record.id, 1)
}

function getPath(record: ResumeRecord) {
  return record.file_path?.trim() || ''
}

function getDisplayPath(record: ResumeRecord) {
  return getPath(record) || '未记录本地存储路径'
}

async function copyText(text: string, successMessage: string) {
  if (!text) {
    alert('当前简历没有可复制的路径。')
    return
  }

  try {
    await navigator.clipboard.writeText(text)
    alert(successMessage)
  } catch {
    window.prompt('请复制以下路径', text)
  }
}

async function handleCopyPath(record: ResumeRecord) {
  await copyText(getPath(record), '路径已复制到剪贴板。')
}

async function handleLocate(record: ResumeRecord) {
  const filePath = getPath(record)
  if (!filePath) {
    alert('当前简历没有记录本地存储路径。')
    return
  }

  const result = await window.proviewDesktop?.locateFile?.(filePath)
  if (!result?.ok) {
    alert(result?.error || '定位文件失败，请稍后重试。')
  }
}

async function handleOpen(record: ResumeRecord) {
  const filePath = getPath(record)
  if (!filePath) {
    alert('当前简历没有记录本地存储路径。')
    return
  }

  const result = await window.proviewDesktop?.openFile?.(filePath)
  if (!result?.ok) {
    alert(result?.error || '打开文件失败，请稍后重试。')
  }
}

function openPreview(record: ResumeRecord) {
  if (record.can_preview === false) return
  previewResume.value = record
  previewPage.value = 0
  previewZoom.value = PREVIEW_MIN_ZOOM
}

function closePreview() {
  previewResume.value = null
  previewPage.value = 0
  previewZoom.value = PREVIEW_MIN_ZOOM
}

function selectPreviewPage(index: number) {
  previewPage.value = index
  previewZoom.value = PREVIEW_MIN_ZOOM
}

function previousPage() {
  if (!previewImages.value.length) return
  previewPage.value = previewPage.value === 0 ? previewImages.value.length - 1 : previewPage.value - 1
  previewZoom.value = PREVIEW_MIN_ZOOM
}

function nextPage() {
  if (!previewImages.value.length) return
  previewPage.value = previewPage.value === previewImages.value.length - 1 ? 0 : previewPage.value + 1
  previewZoom.value = PREVIEW_MIN_ZOOM
}

function zoomInPreview() {
  previewZoom.value = Math.min(PREVIEW_MAX_ZOOM, +(previewZoom.value + PREVIEW_ZOOM_STEP).toFixed(2))
}

function zoomOutPreview() {
  previewZoom.value = Math.max(PREVIEW_MIN_ZOOM, +(previewZoom.value - PREVIEW_ZOOM_STEP).toFixed(2))
}

function resetPreviewZoom() {
  previewZoom.value = PREVIEW_MIN_ZOOM
}

function togglePreviewZoom() {
  previewZoom.value = previewZoomed.value ? PREVIEW_MIN_ZOOM : 2
}

async function handleDelete(record: ResumeRecord) {
  const confirmed = window.confirm(`确定删除简历《${record.file_name}》吗？删除后会同时清理这份本地文件及其派生资源。`)
  if (!confirmed) return

  deletingId.value = record.id
  try {
    await deleteMyResume(record.id)
    resumes.value = resumes.value.filter((item) => item.id !== record.id)
    if (previewResume.value?.id === record.id) {
      closePreview()
    }
  } catch (error: any) {
    alert(error?.response?.data?.message || error?.message || '删除失败，请稍后重试。')
  } finally {
    deletingId.value = null
  }
}
</script>

<template>
  <div class="mx-auto min-h-full max-w-6xl fade-in">
    <section class="resume-library-hero ui-card mb-6 p-6">
      <div class="resume-library-hero__copy">
        <span class="ui-section-badge">简历资产</span>
        <h2 class="ui-page-title mt-4 text-3xl">我的简历</h2>
        <p class="ui-page-subtitle mt-2 text-sm font-medium">
          这里会保留每份简历的预览图、上传时间和本地路径，方便你后续复用、定位和下载。
        </p>
      </div>
      <div class="resume-library-hero__stats">
        <div class="resume-library-stat">
          <span class="resume-library-stat__label">总数量</span>
          <strong class="resume-library-stat__value">{{ resumes.length }}</strong>
        </div>
        <div class="resume-library-stat">
          <span class="resume-library-stat__label">可预览</span>
          <strong class="resume-library-stat__value">{{ previewableCount }}</strong>
        </div>
      </div>
    </section>

    <div class="resume-library-note ui-card-soft mb-5">
      桌面版支持直接定位文件和打开文件；Web 调试环境会保留完整路径展示，并支持复制路径。
    </div>

    <div v-if="loading" class="ui-empty-state flex items-center justify-center gap-3 py-20">
      <Loader class="h-6 w-6 animate-spin text-primary" />
      <span class="text-sm text-slate-500 dark:text-slate-400">正在加载简历库...</span>
    </div>

    <div v-else-if="!resumes.length" class="ui-empty-state py-20 text-center">
      <FileUser class="mx-auto mb-4 h-16 w-16 text-slate-300 dark:text-slate-600" />
      <p class="text-slate-500 dark:text-slate-400">暂无简历记录</p>
      <p class="mt-1 text-sm text-slate-400 dark:text-slate-500">
        在面试配置中上传简历后，这里会展示预览图和对应的本地路径。
      </p>
    </div>

    <div v-else class="space-y-5">
      <article
        v-for="record in resumes"
        :key="record.id"
        class="resume-item ui-card ui-card-interactive"
      >
        <div class="flex flex-col gap-5 xl:flex-row">
          <button
            type="button"
            class="resume-thumb group"
            :disabled="record.can_preview === false"
            @click="openPreview(record)"
          >
            <img
              v-if="record.can_preview !== false"
              :src="previewCover(record)"
              :alt="record.file_name"
              class="h-full w-full object-cover transition duration-300 group-hover:scale-[1.02]"
            />
            <div
              v-else
              class="thumb-empty"
            >
              <FileText class="h-10 w-10" />
              <span class="text-xs">暂无可用预览</span>
            </div>
            <div v-if="record.can_preview !== false" class="thumb-overlay">
              <Eye class="h-5 w-5 text-white" />
              <span class="text-sm font-semibold text-white">查看预览</span>
            </div>
          </button>

          <div class="min-w-0 flex-1">
            <div class="flex items-start gap-4">
              <div class="file-badge">
                <FileText class="h-5 w-5" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-base font-semibold text-slate-900 dark:text-white">{{ record.file_name }}</p>
                <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  上传时间：{{ formatTime(record.upload_time) }}
                </p>
              </div>
            </div>

            <div class="mt-4 flex flex-wrap items-center gap-2 text-xs">
              <span class="meta-badge">{{ formatKind(record) }}</span>
              <span class="meta-badge">{{ previewPageLabel(record) }}</span>
              <span class="meta-badge">本地存储文件</span>
            </div>

            <div class="path-panel mt-4">
              <p class="path-label">简历路径</p>
              <p class="path-value">{{ getDisplayPath(record) }}</p>
            </div>

            <div class="mt-4 flex flex-wrap items-center gap-2">
              <button
                v-if="record.can_preview !== false"
                type="button"
                class="action-btn action-primary"
                @click="openPreview(record)"
              >
                <Eye class="h-4 w-4" />
                预览
              </button>
              <button
                v-if="isDesktop"
                type="button"
                class="action-btn"
                @click="handleLocate(record)"
              >
                <FolderOpen class="h-4 w-4" />
                定位文件
              </button>
              <button
                v-if="isDesktop"
                type="button"
                class="action-btn"
                @click="handleOpen(record)"
              >
                <ExternalLink class="h-4 w-4" />
                打开文件
              </button>
              <button
                type="button"
                class="action-btn"
                @click="handleCopyPath(record)"
              >
                <Copy class="h-4 w-4" />
                复制路径
              </button>
              <a
                :href="getResumeFileUrl(record.id)"
                download
                class="action-btn"
              >
                <Download class="h-4 w-4" />
                下载
              </a>
              <button
                type="button"
                class="action-btn action-danger ml-auto"
                :disabled="deletingId === record.id"
                @click="handleDelete(record)"
              >
                <Loader v-if="deletingId === record.id" class="h-4 w-4 animate-spin" />
                <Trash2 v-else class="h-4 w-4" />
                删除
              </button>
            </div>
          </div>
        </div>
      </article>
    </div>

    <Teleport to="body">
      <div
        v-if="previewResume"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm"
        @click.self="closePreview"
      >
        <div class="preview-shell">
          <div class="preview-header">
            <div class="min-w-0">
              <h3 class="truncate text-sm font-bold text-slate-800 dark:text-white">{{ previewResume.file_name }}</h3>
              <p class="mt-1 text-xs text-slate-400 dark:text-slate-500">
                {{ previewResume.preview_page_count || 1 }} 页图片预览，可放大查看细节。
              </p>
            </div>
            <div class="flex items-center gap-2">
              <a
                :href="getResumeFileUrl(previewResume.id)"
                download
                class="icon-btn"
              >
                <Download class="h-4 w-4" />
              </a>
              <button
                type="button"
                class="icon-btn"
                @click="closePreview"
              >
                <X class="h-4 w-4" />
              </button>
            </div>
          </div>

          <div class="preview-layout">
            <aside v-if="previewImages.length > 1" class="preview-sidebar custom-scroll">
              <button
                v-for="(url, index) in previewImages"
                :key="url"
                type="button"
                class="preview-thumb-item"
                :class="{ 'preview-thumb-active': previewPage === index }"
                @click="selectPreviewPage(index)"
              >
                <img :src="url" :alt="`${previewResume.file_name} 第 ${index + 1} 页`" class="h-full w-full object-cover" />
                <span class="preview-thumb-index">{{ index + 1 }}</span>
              </button>
            </aside>

            <div class="preview-stage">
              <div class="preview-toolbar">
                <button type="button" class="icon-btn" @click="previousPage">
                  <ChevronLeft class="h-4 w-4" />
                </button>
                <span class="text-xs text-slate-500 dark:text-slate-400">
                  第 {{ previewPage + 1 }} / {{ previewImages.length || 1 }} 页
                </span>
                <button type="button" class="icon-btn" @click="nextPage">
                  <ChevronRight class="h-4 w-4" />
                </button>
              </div>

              <div class="preview-canvas custom-scroll">
                <div class="zoom-controls">
                  <button type="button" class="icon-btn" :disabled="previewZoom <= PREVIEW_MIN_ZOOM" @click="zoomOutPreview">
                    <ZoomOut class="h-4 w-4" />
                  </button>
                  <span class="zoom-percent">{{ previewZoomPercent }}%</span>
                  <button type="button" class="icon-btn" :disabled="previewZoom >= PREVIEW_MAX_ZOOM" @click="zoomInPreview">
                    <ZoomIn class="h-4 w-4" />
                  </button>
                  <button type="button" class="zoom-hint" :disabled="previewZoom <= PREVIEW_MIN_ZOOM" @click="resetPreviewZoom">
                    <RotateCcw class="h-4 w-4" />
                    适应宽度
                  </button>
                </div>

                <div
                  v-if="activePreviewUrl"
                  class="preview-image-stage"
                  :class="{ 'preview-image-stage-zoomed': previewZoomed }"
                >
                  <img
                    :src="activePreviewUrl"
                    :alt="previewResume.file_name"
                    class="preview-image"
                    :class="{ 'preview-image-zoomed': previewZoomed }"
                    :style="{ width: previewZoomed ? `${previewZoom * 100}%` : undefined }"
                    @click="togglePreviewZoom"
                  />
                </div>
                <div v-else class="flex h-full items-center justify-center text-sm text-slate-400 dark:text-slate-500">
                  暂无可用预览图
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.resume-item {
  padding: 1.25rem;
}

.resume-library-hero {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.resume-library-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 12% 20%, rgba(59, 130, 246, 0.12), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(99, 102, 241, 0.1), transparent 24%);
  pointer-events: none;
}

.resume-library-hero__copy,
.resume-library-hero__stats {
  position: relative;
  z-index: 1;
}

.resume-library-hero__stats {
  display: flex;
  gap: 0.8rem;
}

.resume-library-stat {
  display: flex;
  min-width: 118px;
  flex-direction: column;
  gap: 0.3rem;
  border-radius: 1.2rem;
  border: 1px solid var(--ui-border-subtle);
  background: var(--ui-surface-raised);
  padding: 0.95rem 1rem;
  box-shadow: var(--ui-shadow-sm);
}

.resume-library-stat__label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ui-text-muted);
}

.resume-library-stat__value {
  font-size: 1.4rem;
  line-height: 1;
  font-weight: 900;
  color: var(--ui-text-primary);
}

.resume-library-note {
  padding: 0.95rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ui-info);
}

.resume-thumb {
  @apply relative block w-full shrink-0 overflow-hidden rounded-[24px] border text-left transition-all xl:w-[220px];
  height: 280px;
  border-color: rgba(203, 213, 225, 0.9);
  background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
}

.resume-thumb:disabled {
  cursor: default;
}

.dark .resume-thumb {
  border-color: rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, #111827 0%, #0f172a 100%);
}

.thumb-empty {
  @apply flex h-full w-full flex-col items-center justify-center gap-3 text-slate-400 dark:text-slate-500;
}

.thumb-overlay {
  @apply absolute inset-0 flex flex-col items-center justify-center gap-2 opacity-0 transition-opacity;
  background: rgba(15, 23, 42, 0.42);
}

.group:hover .thumb-overlay {
  opacity: 1;
}

.file-badge {
  @apply flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl text-white;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
  box-shadow: 0 12px 24px rgba(79, 70, 229, 0.24);
}

.meta-badge {
  @apply inline-flex items-center rounded-full px-2.5 py-1 font-medium;
  background: var(--ui-surface-3);
  color: var(--ui-text-secondary);
}

.path-panel {
  @apply rounded-2xl border px-4 py-3;
  border-color: rgba(191, 219, 254, 0.85);
  background:
    linear-gradient(180deg, rgba(239, 246, 255, 0.92) 0%, rgba(248, 250, 252, 0.9) 100%);
}

.dark .path-panel {
  border-color: rgba(96, 165, 250, 0.18);
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.82) 0%, rgba(2, 6, 23, 0.86) 100%);
}

.path-label {
  @apply text-[11px] font-semibold uppercase tracking-[0.24em];
  color: rgb(59, 130, 246);
}

.path-value {
  @apply mt-2 break-all text-sm leading-6;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  color: rgb(15, 23, 42);
}

.dark .path-value {
  color: rgb(226, 232, 240);
}

.action-btn {
  @apply inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-medium transition-colors;
  border-color: var(--ui-border-default);
  color: var(--ui-text-secondary);
  background: var(--ui-surface-raised);
}

.action-btn:hover {
  border-color: var(--ui-border-strong);
  color: var(--ui-accent-strong);
  background: var(--ui-surface-1);
}

.action-primary {
  border-color: rgba(79, 70, 229, 0.22);
  color: var(--ui-accent-strong);
  background: var(--ui-accent-soft);
}

.action-danger {
  color: var(--ui-danger);
  background: var(--ui-danger-soft);
}

.action-danger:hover {
  border-color: rgba(220, 38, 38, 0.35);
  color: var(--ui-danger);
  background: rgba(244, 63, 94, 0.16);
}

.preview-shell {
  @apply flex max-h-[90vh] w-full max-w-6xl flex-col overflow-hidden rounded-[28px] border shadow-2xl;
  background: rgba(255, 255, 255, 0.98);
  border-color: rgba(226, 232, 240, 0.9);
}

.dark .preview-shell {
  background: rgba(10, 14, 24, 0.98);
  border-color: rgba(255, 255, 255, 0.08);
}

.preview-header {
  @apply flex items-center justify-between gap-4 border-b px-5 py-4;
  border-color: rgba(226, 232, 240, 0.9);
}

.dark .preview-header {
  border-color: rgba(255, 255, 255, 0.08);
}

.preview-layout {
  @apply flex min-h-0 flex-1;
}

.preview-sidebar {
  @apply hidden w-32 shrink-0 gap-3 overflow-y-auto border-r p-4 md:flex md:flex-col;
  border-color: rgba(226, 232, 240, 0.9);
  background: rgba(248, 250, 252, 0.85);
}

.dark .preview-sidebar {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}

.preview-thumb-item {
  @apply relative overflow-hidden rounded-2xl border text-left transition-all;
  height: 120px;
  border-color: rgba(203, 213, 225, 0.8);
}

.preview-thumb-active {
  border-color: rgba(79, 70, 229, 0.55);
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.18);
}

.preview-thumb-index {
  @apply absolute bottom-2 right-2 rounded-full px-2 py-0.5 text-[11px] font-semibold text-white;
  background: rgba(15, 23, 42, 0.7);
}

.preview-stage {
  @apply flex min-h-0 flex-1 flex-col;
}

.preview-toolbar {
  @apply flex items-center justify-center gap-3 border-b px-4 py-3;
  border-color: rgba(226, 232, 240, 0.9);
}

.dark .preview-toolbar {
  border-color: rgba(255, 255, 255, 0.08);
}

.preview-canvas {
  @apply relative flex-1 overflow-auto p-4 md:p-6;
  background:
    radial-gradient(circle at top left, rgba(99, 102, 241, 0.08), transparent 28%),
    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.dark .preview-canvas {
  background:
    radial-gradient(circle at top left, rgba(99, 102, 241, 0.12), transparent 28%),
    linear-gradient(180deg, #0f172a 0%, #020617 100%);
}

.zoom-controls {
  @apply absolute right-4 top-4 z-10 flex items-center gap-2;
}

.zoom-percent {
  @apply rounded-full border px-3 py-1 text-xs font-semibold tabular-nums;
  border-color: rgba(226, 232, 240, 0.95);
  background: rgba(255, 255, 255, 0.88);
  color: rgb(51, 65, 85);
}

.dark .zoom-percent {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.88);
  color: rgb(203, 213, 225);
}

.zoom-hint {
  @apply inline-flex items-center gap-1 rounded-full border px-3 py-1.5 text-xs font-medium;
  border-color: rgba(226, 232, 240, 0.95);
  background: rgba(255, 255, 255, 0.88);
  color: rgb(51, 65, 85);
}

.dark .zoom-hint {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(15, 23, 42, 0.88);
  color: rgb(203, 213, 225);
}

.preview-image-stage {
  @apply flex min-h-full min-w-full items-start justify-center;
}

.preview-image-stage-zoomed {
  justify-content: flex-start;
}

.preview-image {
  @apply block rounded-2xl shadow-xl;
  width: min(100%, 960px);
  max-width: 100%;
  cursor: zoom-in;
}

.preview-image-zoomed {
  max-width: none;
  cursor: zoom-out;
}

.icon-btn {
  @apply inline-flex items-center justify-center rounded-xl border p-2 transition-colors;
  border-color: rgba(226, 232, 240, 0.95);
  color: rgb(71, 85, 105);
}

.icon-btn:hover {
  border-color: rgba(79, 70, 229, 0.4);
  color: rgb(79, 70, 229);
}

.icon-btn:disabled,
.zoom-hint:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.dark .icon-btn {
  border-color: rgba(255, 255, 255, 0.08);
  color: rgb(203, 213, 225);
}

@media (max-width: 880px) {
  .resume-library-hero {
    flex-direction: column;
    align-items: stretch;
  }

  .resume-library-hero__stats {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
