<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BookOpen, LayoutDashboard, ListTodo, Map, Sparkles } from 'lucide-vue-next'
import { useCareerPlanningStore } from '../stores/careerPlanning'

const store = useCareerPlanningStore()
const route = useRoute()
const router = useRouter()

const tabs = [
  { name: 'career-planning-overview', label: '总览页面', icon: LayoutDashboard },
  { name: 'career-planning-roadmap', label: '路线图页面', icon: Map },
  { name: 'career-planning-tasks', label: '任务追踪页面', icon: ListTodo },
  { name: 'career-planning-docs', label: '文档库页面', icon: BookOpen },
] as const

type CareerPlanningTab = (typeof tabs)[number]

const currentTab = computed<CareerPlanningTab>(() => {
  const routeName = typeof route.name === 'string' ? route.name : ''
  return tabs.find((tab) => tab.name === routeName) || tabs[0]
})

function goTo(routeName: CareerPlanningTab['name']) {
  if (route.name === routeName) return
  router.push({ name: routeName })
}

onMounted(async () => {
  await Promise.all([
    store.loadDashboard(),
    store.loadDocs(),
  ])
})
</script>

<template>
  <div class="space-y-6 pb-6">
    <section class="relative overflow-hidden rounded-3xl border border-slate-200/85 bg-[linear-gradient(180deg,rgba(255,255,255,0.9)_0%,rgba(248,250,252,0.9)_100%)] p-6 shadow-[0_18px_48px_rgba(15,23,42,0.08)] backdrop-blur dark:border-white/10 dark:bg-[linear-gradient(180deg,rgba(10,10,15,0.92)_0%,rgba(12,15,23,0.94)_100%)]">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_rgba(129,140,248,0.12),_transparent_36%),radial-gradient(circle_at_bottom_left,_rgba(56,189,248,0.1),_transparent_30%)]"></div>
      <div class="relative flex flex-col gap-5">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="space-y-2">
            <div class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm font-semibold text-slate-700 dark:border-white/10 dark:bg-white/5 dark:text-slate-200">
              <Sparkles class="h-4 w-4" />
              职业规划工作台
            </div>
            <div>
              <h1 class="text-3xl font-black tracking-tight text-slate-900 dark:text-white sm:text-4xl">开启你的职业发展之旅 🚀</h1>
              <p class="mt-3 max-w-4xl text-sm leading-7 text-slate-600 dark:text-slate-400">从目标岗位到技能提升，从任务追踪到学习资源——我们陪你一起规划职业未来。</p>
            </div>
          </div>

          <div class="grid min-w-[240px] gap-3 rounded-3xl border border-slate-200/85 bg-white/80 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.6)] dark:border-white/10 dark:bg-white/5">
            <div class="flex items-center justify-between gap-3">
              <span class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">当前子页面</span>
              <span class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700 dark:border-white/10 dark:bg-white/10 dark:text-slate-200">{{ currentTab.label }}</span>
            </div>
            <div class="grid gap-2 text-sm text-slate-600 dark:text-slate-400">
              <div class="flex items-center justify-between">
                <span>规划状态</span>
                <span class="font-semibold text-slate-900 dark:text-white">{{ store.currentPlan?.status || '未生成' }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span>任务总数</span>
                <span class="font-semibold text-slate-900 dark:text-white">{{ store.stats.active_task_count }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span>完成率</span>
                <span class="font-semibold text-slate-900 dark:text-white">{{ store.stats.progress_rate }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="grid gap-2 rounded-2xl border border-slate-200/90 bg-white/75 p-2 dark:border-white/10 dark:bg-white/5 sm:grid-cols-4">
          <button
            v-for="tab in tabs"
            :key="tab.name"
            @click="goTo(tab.name)"
            class="inline-flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold transition"
            :class="currentTab.name === tab.name
              ? 'border border-indigo-300 bg-[linear-gradient(135deg,rgba(224,242,254,0.74)_0%,rgba(238,242,255,0.8)_55%,rgba(252,231,243,0.72)_100%)] text-indigo-900 shadow-[0_14px_30px_rgba(79,70,229,0.12)] dark:border-indigo-400/40 dark:bg-[linear-gradient(135deg,rgba(30,58,138,0.42)_0%,rgba(67,56,202,0.34)_55%,rgba(131,24,67,0.28)_100%)] dark:text-white'
              : 'text-slate-600 hover:bg-white hover:text-slate-900 dark:text-slate-300 dark:hover:bg-white/10 dark:hover:text-white'"
          >
            <component :is="tab.icon" class="h-4 w-4" />
            {{ tab.label }}
          </button>
        </div>

        <section v-if="store.error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200">
          {{ store.error }}
        </section>
      </div>
    </section>

    <router-view />
  </div>
</template>