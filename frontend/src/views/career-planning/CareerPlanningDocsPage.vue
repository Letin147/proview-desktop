<script setup lang="ts">
import CareerDocsPanel from '../../components/career-planning/CareerDocsPanel.vue'
import { useCareerPlanningStore } from '../../stores/careerPlanning'
import { onMounted } from 'vue'

const store = useCareerPlanningStore()

onMounted(() => {
  // 如果文档还没有加载，则加载
  if (!store.documents.length && !store.docsLoading) {
    store.loadDocs()
  }
})
</script>

<template>
  <section class="space-y-4">
    <!-- 页面介绍卡片 -->
    <div class="rounded-3xl border border-slate-200/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(248,250,252,0.9)_100%)] p-6 text-slate-900 shadow-[0_18px_48px_rgba(15,23,42,0.08)] dark:border-white/10 dark:bg-[linear-gradient(180deg,rgba(10,10,15,0.92)_0%,rgba(12,15,23,0.94)_100%)] dark:text-white">
      <div class="flex items-start justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">📚 学习中心</p>
          <h2 class="mt-2 text-2xl font-black text-slate-900 dark:text-white">ProView AI 面试学习资源库</h2>
          <p class="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600 dark:text-slate-400">
            从求职指南到AI面试技巧，从职业规划到发展路径——我们为你在每个阶段准备了最实用的学习资源。
            每份文档都配有可执行的行动项，帮助你将知识转化为实际行动。
          </p>
        </div>
        <div class="hidden md:flex shrink-0">
          <div class="flex -space-x-3">
            <div class="h-10 w-10 rounded-full border border-slate-200 bg-white/80 dark:border-white/10 dark:bg-white/10 flex items-center justify-center text-lg">🎯</div>
            <div class="h-10 w-10 rounded-full border border-slate-200 bg-white/80 dark:border-white/10 dark:bg-white/10 flex items-center justify-center text-lg">📊</div>
            <div class="h-10 w-10 rounded-full border border-slate-200 bg-white/80 dark:border-white/10 dark:bg-white/10 flex items-center justify-center text-lg">🚀</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档库组件 -->
    <CareerDocsPanel 
      :documents="store.documents" 
      :loading="store.docsLoading" 
      :error="store.docsError" 
      @retry="store.loadDocs({ force: true })"
    />
  </section>
</template>
