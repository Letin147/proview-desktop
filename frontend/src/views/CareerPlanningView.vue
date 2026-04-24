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
  <div class="career-shell space-y-6 pb-6">
    <section class="career-shell__hero ui-card">
      <div class="career-shell__copy">
        <span class="ui-section-badge">
          <Sparkles class="h-4 w-4" />
          职业规划工作台
        </span>
        <h1 class="ui-page-title mt-4 text-3xl sm:text-4xl">把目标岗位拆成路线、任务和学习材料</h1>
        <p class="ui-page-subtitle mt-3 max-w-4xl text-sm leading-7">
          这里承接你的面试结果、当前简历状态和目标岗位方向，把职业规划拆成可以持续推进的执行面板。
        </p>
      </div>

      <div class="career-shell__summary">
        <div class="career-shell__current">
          <span class="career-shell__current-label">当前页面</span>
          <strong class="career-shell__current-value">{{ currentTab.label }}</strong>
        </div>

        <div class="career-shell__metrics">
          <div class="career-shell__metric">
            <span class="career-shell__metric-label">规划状态</span>
            <strong class="career-shell__metric-value">{{ store.currentPlan?.status || '未生成' }}</strong>
          </div>
          <div class="career-shell__metric">
            <span class="career-shell__metric-label">任务总数</span>
            <strong class="career-shell__metric-value">{{ store.stats.active_task_count }}</strong>
          </div>
          <div class="career-shell__metric">
            <span class="career-shell__metric-label">完成率</span>
            <strong class="career-shell__metric-value">{{ store.stats.progress_rate }}%</strong>
          </div>
        </div>
      </div>
    </section>

    <section class="career-shell__tabs ui-card-soft">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        @click="goTo(tab.name)"
        class="career-shell__tab"
        :class="{ 'career-shell__tab--active': currentTab.name === tab.name }"
      >
        <component :is="tab.icon" class="h-4 w-4" />
        {{ tab.label }}
      </button>
    </section>

    <section v-if="store.error" class="career-shell__error ui-card-soft">
      {{ store.error }}
    </section>

    <router-view />
  </div>
</template>

<style scoped>
.career-shell__hero {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(260px, 0.8fr);
  gap: 1.25rem;
  padding: 1.6rem;
}

.career-shell__hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 12% 18%, rgba(59, 130, 246, 0.14), transparent 28%),
    radial-gradient(circle at 88% 20%, rgba(99, 102, 241, 0.12), transparent 24%);
  pointer-events: none;
}

.career-shell__copy,
.career-shell__summary {
  position: relative;
  z-index: 1;
}

.career-shell__summary {
  display: grid;
  gap: 0.9rem;
  align-content: end;
}

.career-shell__current,
.career-shell__metric {
  border-radius: 1.3rem;
  border: 1px solid var(--ui-border-subtle);
  background: var(--ui-surface-raised);
  box-shadow: var(--ui-shadow-sm);
}

.career-shell__current {
  padding: 1rem;
}

.career-shell__current-label,
.career-shell__metric-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ui-text-muted);
}

.career-shell__current-value,
.career-shell__metric-value {
  display: block;
  margin-top: 0.4rem;
  font-size: 1rem;
  font-weight: 900;
  color: var(--ui-text-primary);
}

.career-shell__metrics {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.career-shell__metric {
  padding: 0.95rem;
}

.career-shell__tabs {
  display: grid;
  gap: 0.6rem;
  padding: 0.55rem;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.career-shell__tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  border-radius: 1rem;
  border: 1px solid transparent;
  padding: 0.95rem 1rem;
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--ui-text-secondary);
  transition:
    background-color 180ms ease,
    border-color 180ms ease,
    color 180ms ease,
    box-shadow 180ms ease;
}

.career-shell__tab:hover {
  background: var(--ui-surface-raised);
  color: var(--ui-text-primary);
}

.career-shell__tab--active {
  border-color: var(--ui-border-strong);
  background: var(--ui-accent-soft);
  color: var(--ui-accent-strong);
  box-shadow: var(--ui-shadow-sm);
}

.career-shell__error {
  padding: 0.95rem 1rem;
  color: var(--ui-danger);
  font-size: 0.92rem;
  font-weight: 700;
}

.dark .career-shell__current,
.dark .career-shell__metric {
  background: rgba(15, 23, 42, 0.72);
}

@media (max-width: 960px) {
  .career-shell__hero,
  .career-shell__tabs {
    grid-template-columns: 1fr;
  }

  .career-shell__metrics {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .career-shell__metrics {
    grid-template-columns: 1fr;
  }
}
</style>
