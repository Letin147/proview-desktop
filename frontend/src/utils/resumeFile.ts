const SUPPORTED_RESUME_EXTENSIONS = [
  '.pdf',
  '.docx',
  '.md',
  '.markdown',
  '.txt',
  '.png',
  '.jpg',
  '.jpeg',
  '.bmp',
  '.webp',
  '.heic',
  '.heif',
] as const

const SUPPORTED_RESUME_EXTENSION_SET = new Set<string>(SUPPORTED_RESUME_EXTENSIONS)

export const RESUME_UPLOAD_ACCEPT = SUPPORTED_RESUME_EXTENSIONS.join(',')
export const RESUME_UPLOAD_HINT = 'PDF / Word(.docx) / Markdown / TXT / 图片'

export function getResumeFileExtension(fileName: string): string {
  const normalizedName = String(fileName || '').trim().toLowerCase()
  const lastDotIndex = normalizedName.lastIndexOf('.')
  if (lastDotIndex <= 0 || lastDotIndex === normalizedName.length - 1) {
    return ''
  }
  return normalizedName.slice(lastDotIndex)
}

export function getResumeFileValidationError(file: Pick<File, 'name'> | null | undefined): string {
  const fileName = String(file?.name || '').trim()
  if (!fileName) {
    return '请选择要上传的简历文件。'
  }

  const ext = getResumeFileExtension(fileName)
  if (!ext) {
    return '无法识别简历文件类型，请上传带扩展名的文件。'
  }

  if (ext === '.doc') {
    return '暂不支持旧版 .doc，请先另存为 .docx 后再上传。'
  }

  if (!SUPPORTED_RESUME_EXTENSION_SET.has(ext)) {
    return `不支持的简历格式: ${ext}。当前支持 PDF、图片、DOCX、MD、TXT。`
  }

  return ''
}

export function assertValidResumeFile(file: Pick<File, 'name'> | null | undefined): void {
  const validationError = getResumeFileValidationError(file)
  if (validationError) {
    throw new Error(validationError)
  }
}
