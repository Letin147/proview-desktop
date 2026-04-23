<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { CareerPlanningDocument } from '../../types/career-planning'

const props = defineProps<{
  documents: CareerPlanningDocument[]
  loading: boolean
  error: string
}>()

// 状态管理
const activeDocId = ref('')
const searchQuery = ref('')
const selectedCategory = ref<string>('全部')
const favoriteOnly = ref(false)

// 用户交互状态（本地存储）
const favoriteIds = ref<Set<string>>(new Set())
const readProgress = ref<Record<string, number>>({})
const readHistory = ref<Record<string, string>>({})

// 从 localStorage 加载用户状态
watch(() => props.documents, (documents) => {
  if (!documents.length) return
  
  // 加载收藏状态
  const savedFavorites = localStorage.getItem('career_doc_favorites')
  if (savedFavorites) {
    favoriteIds.value = new Set(JSON.parse(savedFavorites))
  }
  
  // 加载阅读进度
  const savedProgress = localStorage.getItem('career_doc_progress')
  if (savedProgress) {
    readProgress.value = JSON.parse(savedProgress)
  }
  
  // 加载阅读历史
  const savedHistory = localStorage.getItem('career_doc_history')
  if (savedHistory) {
    readHistory.value = JSON.parse(savedHistory)
  }
  
  // 设置默认选中的文档
  if (!activeDocId.value || !documents.some((doc) => doc.id === activeDocId.value)) {
    activeDocId.value = documents[0]?.id || ''
  }
}, { immediate: true })

// 获取所有分类
const categories = computed(() => {
  const cats = ['全部', '求职攻略', '进阶技巧', '职业发展']
  return cats
})

// 筛选后的文档列表
const filteredDocuments = computed(() => {
  let docs = props.documents
  
  // 分类筛选
  if (selectedCategory.value !== '全部') {
    docs = docs.filter(doc => doc.category === selectedCategory.value)
  }
  
  // 收藏筛选
  if (favoriteOnly.value) {
    docs = docs.filter(doc => favoriteIds.value.has(doc.id))
  }
  
  // 搜索筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    docs = docs.filter(doc => 
      doc.title.toLowerCase().includes(query) ||
      doc.subtitle.toLowerCase().includes(query) ||
      doc.summary.toLowerCase().includes(query) ||
      doc.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  return docs
})

watch(filteredDocuments, (documents) => {
  if (!documents.length) {
    activeDocId.value = ''
    return
  }

  if (!documents.some((doc) => doc.id === activeDocId.value)) {
    activeDocId.value = documents[0]?.id || ''
  }
}, { immediate: true })

// 当前激活的文档
const activeDocument = computed(() => 
  props.documents.find(doc => doc.id === activeDocId.value) || null
)

// 推荐文档（基于标签相似度）
const recommendedDocs = computed(() => {
  if (!activeDocument.value) return []
  const activeTags = new Set(activeDocument.value.tags)
  return props.documents
    .filter(doc => doc.id !== activeDocId.value)
    .map(doc => ({
      ...doc,
      matchScore: doc.tags.filter(tag => activeTags.has(tag)).length
    }))
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, 2)
})

// 收藏功能
function toggleFavorite(docId: string) {
  if (favoriteIds.value.has(docId)) {
    favoriteIds.value.delete(docId)
  } else {
    favoriteIds.value.add(docId)
  }
  favoriteIds.value = new Set(favoriteIds.value)
  localStorage.setItem('career_doc_favorites', JSON.stringify([...favoriteIds.value]))
}

// 更新阅读进度
function updateProgress(docId: string, progress: number) {
  readProgress.value[docId] = progress
  readHistory.value[docId] = new Date().toISOString()
  localStorage.setItem('career_doc_progress', JSON.stringify(readProgress.value))
  localStorage.setItem('career_doc_history', JSON.stringify(readHistory.value))
}

watch(activeDocument, (document) => {
  if (!document) return
  const currentProgress = readProgress.value[document.id] || 0
  updateProgress(document.id, Math.max(currentProgress, 100))
}, { immediate: true })

// 分享功能
function shareDocument(doc: CareerPlanningDocument) {
  const shareData = {
    title: `${doc.title} - ProView AI Interviewer`,
    text: doc.summary,
    url: window.location.href
  }
  
  if (navigator.share) {
    navigator.share(shareData).catch(() => {
      copyToClipboard(shareData.url)
    })
  } else {
    copyToClipboard(`${shareData.title}\n${shareData.text}\n${shareData.url}`)
  }
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text).then(() => {
    alert('链接已复制到剪贴板')
  })
}

