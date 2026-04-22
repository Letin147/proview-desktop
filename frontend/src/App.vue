<script setup lang="ts">
import { ref, computed, onBeforeUnmount, onMounted, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from './stores/theme'
import { useInterviewStore } from './stores/interview'
import { useAuthStore } from './stores/auth'
import BlobBackground from './components/BlobBackground.vue'
import {
  Bot, Settings,
  Sun, Moon, ArrowLeft, MessageSquare, BookOpen, Sparkles, FilePlus2, History, FileUser, ChevronLeft, ChevronRight,
  SlidersHorizontal, ClipboardList, Map
} from 'lucide-vue-next'

const CatLoading = defineAsyncComponent(() => import('./components/CatLoading.vue'))

const theme = useThemeStore()
const interview = useInterviewStore()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const isRouteLoading = ref(false)
const pendingRouteName = ref('')
const SIDEBAR_COLLAPSED_KEY = 'proview:sidebar-collapsed'
const isSidebarCollapsed = ref(localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1')
let routeLoadingTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  interview.rehydrateInterviewSession()
})

const isGuestPage = computed(() => route.meta.guest === true)

const routeLoadingMessageMap: Record<string, string> = {
  'runtime-config': '正在加载接口配置页...',
  setup: '正在加载面试配置页...',
  interview: '正在进入面试房间...',
  report: '正在加载评估报告...',
  'report-history': '正在加载历史报告...',
  summary: '正在整理面经总结...',
  history: '正在加载面试历史...',
  'history-detail': '正在打开历史详情...',
  'resume-optimizer': '正在加载简历优化页...',
  'resume-builder': '正在加载简历生成页...',
  'my-resumes': '正在加载我的简历...',
  'career-planning': '正在加载职业规划工作台...',
  'career-planning-overview': '正在加载职业规划总览页...',
  'career-planning-roadmap': '正在加载职业规划路线图页...',
  'career-planning-tasks': '正在加载职业规划任务页...',
  'career-planning-docs': '正在加载职业规划文档页...',
}

const routeLoadingMessage = computed(() => {
  const routeName = pendingRouteName.value || (typeof route.name === 'string' ? route.name : '')
  return routeLoadingMessageMap[routeName] || '页面加载中，请稍候...'
})

const routeLoadingStage = computed(() => (
  route.meta.guest ? '正在准备页面资源' : '你仍然可以继续滚动和查看当前界面'
))

function clearRouteLoadingTimer() {
  if (routeLoadingTimer) {
    clearTimeout(routeLoadingTimer)
    routeLoadingTimer = null
  }
}

function startRouteLoading(routeName = '') {
  pendingRouteName.value = routeName
  clearRouteLoadingTimer()
  routeLoadingTimer = setTimeout(() => {
    isRouteLoading.value = true
  }, 120)
}

function finishRouteLoading() {
  clearRouteLoadingTimer()
  isRouteLoading.value = false
  pendingRouteName.value = ''
}

const removeRouteErrorHandler = router.onError(() => {
  finishRouteLoading()
})

const removeRouteLoadingStart = router.beforeEach((to, from) => {
  if (!from.matched.length || to.fullPath === from.fullPath) return
  startRouteLoading(typeof to.name === 'string' ? to.name : '')
})

const removeRouteLoadingEnd = router.afterEach(() => {
  finishRouteLoading()
})

const navItems = computed(() => [
  { name: 'setup', icon: SlidersHorizontal, label: '面试配置', path: '/', group: '面试流程' },
  { name: 'history', icon: History, label: '面试历史', path: '/history', group: '面试流程' },
  { name: 'interview', icon: MessageSquare, label: '面试房间', path: '/interview', disabled: !interview.canEnterInterviewRoom, group: '面试流程' },
  { name: 'report', icon: ClipboardList, label: '评估报告', path: '/report', group: '面试流程' },
  { name: 'summary', icon: BookOpen, label: '面经总结', path: '/summary', group: '面试流程' },
  { name: 'runtime-config', icon: Settings, label: '接口配置', path: '/config', group: '工具箱' },
  { name: 'resume-optimizer', icon: Sparkles, label: '简历优化', path: '/resume-optimizer', group: '工具箱' },
  { name: 'resume-builder', icon: FilePlus2, label: '简历生成', path: '/resume-builder', group: '工具箱' },
  { name: 'my-resumes', icon: FileUser, label: '我的简历', path: '/my-resumes', group: '工具箱' },
  { name: 'career-planning', icon: Map, label: '职业规划', routeName: 'career-planning-overview', path: '/career-planning/overview', group: '工具箱' },
])

