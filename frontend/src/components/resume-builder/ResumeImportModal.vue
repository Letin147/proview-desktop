<script setup lang="ts">
import { ref, computed } from 'vue'
import { Upload, FileText, Loader, CheckCircle, XCircle, AlertCircle } from 'lucide-vue-next'
import { useResumeImportStore } from '../../stores/resumeImport'
import { getResumeFileValidationError, RESUME_UPLOAD_ACCEPT, RESUME_UPLOAD_HINT } from '../../utils/resumeFile'

const emit = defineEmits<{
  success: []
  cancel: []
}>()

const importStore = useResumeImportStore()
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const selectionError = ref('')

// 进度状态映射
const progressSteps = computed(() => {
  const current = importStore.importProgress
  return {
    uploading: { label: '上传中', active: current === 'uploading', done: ['parsing', 'loading', 'success'].includes(current) },
    parsing: { label: 'AI 解析中', active: current === 'parsing', done: ['loading', 'success'].includes(current) },
    loading: { label: '数据装载中', active: current === 'loading', done: current === 'success' },
  }
})

const statusConfig = computed(() => {
  switch (importStore.importProgress) {
    case 'idle':
      return { icon: Upload, color: 'text-slate-400', message: '选择简历文件开始导入' }
    case 'uploading':
    case 'parsing':
    case 'loading':
      return { icon: Loader, color: 'text-indigo-500 animate-spin', message: '正在处理，请稍候...' }
    case 'success':
      return { icon: CheckCircle, color: 'text-emerald-500', message: '导入成功！' }
    case 'error':
      return { icon: XCircle, color: 'text-red-500', message: importStore.importError || '导入失败' }
    default:
      return { icon: Upload, color: 'text-slate-400', message: '' }
  }
})

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const nextFile = input.files?.[0] || null
  if (!nextFile) {
    selectionError.value = ''
    return
  }

  const validationError = getResumeFileValidationError(nextFile)
  if (validationError) {
    selectedFile.value = null
    selectionError.value = validationError
    input.value = ''
    return
  }

  selectedFile.value = nextFile
  selectionError.value = ''
}

function handleFileDrop(event: DragEvent) {
  const nextFile = event.dataTransfer?.files?.[0] || null
  if (!nextFile) {
    return
  }

  const validationError = getResumeFileValidationError(nextFile)
  if (validationError) {
    selectedFile.value = null
    selectionError.value = validationError
    return
  }

  selectedFile.value = nextFile
  selectionError.value = ''
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

async function startImport() {
  if (!selectedFile.value) return

  const success = await importStore.importResume(selectedFile.value)

  if (success) {
    // 延迟 1 秒后自动关闭，让用户看到成功提示
    setTimeout(() => {
      emit('success')
      importStore.resetImportState()
    }, 1000)
  }
}

function cancel() {
  importStore.resetImportState()
  selectedFile.value = null
  selectionError.value = ''
  emit('cancel')
}
</script>

<template>
  <div class="import-modal-overlay" @click.self="cancel">
    <div class="import-modal">
      <!-- 头部 -->
      <div class="modal-header">
        <h2 class="modal-title">导入现有简历</h2>
        <p class="modal-subtitle">AI 将自动提取简历内容并填充到编辑器</p>
      </div>

      <!-- 主体 -->
      <div class="modal-body">
        <!-- 文件选择区 -->
        <div
          v-if="!selectedFile"
          class="upload-zone"
          @click="triggerFileInput"
          @dragover.prevent
          @drop.prevent="handleFileDrop"
        >
          <component :is="statusConfig.icon" :class="['upload-icon', statusConfig.color]" />
            <p class="upload-text">点击选择或拖拽文件到此处</p>
            <p class="upload-hint">支持 {{ RESUME_UPLOAD_HINT }}</p>
            <input
              ref="fileInputRef"
              type="file"
              :accept="RESUME_UPLOAD_ACCEPT"
              class="hidden"
              @change="handleFileSelect"
            />
          </div>

        <!-- 已选择文件 -->
        <div v-else class="file-selected">
          <FileText class="file-icon" />
          <div class="file-info">
            <p class="file-name">{{ selectedFile.name }}</p>
            <p class="file-size">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
          </div>
          <button
            v-if="importStore.importProgress === 'idle'"
            @click="selectedFile = null; selectionError = ''"
            class="file-remove"
          >
            <XCircle class="w-4 h-4" />
          </button>
        </div>

        <div v-if="selectionError" class="error-detail">
          <AlertCircle class="w-4 h-4 text-red-500" />
          <span>{{ selectionError }}</span>
        </div>

        <!-- 进度指示器 -->
        <div v-if="importStore.isImporting" class="progress-steps">
          <div
            v-for="(step, key) in progressSteps"
            :key="key"
            class="progress-step"
            :class="{
              'step-active': step.active,
              'step-done': step.done,
            }"
          >
            <div class="step-dot" />
            <span class="step-label">{{ step.label }}</span>
          </div>
        </div>

        <!-- 状态消息 -->
        <div v-if="importStore.importProgress !== 'idle'" class="status-message">
          <component :is="statusConfig.icon" :class="['status-icon', statusConfig.color]" />
          <span>{{ statusConfig.message }}</span>
        </div>

        <!-- 错误详情 -->
        <div v-if="importStore.importProgress === 'error' && importStore.importError" class="error-detail">
          <AlertCircle class="w-4 h-4 text-red-500" />
          <span>{{ importStore.importError }}</span>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="modal-footer">
        <button
          @click="cancel"
          class="btn-secondary"
          :disabled="importStore.isImporting"
        >
          取消
        </button>
        <button
          v-if="selectedFile && importStore.importProgress === 'idle'"
          @click="startImport"
          class="btn-primary"
        >
          开始导入
        </button>
        <button
          v-else-if="importStore.importProgress === 'error'"
          @click="selectedFile = null; importStore.resetImportState()"
          class="btn-primary"
        >
          重新选择
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.import-modal-overlay {
  @apply fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4;
  animation: fadeIn 0.2s ease-out;
}

