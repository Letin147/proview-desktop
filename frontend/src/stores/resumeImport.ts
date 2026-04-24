import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useResumeBuilderStore } from './resumeBuilder'
import { buildApiUrl } from '../services/runtimeConfig'
import { assertValidResumeFile } from '../utils/resumeFile'

/**
 * 简历导入状态管理
 * 处理：上传 -> 解析 -> 数据装载 的完整流程
 */
export const useResumeImportStore = defineStore('resumeImport', () => {
  // ===== 状态 =====
  const isImporting = ref(false)
  const importProgress = ref<'idle' | 'uploading' | 'parsing' | 'loading' | 'success' | 'error'>('idle')
  const importError = ref<string | null>(null)
  const rawText = ref<string>('')  // 用于调试的原始文本

  // ===== 导入流程 =====
  async function importResume(file: File): Promise<boolean> {
    const builderStore = useResumeBuilderStore()

    try {
      assertValidResumeFile(file)

      // 1. 重置状态
      isImporting.value = true
      importProgress.value = 'uploading'
      importError.value = null
      rawText.value = ''

      // 2. 上传文件
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await fetch(buildApiUrl('/api/resume/parse'), {
        method: 'POST',
        body: formData,
      })

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json()
        throw new Error(errorData.message || '上传失败')
      }

      // 3. 解析中
      importProgress.value = 'parsing'
      const result = await uploadResponse.json()

      if (result.status !== 'success') {
        throw new Error(result.message || '解析失败')
      }

      // 4. 数据装载
      importProgress.value = 'loading'
      rawText.value = result.raw_text || ''

      // 合并解析数据到 builder store
      await loadParsedData(result.data, builderStore)

      // 5. 完成
      importProgress.value = 'success'
      isImporting.value = false

      return true

    } catch (error: any) {
      console.error('简历导入失败:', error)
      importProgress.value = 'error'
      importError.value = error.message || '导入失败，请重试'
      isImporting.value = false
      return false
    }
  }

  /**
   * 将解析后的数据装载到 builder store
   */
  async function loadParsedData(
    parsedData: { basicInfo: any; modules: any[] },
    builderStore: ReturnType<typeof useResumeBuilderStore>
  ) {
    // 1. 更新基本信息
    if (parsedData.basicInfo) {
      Object.assign(builderStore.document.basicInfo, parsedData.basicInfo)
    }

    // 2. 清空现有模块（可选：或者合并）
    builderStore.document.modules = []

    // 3. 装载解析的模块
    if (parsedData.modules && Array.isArray(parsedData.modules)) {
      for (const module of parsedData.modules) {
        // 只添加有内容的模块
        const hasContent =
          (module.entries && module.entries.length > 0) ||
          (module.content && module.content.trim()) ||
          (module.intention && Object.values(module.intention).some(v => v)) ||
          (module.tags && module.tags.length > 0)

        if (hasContent) {
          builderStore.document.modules.push(module)
        }
      }
    }

    // 4. 标记为脏数据，触发自动保存
    builderStore.isDirty = true
  }

  /**
   * 重置导入状态
   */
  function resetImportState() {
    isImporting.value = false
    importProgress.value = 'idle'
    importError.value = null
    rawText.value = ''
  }

  return {
    // state
    isImporting,
    importProgress,
    importError,
    rawText,
    // actions
    importResume,
    resetImportState,
  }
})