const currentNav = computed(() => {
  if (route.name === 'interview') return 'interview'
  if (route.name === 'report' || route.name === 'report-history') return 'report'
  if (route.name === 'summary') return 'summary'
  if (route.name === 'runtime-config') return 'runtime-config'
  if (route.name === 'history' || route.name === 'history-detail') return 'history'
  if (route.name === 'resume-optimizer') return 'resume-optimizer'
  if (route.name === 'resume-builder') return 'resume-builder'
  if (route.name === 'my-resumes') return 'my-resumes'
  if (typeof route.name === 'string' && route.name.startsWith('career-planning')) return 'career-planning'
  return 'setup'
})

function navigateTo(item: { name?: string; path: string; routeName?: string; disabled?: boolean }) {
  if (item.disabled) return
  const targetName = item.routeName || item.name || ''
  const targetPath = item.path
  if ((targetName && route.name === targetName) || (!targetName && route.path === targetPath)) {
    return
  }

  startRouteLoading(targetName)

  if (item.routeName) {
    router.push({ name: item.routeName }).catch(() => finishRouteLoading())
    return
  }
  router.push(item.path).catch(() => finishRouteLoading())
}

function getNavItemClass(item: { name: string; disabled?: boolean }, activeClass: string, idleClass: string, disabledClass: string) {
  if (currentNav.value === item.name) return activeClass
  if (item.disabled) return disabledClass
  return idleClass
}

function handleThemeToggle(e: MouseEvent) {
  theme.toggle(e.currentTarget as HTMLElement)
}

function goLanding() {
  const currentPageUrl = window.location.href.split('#')[0]
  const landingUrl = new URL('index.html', currentPageUrl)
  window.location.assign(landingUrl.toString())
}

function openSettings() {
  if (route.name === 'runtime-config') return
  router.push('/config')
}

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, isSidebarCollapsed.value ? '1' : '0')
}

onBeforeUnmount(() => {
  clearRouteLoadingTimer()
  removeRouteErrorHandler()
  removeRouteLoadingStart()
  removeRouteLoadingEnd()
})
</script>