.import-modal {
  @apply bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full;
  animation: slideUp 0.3s ease-out;
}

.modal-header {
  @apply p-6 border-b border-slate-200 dark:border-white/10;
}

.modal-title {
  @apply text-xl font-bold text-slate-900 dark:text-white;
}

.modal-subtitle {
  @apply text-sm text-slate-500 dark:text-slate-400 mt-1;
}

.modal-body {
  @apply p-6 space-y-4;
}

.upload-zone {
  @apply border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-xl p-8 text-center cursor-pointer transition-colors;
  @apply hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/10;
}

.upload-icon {
  @apply w-12 h-12 mx-auto mb-3;
}

.upload-text {
  @apply text-sm font-medium text-slate-700 dark:text-slate-300;
}

.upload-hint {
  @apply text-xs text-slate-400 dark:text-slate-500 mt-1;
}

.file-selected {
  @apply flex items-center gap-3 p-4 bg-slate-50 dark:bg-slate-900 rounded-xl;
}

.file-icon {
  @apply w-10 h-10 text-indigo-500 shrink-0;
}

.file-info {
  @apply flex-1 min-w-0;
}

.file-name {
  @apply text-sm font-medium text-slate-900 dark:text-white truncate;
}

.file-size {
  @apply text-xs text-slate-500 dark:text-slate-400;
}

.file-remove {
  @apply p-1 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition;
}

.progress-steps {
  @apply flex items-center justify-between gap-2 py-4;
}

.progress-step {
  @apply flex flex-col items-center gap-2 flex-1;
}

.step-dot {
  @apply w-3 h-3 rounded-full bg-slate-300 dark:bg-slate-600 transition-colors;
}

.step-active .step-dot {
  @apply bg-indigo-500 ring-4 ring-indigo-500/20;
}

.step-done .step-dot {
  @apply bg-emerald-500;
}

.step-label {
  @apply text-xs text-slate-500 dark:text-slate-400;
}

.step-active .step-label {
  @apply text-indigo-500 font-medium;
}

.status-message {
  @apply flex items-center gap-2 text-sm;
}

.status-icon {
  @apply w-5 h-5;
}

.error-detail {
  @apply flex items-start gap-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg text-sm text-red-600 dark:text-red-400;
}

.modal-footer {
  @apply p-6 border-t border-slate-200 dark:border-white/10 flex justify-end gap-3;
}

.btn-secondary {
  @apply px-4 py-2 rounded-xl text-sm font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition disabled:opacity-50;
}

.btn-primary {
  @apply px-4 py-2 rounded-xl text-sm font-medium text-white bg-indigo-500 hover:bg-indigo-600 transition disabled:opacity-50;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
