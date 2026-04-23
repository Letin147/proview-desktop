<script setup lang="ts">
import { computed } from 'vue'
import CareerRoadmapPanel from '../../components/career-planning/CareerRoadmapPanel.vue'
import { useCareerPlanningStore } from '../../stores/careerPlanning'

const store = useCareerPlanningStore()

const completedCount = computed(() => store.milestones.filter(m => m.status === 'completed').length)
const progressPercent = computed(() => store.milestones.length ? Math.round((completedCount.value / store.milestones.length) * 100) : 0)
</script>

<template>
  <section class="space-y-5">
    <!-- 页面标题区 -->
    <div class="relative overflow-hidden rounded-3xl border border-slate-200/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(248,250,252,0.9)_100%)] p-6 shadow-[0_18px_48px_rgba(15,23,42,0.08)] dark:border-white/10 dark:bg-[linear-gradient(180deg,rgba(10,10,15,0.92)_0%,rgba(12,15,23,0.94)_100%)]">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-indigo-200/20 dark:bg-indigo-400/10"></div>
      <div class="absolute -bottom-5 -right-5 h-24 w-24 rounded-full bg-sky-200/20 dark:bg-sky-400/10"></div>
      <div class="relative flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">🗺️ 路线图</p>
          <h1 class="mt-2 text-3xl font-black tracking-tight text-slate-900 dark:text-white">按阶段展开目标、里程碑和预期结果</h1>
          <p class="mt-2 max-w-xl text-sm text-slate-600 dark:text-slate-400">这是一条从当前状态到目标岗位的线性路线，适合快速检查每一阶段是否已经按计划推进。</p>
        </div>
        <div class="hidden lg:flex items-center gap-4">
          <div class="text-center">
            <p class="text-3xl font-black text-slate-900 dark:text-white">{{ completedCount }}/{{ store.milestones.length }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">已完成阶段</p>
          </div>
          <div class="h-12 w-12 rounded-full border border-slate-200 bg-white/80 dark:border-white/10 dark:bg-white/10 flex items-center justify-center">
            <span class="text-xl text-indigo-600 dark:text-indigo-300">📍</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 进度概览 -->
    <div class="rounded-2xl border border-slate-200/85 bg-white/85 p-4 backdrop-blur-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.55)] dark:border-white/10 dark:bg-[#0C0F17]/80">
      <div class="flex items-center justify-between mb-2">
        <p class="text-sm font-semibold text-slate-700 dark:text-white">整体进度</p>
        <p class="text-sm font-bold text-indigo-600 dark:text-indigo-400">{{ progressPercent }}%</p>
      </div>
      <div class="h-2.5 overflow-hidden rounded-full bg-slate-200 dark:bg-white/10">
        <div 
          class="h-full rounded-full bg-gradient-to-r from-indigo-500 to-cyan-500 transition-all duration-500"
          :style="{ width: `${progressPercent}%` }"
        ></div>
      </div>
    </div>

    <!-- 路线图面板 -->
    <CareerRoadmapPanel :milestones="store.milestones" />
  </section>
</template>