<template>
  <div class="app-shell flex h-screen w-full overflow-hidden font-sans text-slate-900 transition-colors duration-500 dark:text-slate-300">

    <!-- ================== PC端：左侧边栏 ================== -->
    <aside
      v-if="!isGuestPage"
      class="app-sidebar z-20 hidden min-h-0 flex-col overflow-hidden transition-[width] duration-300 md:flex"
      :class="isSidebarCollapsed ? 'w-[92px]' : 'w-[280px]'"
    >
      <!-- Logo -->
      <div class="app-sidebar__header flex h-20 shrink-0 items-center" :class="isSidebarCollapsed ? 'px-3' : 'px-6'">
        <div class="flex min-w-0 flex-1 items-center" :class="isSidebarCollapsed ? 'justify-center' : 'gap-3'">
          <div class="app-logo-mark flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl text-white">
            <Bot class="w-5 h-5" />
          </div>
          <span
            v-if="!isSidebarCollapsed"
            class="app-logo-text truncate text-xl font-extrabold tracking-wide"
          >
            ProView AI
          </span>
        </div>
        <button
          type="button"
          class="app-icon-control inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl"
          :title="isSidebarCollapsed ? '展开导航栏' : '折叠导航栏'"
          @click="toggleSidebar"
        >
          <ChevronRight v-if="isSidebarCollapsed" class="h-4 w-4" />
          <ChevronLeft v-else class="h-4 w-4" />
        </button>
      </div>

      <div class="custom-scroll min-h-0 flex-1 overflow-y-auto overscroll-contain">
        <div class="px-4 pt-4">
          <button
            type="button"
            @click="handleThemeToggle"
            class="app-sidebar-pill flex w-full items-center py-3 text-sm font-semibold"
            :class="isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4'"
            :title="theme.isDark ? '切换到浅色模式' : '切换到深色模式'"
          >
            <Sun v-if="theme.isDark" class="w-5 h-5 text-amber-400" />
            <Moon v-else class="w-5 h-5" />
            <span v-if="!isSidebarCollapsed">{{ theme.isDark ? '浅色模式' : '深色模式' }}</span>
          </button>
        </div>

        <!-- 导航菜单 -->
        <nav class="mt-5 flex flex-col gap-2 px-4 pb-4">
          <div v-if="!isSidebarCollapsed" class="app-nav-group-title mb-2 px-2">面试流程</div>
          <button
            v-for="item in navItems.filter(i => i.group === '面试流程')" :key="item.name"
            @click="navigateTo(item)"
            class="app-nav-button group flex items-center py-3 text-sm font-bold"
            :class="[
              isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4',
              getNavItemClass(
                item,
                'app-nav-button--active',
                'app-nav-button--idle',
                'app-nav-button--disabled'
              )
            ]"
            :disabled="item.disabled"
            :title="isSidebarCollapsed ? item.label : undefined"
          >
            <component :is="item.icon" class="w-5 h-5 transition-transform group-hover:scale-110" />
            <span v-if="!isSidebarCollapsed">{{ item.label }}</span>
          </button>
          <div v-if="!isSidebarCollapsed" class="app-nav-group-title mt-4 mb-2 px-2">工具箱</div>
          <button
            v-for="item in navItems.filter(i => i.group === '工具箱')" :key="item.name"
            @click="navigateTo(item)"
            class="app-nav-button group flex items-center py-3 text-sm font-bold"
            :class="[
              isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4',
              getNavItemClass(
                item,
                'app-nav-button--active',
                'app-nav-button--idle',
                'app-nav-button--disabled'
              )
            ]"
            :disabled="item.disabled"
            :title="isSidebarCollapsed ? item.label : undefined"
          >
            <component :is="item.icon" class="w-5 h-5 transition-transform group-hover:scale-110" />
            <span v-if="!isSidebarCollapsed">{{ item.label }}</span>
          </button>
        </nav>
      </div>

      <!-- 底部控制 -->
      <div class="app-sidebar__footer shrink-0 space-y-2 p-4">
        <button
          @click="goLanding"
          class="app-sidebar-pill flex w-full items-center py-3 text-sm font-semibold"
          :class="isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4'"
          :title="isSidebarCollapsed ? '返回介绍页' : undefined"
        >
          <ArrowLeft class="w-5 h-5" />
          <span v-if="!isSidebarCollapsed">返回介绍页</span>
        </button>
        <button
          @click="openSettings"
          class="app-sidebar-pill flex w-full items-center py-3 text-sm font-semibold"
          :class="isSidebarCollapsed ? 'justify-center px-3' : 'gap-3 px-4'"
          :title="isSidebarCollapsed ? '应用设置' : undefined"
        >
          <Settings class="w-5 h-5" />
          <span v-if="!isSidebarCollapsed">应用设置</span>
        </button>
        <div class="app-user-card rounded-[24px] py-3" :class="isSidebarCollapsed ? 'px-3' : 'px-4'">
          <div class="flex items-center" :class="isSidebarCollapsed ? 'justify-center' : 'gap-3'">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-md shadow-emerald-500/20">
              <Bot class="h-4 w-4" />
            </div>
            <div v-if="!isSidebarCollapsed" class="min-w-0">
              <p class="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">单机模式</p>
              <p class="mt-1 truncate text-sm font-semibold text-slate-700 dark:text-slate-200">{{ auth.user?.display_name || auth.user?.username || '本地用户' }}</p>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- ================== 移动端：底部 Tab ================== -->
    <nav v-if="!isGuestPage" class="app-mobile-nav fixed bottom-0 left-0 right-0 z-50 pb-2 pt-2 md:hidden">
      <div class="flex justify-around">
        <button
          v-for="item in navItems" :key="item.name"
          @click="navigateTo(item)"
          class="app-mobile-tab flex flex-col items-center p-2"
          :class="getNavItemClass(
            item,
            'app-mobile-tab--active',
            'app-mobile-tab--idle',
            'app-mobile-tab--disabled'
          )"
          :disabled="item.disabled"
        >
          <component :is="item.icon" class="mb-1 w-5 h-5" />
          <span class="text-[10px] font-bold">{{ item.label }}</span>
        </button>
        <button @click="goLanding" class="app-mobile-tab app-mobile-tab--idle flex flex-col items-center p-2">
          <ArrowLeft class="mb-1 w-5 h-5" />
          <span class="text-[10px] font-bold">介绍页</span>
        </button>
      </div>
    </nav>

    <!-- ================== 右侧主内容区 ================== -->
    <main class="app-main custom-scroll relative z-10 min-h-0 flex-1 overflow-y-auto overscroll-contain pb-20 md:pb-0">
      <BlobBackground />
      <div class="relative z-10 min-h-full">
        <div v-if="!isGuestPage" class="pointer-events-none absolute left-4 top-4 z-20 md:hidden">
          <button
            type="button"
            class="app-top-icon pointer-events-auto inline-flex h-11 w-11 items-center justify-center rounded-full"
            :title="theme.isDark ? '切换到浅色模式' : '切换到深色模式'"
            @click="handleThemeToggle"
          >
            <Sun v-if="theme.isDark" class="h-5 w-5 text-amber-400" />
            <Moon v-else class="h-5 w-5" />
          </button>
        </div>
        <div v-if="!isGuestPage" class="pointer-events-none absolute right-4 top-4 z-20 flex items-center gap-3">
          <div class="app-top-chip pointer-events-auto hidden items-center gap-3 rounded-full px-4 py-2 text-sm md:flex">
            <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
            <span class="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">单机模式</span>
            <span class="max-w-[180px] truncate font-semibold">{{ auth.user?.display_name || auth.user?.username || '本地用户' }}</span>
          </div>
          <button
            type="button"
            class="app-top-chip pointer-events-auto inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold"
            @click="openSettings"
          >
            <Settings class="h-4 w-4" />
            <span class="hidden sm:inline">设置</span>
          </button>
        </div>
        <div
          class="container mx-auto max-w-7xl px-4 sm:px-8"
          :class="isGuestPage ? 'py-8' : 'pb-8 pt-24 md:py-8'"
        >
          <router-view v-slot="{ Component, route: viewRoute }">
            <keep-alive :include="['InterviewView']">
              <component :is="Component" :key="viewRoute.fullPath" />
            </keep-alive>
          </router-view>
        </div>
      </div>
    </main>

    <CatLoading
      v-if="isRouteLoading"
      variant="corner"
      :blocking="false"
      :message="routeLoadingMessage"
      :stage="routeLoadingStage"
    />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.app-shell {
  background:
    radial-gradient(920px circle at -10% -12%, rgba(251, 191, 36, 0.14), transparent 46%),
    radial-gradient(860px circle at 108% 4%, rgba(56, 189, 248, 0.12), transparent 48%),
    linear-gradient(135deg, rgba(255, 248, 238, 0.72) 0%, rgba(255, 255, 255, 0.54) 46%, rgba(239, 247, 255, 0.6) 100%);
}

