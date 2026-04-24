<script setup lang="ts">
import { BookOpen, Download, FileText, Sparkles } from 'lucide-vue-next'
</script>

<template>
  <div class="fade-in min-h-full">
    <div class="mb-8">
      <h2 class="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl dark:text-white">
        面经总结
      </h2>
      <p class="mt-2 text-sm font-medium text-slate-500 dark:text-slate-400">AI 自动提炼面试要点，生成结构化面经</p>
    </div>

    <div class="relative rounded-3xl border border-slate-200/60 bg-white/70 p-8 shadow-xl backdrop-blur-xl sm:p-12 dark:border-white/10 dark:bg-[#0A0A0F]/60">
      <div class="mx-auto flex max-w-md flex-col items-center text-center">
        <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10 dark:bg-primary/20">
          <BookOpen class="h-10 w-10 text-primary" />
        </div>

        <h3 class="mb-3 text-xl font-bold text-slate-800 dark:text-white">功能开发中，敬请期待</h3>
        <p class="mb-8 text-sm leading-relaxed text-slate-500 dark:text-slate-400">
          面经总结功能正在紧锣密鼓地开发中，完成后将为你提供以下能力：
        </p>

        <div class="w-full space-y-4 text-left">
          <div class="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-white/5 dark:bg-white/5">
            <Sparkles class="mt-0.5 h-5 w-5 shrink-0 text-amber-500" />
            <div>
              <div class="text-sm font-bold text-slate-700 dark:text-slate-300">AI 自动提炼面试要点</div>
              <div class="mt-1 text-xs text-slate-500 dark:text-slate-400">智能分析面试对话，提取核心知识点和高频考点</div>
            </div>
          </div>

          <div class="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-white/5 dark:bg-white/5">
            <FileText class="mt-0.5 h-5 w-5 shrink-0 text-blue-500" />
            <div>
              <div class="text-sm font-bold text-slate-700 dark:text-slate-300">生成结构化面经</div>
              <div class="mt-1 text-xs text-slate-500 dark:text-slate-400">按题型、难度、知识领域自动归类整理</div>
            </div>
          </div>

          <div class="flex items-start gap-3 rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-white/5 dark:bg-white/5">
            <Download class="mt-0.5 h-5 w-5 shrink-0 text-emerald-500" />
            <div>
              <div class="text-sm font-bold text-slate-700 dark:text-slate-300">支持 Markdown 导出</div>
              <div class="mt-1 text-xs text-slate-500 dark:text-slate-400">一键导出面经文档，方便复习和分享</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
