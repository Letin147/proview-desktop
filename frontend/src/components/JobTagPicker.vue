<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import api from '../services/api'

const props = defineProps<{ modelValue: string; defaultExpanded?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const allPositions = ref<string[]>([])
const expanded = ref(props.defaultExpanded ?? false)
const searchMode = ref(false)
const displayTags = ref<string[]>([])

const BATCH_SIZE = 8

const TAG_COLORS = [
  { bg: '#FFF0F0', text: '#E03131', border: '#FFC9C9' },
  { bg: '#FFF4E6', text: '#E8590C', border: '#FFD8A8' },
  { bg: '#FFF9DB', text: '#E67700', border: '#FFE066' },
  { bg: '#EBFBEE', text: '#2F9E44', border: '#B2F2BB' },
  { bg: '#E6FCF5', text: '#099268', border: '#96F2D7' },
  { bg: '#E7F5FF', text: '#1971C2', border: '#A5D8FF' },
  { bg: '#EDF2FF', text: '#4263EB', border: '#BAC8FF' },
  { bg: '#F8F0FC', text: '#AE3EC9', border: '#EEBEFA' },
]

const filteredPositions = computed(() => {
  if (!props.modelValue.trim()) return []
  const q = props.modelValue.trim().toLowerCase()
  return allPositions.value.filter(p => p.toLowerCase().includes(q)).slice(0, 12)
})

const visibleTags = computed(() => {
  if (searchMode.value && props.modelValue.trim()) return filteredPositions.value
  return displayTags.value
})

function shuffleTags() {
  const pool = [...allPositions.value]
  const result: string[] = []
  while (result.length < BATCH_SIZE && pool.length > 0) {
    const idx = Math.floor(Math.random() * pool.length)
    const item = pool.splice(idx, 1)[0]
    if (item) result.push(item)
  }
  displayTags.value = result
}

function onInput(e: Event) {
  const val = (e.target as HTMLInputElement).value
  emit('update:modelValue', val)
  searchMode.value = val.trim().length > 0 && expanded.value
}

function selectTag(tag: string) {
  emit('update:modelValue', tag)
  searchMode.value = false
}

function getColor(index: number) {
  return TAG_COLORS[index % TAG_COLORS.length]!
}

onMounted(async () => {
  try {
    const { data } = await api.get('/api/positions')
    allPositions.value = data.positions || []
    shuffleTags()
  } catch (e) {
    console.error('加载岗位数据失败:', e)
  }
})
</script>

<template>
  <div class="job-tag-picker">
    <input
      :value="modelValue"
      @input="onInput"
      type="text"
      placeholder="在这里填写岗位"
      class="config-input w-full"
    />

    <!-- 展开/收起按钮 -->
    <button
      v-if="allPositions.length > 0"
      type="button"
      @click="expanded = !expanded"
      class="job-tag-picker__toggle"
    >
      {{ expanded ? '收起岗位推荐' : '🔍 查看更多岗位推荐' }}
    </button>

    <!-- 标签区域 -->
    <div v-if="expanded && allPositions.length > 0" class="job-tag-picker__panel">
      <div class="job-tag-picker__panel-head">
        <span class="job-tag-picker__panel-label">
          {{ searchMode && modelValue.trim() ? `搜索到 ${visibleTags.length} 个岗位` : '岗位快速检索，点击标签选择' }}
        </span>
        <button
          v-if="!searchMode || !modelValue.trim()"
          type="button"
          @click="shuffleTags"
          class="job-tag-picker__refresh"
        >
          <RefreshCw class="w-3 h-3" /> 换一批
        </button>
      </div>

      <div class="job-tag-picker__cloud">
        <button
          v-for="(tag, i) in visibleTags"
          :key="tag"
          type="button"
          @click="selectTag(tag)"
          class="job-tag"
          :style="{
            '--job-tag-bg': getColor(i).bg,
            '--job-tag-text': getColor(i).text,
            '--job-tag-border': getColor(i).border,
          }"
        >
          {{ tag }}
        </button>
        <span v-if="visibleTags.length === 0 && searchMode" class="job-tag-picker__empty">
          未找到匹配岗位，可直接输入自定义岗位
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.job-tag-picker__toggle {
  margin-top: 0.6rem;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--ui-accent-strong);
  transition: color 180ms ease;
}

.job-tag-picker__toggle:hover {
  color: var(--ui-accent);
}

.job-tag-picker__panel {
  margin-top: 0.9rem;
  border-radius: 1.15rem;
  border: 1px solid var(--ui-border-default);
  background: var(--ui-surface-2);
  padding: 0.95rem 1rem 1rem;
  box-shadow: var(--ui-shadow-sm);
}

.job-tag-picker__panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.8rem;
}

.job-tag-picker__panel-label,
.job-tag-picker__empty {
  font-size: 0.74rem;
  color: var(--ui-text-muted);
}

.job-tag-picker__refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--ui-text-secondary);
  transition: color 180ms ease;
}

.job-tag-picker__refresh:hover {
  color: var(--ui-accent-strong);
}

.job-tag-picker__cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.job-tag {
  @apply rounded-full border px-3 py-1.5 text-xs font-bold transition-all cursor-pointer;
  background: var(--job-tag-bg);
  color: var(--job-tag-text);
  border-color: var(--job-tag-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.job-tag:hover {
  filter: brightness(0.95);
  transform: translateY(-1px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.58),
    0 8px 18px rgba(15, 23, 42, 0.08);
}

.dark .job-tag-picker__toggle {
  color: #c7d2fe;
}

.dark .job-tag-picker__toggle:hover {
  color: #e2e8f0;
}

.dark .job-tag-picker__panel {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(15, 23, 42, 0.82);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 14px 28px rgba(0, 0, 0, 0.22);
}

.dark .job-tag-picker__panel-label,
.dark .job-tag-picker__empty {
  color: rgba(226, 232, 240, 0.62);
}

.dark .job-tag-picker__refresh {
  color: #94a3b8;
}

.dark .job-tag-picker__refresh:hover {
  color: #c7d2fe;
}

:root.dark .job-tag,
.dark .job-tag {
  filter: brightness(0.82) saturate(0.92);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

:root.dark .job-tag:hover,
.dark .job-tag:hover {
  filter: brightness(0.9) saturate(0.98);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.12),
    0 12px 24px rgba(0, 0, 0, 0.26);
}
</style>