.app-sidebar {
  position: relative;
  border-right: 1px solid rgba(226, 232, 240, 0.75);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.88) 0%, rgba(248, 250, 252, 0.9) 100%);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  box-shadow:
    0 18px 48px rgba(15, 23, 42, 0.08),
    inset -1px 0 0 rgba(255, 255, 255, 0.6);
}

.app-sidebar::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(120% 100% at 0% 0%, rgba(251, 191, 36, 0.08), transparent 34%),
    radial-gradient(110% 100% at 100% 18%, rgba(99, 102, 241, 0.08), transparent 36%),
    radial-gradient(120% 100% at 50% 100%, rgba(244, 114, 182, 0.06), transparent 28%);
}

.app-sidebar__header {
  position: relative;
  border-bottom: 1px solid rgba(226, 232, 240, 0.68);
}

.app-sidebar__header::after {
  content: '';
  position: absolute;
  left: 1.25rem;
  right: 1.25rem;
  bottom: -1px;
  height: 1px;
  border-radius: 9999px;
  background: linear-gradient(90deg, rgba(251, 191, 36, 0.15), rgba(99, 102, 241, 0.18), rgba(244, 114, 182, 0.12));
}

.app-logo-mark {
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 55%, #ec4899 100%);
  box-shadow:
    0 14px 30px rgba(79, 70, 229, 0.2),
    0 8px 18px rgba(59, 130, 246, 0.16);
}