// 获取难度颜色
function getDifficultyColor(difficulty: string) {
  const colors: Record<string, string> = {
    '入门': 'border border-slate-200 bg-white text-slate-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-300',
    '进阶': 'border border-slate-200 bg-white text-slate-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-300',
    '中级': 'border border-slate-200 bg-white text-slate-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-300',
    '高级': 'border border-slate-200 bg-white text-slate-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-300'
  }
  return colors[difficulty] || colors['入门']
}

// 获取分类图标
function getCategoryIcon(icon: string) {
  const icons: Record<string, string> = {
    'book-open': '📚',
    'cpu': '🤖',
    'map': '🗺️',
    'graduation-cap': '🎓',
    'trending-up': '📈',
    'bot': '💬'
  }
  return icons[icon] || '📄'
}
</script>

<template>
  <section class="rounded-3xl border border-slate-200/85 bg-white/90 p-6 shadow-[0_18px_48px_rgba(15,23,42,0.08)] dark:border-white/10 dark:bg-[#0C0F17]/90">
    <!-- 顶部标题区 -->
    <div class="mb-6 flex items-start justify-between gap-4">
      <div>
        <h2 class="text-2xl font-black text-slate-900 dark:text-white">📚 学习中心</h2>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          求职必读指南，AI面试技巧，职业发展路径
        </p>
      </div>
      <div class="flex items-center gap-2">
        <span class="rounded-full border border-slate-200 bg-white/80 px-3 py-1 text-xs font-semibold text-slate-700 dark:border-white/10 dark:bg-white/5 dark:text-slate-300">
          {{ filteredDocuments.length }} 篇精选内容
        </span>
      </div>
    </div>

    <!-- 文档类别快捷入口 - 横向长卡片 -->
    <div class="mb-6 grid gap-3 sm:grid-cols-3">
      <div
        v-for="doc in filteredDocuments"
        :key="doc.id"
        @click="activeDocId = doc.id"
        class="group cursor-pointer rounded-2xl border p-4 transition-all duration-200"
        :class="activeDocument?.id === doc.id 
          ? 'border-indigo-300 bg-[linear-gradient(135deg,rgba(224,242,254,0.74)_0%,rgba(238,242,255,0.8)_55%,rgba(252,231,243,0.72)_100%)] shadow-[0_14px_30px_rgba(79,70,229,0.12)] dark:border-indigo-400/40 dark:bg-[linear-gradient(135deg,rgba(30,58,138,0.42)_0%,rgba(67,56,202,0.34)_55%,rgba(131,24,67,0.28)_100%)] dark:shadow-none' 
          : 'border-slate-200/90 bg-white/85 hover:border-indigo-300 hover:shadow-[0_14px_30px_rgba(79,70,229,0.1)] dark:border-white/10 dark:bg-white/5 dark:hover:border-indigo-500/30'"
      >
        <div class="flex items-start gap-3">
          <div 
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white text-2xl shadow-sm dark:border-white/10 dark:bg-white/10"
          >
            {{ getCategoryIcon(doc.cover_icon) }}
          </div>
          <div class="min-w-0 flex-1">
            <h3 class="font-bold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
              {{ doc.title }}
            </h3>
            <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
              {{ doc.subtitle }}
            </p>
          </div>
        </div>
        <!-- 简介内容 -->
        <p class="mt-3 text-xs text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">
          {{ doc.summary }}
        </p>
        <!-- 标签信息 -->
        <div class="mt-3 flex flex-wrap items-center gap-2">
          <span 
            class="rounded-full px-2 py-0.5 text-[10px] font-semibold"
            :class="getDifficultyColor(doc.difficulty)"
          >
            {{ doc.difficulty }}
          </span>
          <span class="flex items-center gap-1 text-[10px] text-slate-400">
            <span>⏱️</span>
            <span>{{ doc.read_time }}分钟</span>
          </span>
          <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:bg-white/10 dark:text-slate-300">
            {{ doc.category }}
          </span>
        </div>
        <!-- 收藏按钮 -->
        <div class="mt-3 flex items-center justify-between">
          <div class="flex flex-wrap gap-1">
            <span 
              v-for="tag in doc.tags.slice(0, 3)" 
              :key="tag"
              class="rounded-full bg-indigo-50 px-1.5 py-0.5 text-[9px] font-medium text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-300"
            >
              {{ tag }}
            </span>
          </div>
          <button
            @click.stop="toggleFavorite(doc.id)"
            class="shrink-0 rounded-full p-1.5 transition hover:bg-rose-100 dark:hover:bg-rose-500/20"
            :class="favoriteIds.has(doc.id) ? 'text-rose-500' : 'text-slate-300 hover:text-rose-500'"
          >
            {{ favoriteIds.has(doc.id) ? '❤️' : '🤍' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选栏 -->
    <div class="mb-6 flex flex-wrap items-center gap-3">
      <!-- 搜索框 -->
      <div class="relative flex-1 min-w-[200px]">
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="搜索文档..."
          class="w-full rounded-xl border border-slate-200/90 bg-white/85 px-4 py-2.5 pl-10 text-sm text-slate-900 placeholder-slate-400 transition focus:border-indigo-300 focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-100 dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-slate-500"
        />
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">🔍</span>
      </div>
      
      <!-- 分类标签 -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="cat in categories"
          :key="cat"
          @click="selectedCategory = cat"
          class="rounded-full px-4 py-1.5 text-xs font-semibold transition"
          :class="selectedCategory === cat 
            ? 'border border-indigo-300 bg-[linear-gradient(135deg,rgba(224,242,254,0.74)_0%,rgba(238,242,255,0.8)_55%,rgba(252,231,243,0.72)_100%)] text-indigo-900 dark:border-indigo-400/40 dark:bg-[linear-gradient(135deg,rgba(30,58,138,0.42)_0%,rgba(67,56,202,0.34)_55%,rgba(131,24,67,0.28)_100%)] dark:text-white' 
            : 'border border-slate-200 bg-white/80 text-slate-600 hover:bg-slate-100 dark:border-white/10 dark:bg-white/10 dark:text-slate-300'"
        >
          {{ cat }}
        </button>
      </div>
      
      <!-- 收藏筛选 -->
      <button
        @click="favoriteOnly = !favoriteOnly"
        class="flex items-center gap-1.5 rounded-full px-4 py-1.5 text-xs font-semibold transition"
        :class="favoriteOnly 
          ? 'border border-rose-300 bg-rose-50 text-rose-700 dark:border-rose-400/40 dark:bg-rose-500/15 dark:text-rose-200' 
          : 'border border-slate-200 bg-white/80 text-slate-600 hover:bg-slate-100 dark:border-white/10 dark:bg-white/10 dark:text-slate-300'"
      >
        <span>❤️</span>
        <span>我的收藏</span>
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="h-8 w-8 animate-spin rounded-full border-3 border-indigo-200 border-t-indigo-600"></div>
      <span class="ml-3 text-sm text-slate-500">正在加载文档库...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="rounded-xl border border-rose-200 bg-rose-50 p-5 text-center dark:border-rose-500/30 dark:bg-rose-500/10">
      <p class="font-semibold text-rose-700 dark:text-rose-200">{{ error }}</p>
      <button 
        @click="$emit('retry')"
        class="mt-3 rounded-lg bg-rose-500 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-600"
      >
        重试
      </button>
    </div>

    <!-- 主内容区 - 文档详情展开区域 -->
    <div v-if="activeDocument" class="space-y-4">
      <!-- 文档详情卡片 -->
      <div 
        class="overflow-hidden rounded-2xl border border-slate-200/85 bg-white shadow-[0_18px_48px_rgba(15,23,42,0.08)] dark:border-white/10 dark:bg-[#0C0F17]"
      >
        <!-- 详情头部 -->
        <div class="relative border-b border-slate-200/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(248,250,252,0.9)_100%)] p-5 text-slate-900 dark:border-white/10 dark:bg-[linear-gradient(180deg,rgba(10,10,15,0.92)_0%,rgba(12,15,23,0.94)_100%)] dark:text-white">
          <div class="absolute -right-6 -top-6 h-28 w-28 rounded-full bg-indigo-200/25 dark:bg-indigo-400/10"></div>
          <div class="relative">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-bold text-slate-700 dark:border-white/10 dark:bg-white/10 dark:text-slate-200">
                  {{ activeDocument.difficulty }}
                </span>
                <span class="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                  ⏱️ {{ activeDocument.read_time }}分钟阅读
                </span>
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="toggleFavorite(activeDocument.id)"
                  class="flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 backdrop-blur-sm transition hover:border-rose-300 hover:text-rose-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-200 dark:hover:border-rose-400/40 dark:hover:text-rose-300"
                >
                  {{ favoriteIds.has(activeDocument.id) ? '❤️ 已收藏' : '🤍 收藏' }}
                </button>
                <button
                  @click="shareDocument(activeDocument)"
                  class="flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 backdrop-blur-sm transition hover:border-indigo-300 hover:text-indigo-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-200 dark:hover:border-indigo-400/40 dark:hover:text-indigo-300"
                >
                  📤 分享
                </button>
              </div>
            </div>
            
            <h2 class="mt-3 text-xl font-black">{{ activeDocument.title }}</h2>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">{{ activeDocument.subtitle }}</p>
            
            <!-- 标签 -->
            <div class="mt-3 flex flex-wrap gap-2">
              <span 
                v-for="tag in activeDocument.tags" 
                :key="tag"
                class="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-xs font-medium text-slate-600 dark:border-white/10 dark:bg-white/10 dark:text-slate-300"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <!-- 文档内容 -->
        <div class="p-5 space-y-5">
          <div 
            v-for="(section) in activeDocument.sections" 
            :key="section.heading"
          >
            <h3 class="text-base font-bold text-slate-900 dark:text-white">{{ section.heading }}</h3>
            
            <div class="mt-2 space-y-2">
              <p 
                v-for="(para, pIdx) in section.paragraphs" 
                :key="pIdx"
                class="text-sm leading-relaxed text-slate-600 dark:text-slate-300"
              >
                {{ para }}
              </p>
            </div>

            <!-- 要点列表 -->
            <ul v-if="section.bullets?.length" class="mt-3 space-y-1.5">
              <li 
                v-for="(bullet, bIdx) in section.bullets" 
                :key="bIdx"
                class="flex items-start gap-2.5 text-sm text-slate-600 dark:text-slate-300"
              >
                <span class="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-500"></span>
                <span>{{ bullet }}</span>
              </li>
            </ul>

            <!-- 行动项 -->
            <div 
              v-if="section.action_items?.length" 
              class="mt-3 rounded-xl bg-indigo-50 p-3 dark:bg-indigo-500/10"
            >
              <h4 class="flex items-center gap-2 text-sm font-bold text-indigo-700 dark:text-indigo-300">
                <span>🎯</span>
                <span>立即行动</span>
              </h4>
              <ul class="mt-2 space-y-1">
                <li 
                  v-for="(item, iIdx) in section.action_items" 
                  :key="iIdx"
                  class="flex items-start gap-2 text-sm text-indigo-600 dark:text-indigo-400"
                >
                  <span class="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400"></span>
                  <span>{{ item }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 相关推荐 -->
        <div v-if="recommendedDocs.length > 0" class="border-t border-slate-200/80 p-4 dark:border-white/10">
          <h4 class="mb-3 flex items-center gap-2 text-sm font-bold text-slate-700 dark:text-slate-200">
            <span>📖</span>
            <span>相关推荐</span>
          </h4>
          <div class="grid gap-2 sm:grid-cols-2">
            <div
              v-for="doc in recommendedDocs"
              :key="doc.id"
              @click="activeDocId = doc.id"
              class="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 p-3 transition hover:border-indigo-300 hover:bg-indigo-50/50 dark:border-white/10 dark:bg-white/5 dark:hover:border-indigo-500/30"
            >
              <div 
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-white text-lg dark:border-white/10 dark:bg-white/10"
              >
                {{ getCategoryIcon(doc.cover_icon) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold text-slate-900 dark:text-white">{{ doc.title }}</p>
                <p class="text-xs text-slate-500">{{ doc.difficulty }} · {{ doc.read_time }}分钟</p>
              </div>
              <span class="text-slate-400">→</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无选中文档时的提示 -->
    <div 
      v-else
      class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/50 py-12 dark:border-slate-600 dark:bg-white/5"
    >
      <p class="text-4xl">📚</p>
      <p class="mt-3 text-sm text-slate-500 dark:text-slate-400">
        {{ filteredDocuments.length ? '点击上方文档卡片查看详情' : '没有符合当前筛选条件的文档' }}
      </p>
    </div>
  </section>
</template>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
