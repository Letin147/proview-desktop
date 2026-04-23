<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import CareerTaskBoard from '../../components/career-planning/CareerTaskBoard.vue'
import { useCareerPlanningStore } from '../../stores/careerPlanning'

const store = useCareerPlanningStore()
const selectedTaskId = ref<number | null>(null)

watch(
  () => store.tasks,
  () => {
    selectedTaskId.value = store.tasks.find((task) => task.status !== 'completed')?.id || store.tasks[0]?.id || null
  },
  { immediate: true },
)

const stats = computed(() => {
  const total = store.tasks.length
  const completed = store.tasks.filter(t => t.status === 'completed').length
  const inProgress = total - completed
  const avgProgress = total > 0 ? Math.round(store.tasks.reduce((sum, t) => sum + (t.progress || 0), 0) / total) : 0
  return { total, completed, inProgress, avgProgress }
})

async function markTaskComplete(taskId: number) {
  try {
    await store.patchTask(taskId, { status: 'completed', progress: 100, note: '由任务追踪页完成' })
  } catch (error) {
    store.error = error instanceof Error ? error.message : '更新任务失败'
  }
}

async function addProgress(taskId: number) {
  try {
    const task = store.getTaskById(taskId)
    const nextProgress = Math.min(100, (task?.progress || 0) + 25)
    await store.logTask(taskId, { progress: nextProgress, note: '推进了阶段性任务' })
  } catch (error) {
    store.error = error instanceof Error ? error.message : '记录任务进度失败'
  }
}

function handleSelectTask(taskId: number) {
  selectedTaskId.value = taskId
}
</script>

<template>
  <section class="space-y-5">
    <!-- 页面标题区 -->
    <div class="relative overflow-hidden rounded-3xl border border-slate-200/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(248,250,252,0.9)_100%)] p-6 shadow-[0_18px_48px_rgba(15,23,42,0.08)] dark:border-white/10 dark:bg-[linear-gradient(180deg,rgba(10,10,15,0.92)_0%,rgba(12,15,23,0.94)_100%)]">
      <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-indigo-200/20 dark:bg-indigo-400/10"></div>
      <div class="absolute -bottom-5 -right-5 h-24 w-24 rounded-full bg-sky-200/20 dark:bg-sky-400/10"></div>
      <div class="relative flex items-center justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">✅ 任务追踪</p>
          <h1 class="mt-2 text-3xl font-black tracking-tight text-slate-900 dark:text-white">把每个里程碑拆成可执行任务并持续推进</h1>
          <p class="mt-2 max-w-xl text-sm text-slate-600 dark:text-slate-400">聚焦当下正在做的事情，支持单个任务标记完成、推进进度和记录阶段性备注。</p>
        </div>
        <div class="hidden lg:flex items-center gap-3">
          <div class="flex -space-x-2">
            <div class="h-10 w-10 rounded-full border border-slate-200 bg-white/80 dark:border-white/10 dark:bg-white/10 flex items-center justify-center text-lg backdrop-blur-sm">📋</div>
            <div class="h-10 w-10 rounded-full border border-slate-200 bg-white/80 dark:border-white/10 dark:bg-white/10 flex items-center justify-center text-lg backdrop-blur-sm">🎯</div>
            <div class="h-10 w-10 rounded-full border border-slate-200 bg-white/80 dark:border-white/10 dark:bg-white/10 flex items-center justify-center text-lg backdrop-blur-sm">🚀</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计概览卡片 -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-slate-50 to-white p-4 shadow-sm dark:border-white/10 dark:from-[#0C0F17] dark:to-[#0C0F17]/80">
        <div class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-100 text-indigo-600 dark:bg-indigo-500/20 dark:text-indigo-300">
            📋
          </div>
          <div>
            <p class="text-2xl font-black text-slate-900 dark:text-white">{{ stats.total }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">总任务</p>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-emerald-200/80 bg-gradient-to-br from-emerald-50 to-white p-4 shadow-sm dark:border-emerald-500/20 dark:from-emerald-500/10 dark:to-[#0C0F17]">
        <div class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300">
            ✓
          </div>
          <div>
            <p class="text-2xl font-black text-emerald-700 dark:text-emerald-100">{{ stats.completed }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">已完成</p>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-amber-200/80 bg-gradient-to-br from-amber-50 to-white p-4 shadow-sm dark:border-amber-500/20 dark:from-amber-500/10 dark:to-[#0C0F17]">
        <div class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-300">
            ⏳
          </div>
          <div>
            <p class="text-2xl font-black text-amber-700 dark:text-amber-100">{{ stats.inProgress }}</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">进行中</p>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-violet-200/80 bg-gradient-to-br from-violet-50 to-white p-4 shadow-sm dark:border-violet-500/20 dark:from-violet-500/10 dark:to-[#0C0F17]">
        <div class="flex items-center gap-2">
          <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-100 text-violet-600 dark:bg-violet-500/20 dark:text-violet-300">
            📊
          </div>
          <div>
            <p class="text-2xl font-black text-violet-700 dark:text-violet-100">{{ stats.avgProgress }}%</p>
            <p class="text-xs text-slate-500 dark:text-slate-400">平均进度</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 进度条概览 -->
    <div class="rounded-2xl border border-slate-200/85 bg-white/85 p-4 backdrop-blur-sm shadow-[inset_0_1px_0_rgba(255,255,255,0.55)] dark:border-white/10 dark:bg-[#0C0F17]/80">
      <div class="flex items-center justify-between mb-2">
        <p class="text-sm font-semibold text-slate-700 dark:text-white">整体完成进度</p>
        <p class="text-sm font-bold text-emerald-600 dark:text-emerald-400">{{ stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0 }}%</p>
      </div>
      <div class="h-3 overflow-hidden rounded-full bg-slate-200 dark:bg-white/10">
        <div 
          class="h-full rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-500"
          :style="{ width: `${stats.total > 0 ? (stats.completed / stats.total) * 100 : 0}%` }"
        ></div>
      </div>
    </div>

    <!-- 任务看板 -->
    <CareerTaskBoard
      :tasks="store.tasks"
      :selected-task-id="selectedTaskId"
      @select-task="handleSelectTask"
      @complete-task="markTaskComplete"
      @add-progress="addProgress"
    />
  </section>
</template>