.app-logo-text {
  color: transparent;
  background-image: linear-gradient(90deg, #1d4ed8 0%, #4f46e5 52%, #be185d 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.app-icon-control,
.app-sidebar-pill,
.app-top-chip,
.app-top-icon {
  border: 1px solid rgba(226, 232, 240, 0.92);
  background: rgba(255, 255, 255, 0.82);
  color: #475569;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease,
    color 180ms ease,
    background-color 180ms ease;
}

.app-icon-control:hover,
.app-sidebar-pill:hover,
.app-top-chip:hover,
.app-top-icon:hover {
  transform: translateY(-1px);
  border-color: rgba(129, 140, 248, 0.42);
  color: #4f46e5;
  box-shadow: 0 14px 30px rgba(79, 70, 229, 0.12);
}

.app-nav-group-title {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #94a3b8;
}

.app-nav-button {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  text-align: left;
  transition:
    transform 220ms ease,
    color 220ms ease,
    background-color 220ms ease,
    box-shadow 220ms ease,
    border-color 220ms ease;
}

.app-nav-button--idle {
  color: #64748b;
}

.app-nav-button--idle:hover {
  transform: translateY(-1px);
  color: #334155;
  background:
    linear-gradient(90deg, rgba(240, 249, 255, 0.42) 0%, rgba(245, 243, 255, 0.36) 100%);
}

.app-nav-button--idle::before {
  content: '';
  position: absolute;
  left: 0.4rem;
  top: 50%;
  width: 2px;
  height: 0;
  border-radius: 9999px;
  transform: translateY(-50%);
  background: linear-gradient(180deg, #38bdf8, #818cf8, #f472b6);
  opacity: 0;
  transition: height 220ms ease, opacity 220ms ease;
}

.app-nav-button--idle:hover::before {
  height: 60%;
  opacity: 0.7;
}

.app-nav-button--active {
  color: #1e3a8a;
  background:
    linear-gradient(135deg, rgba(224, 242, 254, 0.72) 0%, rgba(238, 242, 255, 0.78) 52%, rgba(252, 231, 243, 0.66) 100%);
  box-shadow:
    0 12px 28px rgba(79, 70, 229, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.65);
}

.app-nav-button--active::before {
  content: '';
  position: absolute;
  left: 0.35rem;
  top: 50%;
  width: 3px;
  height: 74%;
  border-radius: 9999px;
  transform: translateY(-50%);
  background: linear-gradient(180deg, #38bdf8, #818cf8, #f472b6);
  box-shadow: 0 0 14px rgba(129, 140, 248, 0.35);
}

.app-nav-button--disabled {
  color: #cbd5e1;
  cursor: not-allowed;
}

.app-nav-button--disabled:hover {
  transform: none;
  color: #cbd5e1;
  background: transparent;
  box-shadow: none;
}

.app-sidebar__footer {
  position: relative;
  border-top: 1px solid rgba(226, 232, 240, 0.68);
}

.app-user-card {
  border: 1px solid rgba(226, 232, 240, 0.92);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.82) 0%, rgba(248, 250, 252, 0.92) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.app-mobile-nav {
  border-top: 1px solid rgba(226, 232, 240, 0.82);
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: 0 -10px 30px rgba(15, 23, 42, 0.08);
}

.app-mobile-tab {
  position: relative;
  transition: color 180ms ease, transform 180ms ease;
}

.app-mobile-tab--active {
  color: #4f46e5;
}

.app-mobile-tab--active::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -2px;
  width: 24px;
  height: 3px;
  border-radius: 9999px;
  transform: translateX(-50%);
  background: linear-gradient(90deg, #38bdf8, #818cf8, #f472b6);
}

.app-mobile-tab--idle {
  color: #64748b;
}

.app-mobile-tab--idle:hover {
  color: #334155;
  transform: translateY(-1px);
}

.app-mobile-tab--disabled {
  color: #cbd5e1;
}

.app-main {
  background: transparent;
}

:global(html.dark) .app-shell {
  background:
    radial-gradient(920px circle at -10% -12%, rgba(56, 189, 248, 0.14), transparent 44%),
    radial-gradient(840px circle at 108% 4%, rgba(129, 140, 248, 0.14), transparent 46%),
    linear-gradient(160deg, rgba(5, 6, 13, 0.96) 0%, rgba(11, 16, 32, 0.95) 52%, rgba(7, 11, 22, 0.96) 100%);
}

:global(html.dark) .app-sidebar {
  border-right-color: rgba(255, 255, 255, 0.08);
  background:
    linear-gradient(180deg, rgba(10, 10, 15, 0.92) 0%, rgba(12, 15, 23, 0.94) 100%);
  box-shadow:
    0 18px 42px rgba(0, 0, 0, 0.38),
    inset -1px 0 0 rgba(255, 255, 255, 0.03);
}

:global(html.dark) .app-sidebar__header,
:global(html.dark) .app-sidebar__footer {
  border-color: rgba(255, 255, 255, 0.08);
}

:global(html.dark) .app-logo-text {
  background-image: linear-gradient(90deg, #ffffff 0%, #c4b5fd 46%, #7dd3fc 100%);
}

:global(html.dark) .app-icon-control,
:global(html.dark) .app-sidebar-pill,
:global(html.dark) .app-top-chip,
:global(html.dark) .app-top-icon,
:global(html.dark) .app-user-card {
  border-color: rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: #cbd5e1;
}

:global(html.dark) .app-icon-control:hover,
:global(html.dark) .app-sidebar-pill:hover,
:global(html.dark) .app-top-chip:hover,
:global(html.dark) .app-top-icon:hover {
  border-color: rgba(129, 140, 248, 0.4);
  color: #c4b5fd;
  box-shadow: 0 16px 30px rgba(0, 0, 0, 0.28);
}

:global(html.dark) .app-nav-group-title {
  color: #64748b;
}

:global(html.dark) .app-nav-button--idle {
  color: #94a3b8;
}

:global(html.dark) .app-nav-button--idle:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.06);
}

:global(html.dark) .app-nav-button--active {
  color: #c4b5fd;
  background:
    linear-gradient(135deg, rgba(30, 58, 138, 0.4) 0%, rgba(67, 56, 202, 0.34) 52%, rgba(131, 24, 67, 0.28) 100%);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.28);
}

:global(html.dark) .app-nav-button--disabled {
  color: #475569;
}

:global(html.dark) .app-mobile-nav {
  border-top-color: rgba(255, 255, 255, 0.08);
  background: rgba(10, 10, 15, 0.9);
  box-shadow: 0 -12px 32px rgba(0, 0, 0, 0.3);
}

:global(html.dark) .app-mobile-tab--idle {
  color: #94a3b8;
}

:global(html.dark) .app-mobile-tab--idle:hover {
  color: #e2e8f0;
}
</style>
