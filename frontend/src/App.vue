<script setup lang="ts">
import { ref, computed, onBeforeUnmount, onMounted, defineAsyncComponent } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useThemeStore } from './stores/theme'
import { useInterviewStore } from './stores/interview'
import BlobBackground from './components/BlobBackground.vue'
import {
  Bot, Settings,
  Sun, Moon, ArrowLeft, MessageSquare, BookOpen, Sparkles, FilePlus2, History, FileUser, ChevronLeft,
  SlidersHorizontal, ClipboardList, Map
} from 'lucide-vue-next'

const CatLoading = defineAsyncComponent(() => import('./components/CatLoading.vue'))

const theme = useThemeStore()
const interview = useInterviewStore()
const router = useRouter()
const route = useRoute()
const isRouteLoading = ref(false)
const pendingRouteName = ref('')
const isDesktop = typeof window !== 'undefined' && Boolean(window.proviewDesktop?.isDesktop)
const SIDEBAR_COLLAPSED_KEY = 'proview:sidebar-collapsed'
const DESKTOP_ZOOM_KEY = 'proview:desktop-zoom-factor'
const DESKTOP_ZOOM_MIN = 0.8
const DESKTOP_ZOOM_MAX = 1.15
const DESKTOP_ZOOM_STEP = 0.05
const isSidebarCollapsed = ref(localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === '1')
const desktopZoomFactor = ref(1)
let routeLoadingTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  interview.rehydrateInterviewSession()
  if (!isDesktop) {
    return
  }

  const storedZoom = Number.parseFloat(localStorage.getItem(DESKTOP_ZOOM_KEY) || '')
  const initialZoom = Number.isFinite(storedZoom)
    ? storedZoom
    : (window.proviewDesktop?.getZoomFactor?.() || 1)

  applyDesktopZoom(initialZoom)
})

const isGuestPage = computed(() => route.meta.guest === true)

const routeLoadingMessageMap: Record<string, string> = {
  'runtime-config': '正在加载应用设置页...',
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
const desktopZoomPercent = computed(() => `${Math.round(desktopZoomFactor.value * 100)}%`)
const canZoomOutDesktop = computed(() => desktopZoomFactor.value > DESKTOP_ZOOM_MIN + 0.001)
const canZoomInDesktop = computed(() => desktopZoomFactor.value < DESKTOP_ZOOM_MAX - 0.001)

function clampDesktopZoom(factor: number) {
  if (!Number.isFinite(factor)) {
    return 1
  }
  return Math.min(DESKTOP_ZOOM_MAX, Math.max(DESKTOP_ZOOM_MIN, +factor.toFixed(2)))
}

function applyDesktopZoom(factor: number) {
  const nextFactor = clampDesktopZoom(factor)
  desktopZoomFactor.value = window.proviewDesktop?.setZoomFactor?.(nextFactor) || nextFactor
  localStorage.setItem(DESKTOP_ZOOM_KEY, String(desktopZoomFactor.value))
}

function zoomOutDesktop() {
  applyDesktopZoom(desktopZoomFactor.value - DESKTOP_ZOOM_STEP)
}

function zoomInDesktop() {
  applyDesktopZoom(desktopZoomFactor.value + DESKTOP_ZOOM_STEP)
}

function resetDesktopZoom() {
  applyDesktopZoom(1)
}

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
  { name: 'resume-optimizer', icon: Sparkles, label: '简历优化', path: '/resume-optimizer', group: '工具箱' },
  { name: 'resume-builder', icon: FilePlus2, label: '简历生成', path: '/resume-builder', group: '工具箱' },
  { name: 'my-resumes', icon: FileUser, label: '我的简历', path: '/my-resumes', group: '工具箱' },
  { name: 'career-planning', icon: Map, label: '职业规划', routeName: 'career-planning-overview', path: '/career-planning/overview', group: '工具箱' },
])

const settingsNavItem = { name: 'runtime-config', icon: Settings, label: '应用设置', path: '/config' }
const interviewFlowItems = computed(() => navItems.value.filter(item => item.group === '面试流程'))
const toolboxItems = computed(() => navItems.value.filter(item => item.group === '工具箱'))

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

const isSettingsRoute = computed(() => route.name === 'runtime-config')
const shouldUseCleanMain = computed(() => !isGuestPage.value)

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

function setThemeMode(mode: 'light' | 'dark', e: MouseEvent) {
  const wantsDark = mode === 'dark'
  if (theme.isDark === wantsDark) return
  theme.toggle(e.currentTarget as HTMLElement)
}

function toggleSidebarTheme(e: MouseEvent) {
  theme.toggle(e.currentTarget as HTMLElement)
}

function goLanding() {
  const currentPageUrl = window.location.href.split('#')[0]
  const landingUrl = new URL('index.html', currentPageUrl)
  window.location.assign(landingUrl.toString())
}

function openSettings() {
  navigateTo(settingsNavItem)
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
      class="app-sidebar z-20 hidden min-h-0 flex-col overflow-visible transition-[width] duration-300 md:flex"
      :class="[isSidebarCollapsed ? 'w-[80px]' : 'w-[280px]', { 'app-sidebar--collapsed': isSidebarCollapsed }]"
    >
      <button
        type="button"
        class="app-sidebar__toggle"
        :title="isSidebarCollapsed ? '展开导航栏' : '折叠导航栏'"
        @click="toggleSidebar"
      >
        <ChevronLeft class="app-sidebar__toggle-icon h-4 w-4" />
      </button>

      <div class="app-sidebar__header flex h-20 shrink-0 items-center" :class="isSidebarCollapsed ? 'px-3' : 'px-6'">
        <div class="flex min-w-0 flex-1 items-center" :class="isSidebarCollapsed ? 'justify-center' : 'gap-3'">
          <div class="app-logo-mark flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl text-white">
            <Bot class="w-5 h-5" />
          </div>
          <span
            v-if="!isSidebarCollapsed"
            class="app-logo-text truncate text-xl font-bold tracking-tight"
          >
            ProView AI
          </span>
        </div>
      </div>

      <div class="app-sidebar__scroll custom-scroll min-h-0 flex-1 overflow-y-auto overscroll-contain">
        <nav class="app-sidebar__nav flex flex-col gap-6 px-5 pb-4 pt-5">
          <section class="flex flex-col gap-1">
            <div v-if="!isSidebarCollapsed" class="app-nav-group-title">面试流程</div>
            <button
              v-for="item in interviewFlowItems" :key="item.name"
              @click="navigateTo(item)"
              class="app-nav-button group flex items-center py-3 text-sm font-medium"
              :class="[
                isSidebarCollapsed ? 'justify-center px-0' : 'gap-3 px-4',
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
              <component :is="item.icon" class="h-[18px] w-[18px] shrink-0 transition-transform group-hover:scale-105" />
              <span v-if="!isSidebarCollapsed" class="truncate">{{ item.label }}</span>
            </button>
          </section>

          <section class="flex flex-col gap-1">
            <div v-if="!isSidebarCollapsed" class="app-nav-group-title">工具箱</div>
            <button
              v-for="item in toolboxItems" :key="item.name"
              @click="navigateTo(item)"
              class="app-nav-button group flex items-center py-3 text-sm font-medium"
              :class="[
                isSidebarCollapsed ? 'justify-center px-0' : 'gap-3 px-4',
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
              <component :is="item.icon" class="h-[18px] w-[18px] shrink-0 transition-transform group-hover:scale-105" />
              <span v-if="!isSidebarCollapsed" class="truncate">{{ item.label }}</span>
            </button>
          </section>

          <section class="flex flex-col gap-1">
            <div v-if="!isSidebarCollapsed" class="app-nav-group-title">系统</div>
            <button
              @click="goLanding"
              class="app-nav-button group flex items-center py-3 text-sm font-medium app-nav-button--idle"
              :class="isSidebarCollapsed ? 'justify-center px-0' : 'gap-3 px-4'"
              :title="isSidebarCollapsed ? '返回介绍页' : undefined"
            >
              <ArrowLeft class="h-[18px] w-[18px] shrink-0 transition-transform group-hover:scale-105" />
              <span v-if="!isSidebarCollapsed" class="truncate">返回介绍页</span>
            </button>
            <button
              @click="openSettings"
              class="app-nav-button group flex items-center py-3 text-sm font-medium"
              :class="[
                isSidebarCollapsed ? 'justify-center px-0' : 'gap-3 px-4',
                isSettingsRoute ? 'app-nav-button--active' : 'app-nav-button--idle'
              ]"
              :title="isSidebarCollapsed ? '应用设置' : undefined"
            >
              <Settings class="h-[18px] w-[18px] shrink-0 transition-transform group-hover:scale-105" />
              <span v-if="!isSidebarCollapsed" class="truncate">应用设置</span>
            </button>
          </section>
        </nav>
      </div>

      <div class="app-sidebar__footer shrink-0" :class="isSidebarCollapsed ? 'px-3 pb-6 pt-4' : 'px-5 pb-6 pt-4'">
        <div v-if="!isSidebarCollapsed" class="app-sidebar-theme">
          <span class="app-sidebar-theme__label">{{ theme.isDark ? '深色' : '浅色' }}</span>
          <div class="app-sidebar-theme__actions">
            <button
              type="button"
              class="app-sidebar-theme__option"
              :class="{ 'app-sidebar-theme__option--active': !theme.isDark }"
              :aria-pressed="!theme.isDark"
              title="切换到浅色主题"
              @click="setThemeMode('light', $event)"
            >
              <Sun class="h-4 w-4" />
            </button>
            <button
              type="button"
              class="app-sidebar-theme__option"
              :class="{ 'app-sidebar-theme__option--active': theme.isDark }"
              :aria-pressed="theme.isDark"
              title="切换到深色主题"
              @click="setThemeMode('dark', $event)"
            >
              <Moon class="h-4 w-4" />
            </button>
          </div>
        </div>
        <div v-if="isDesktop && !isSidebarCollapsed" class="app-sidebar-zoom">
          <span class="app-sidebar-theme__label">界面缩放</span>
          <div class="app-sidebar-zoom__actions">
            <button
              type="button"
              class="app-sidebar-zoom__button"
              :disabled="!canZoomOutDesktop"
              title="缩小界面"
              @click="zoomOutDesktop"
            >
              -
            </button>
            <button
              type="button"
              class="app-sidebar-zoom__value"
              :disabled="desktopZoomFactor === 1"
              title="恢复默认缩放"
              @click="resetDesktopZoom"
            >
              {{ desktopZoomPercent }}
            </button>
            <button
              type="button"
              class="app-sidebar-zoom__button"
              :disabled="!canZoomInDesktop"
              title="放大界面"
              @click="zoomInDesktop"
            >
              +
            </button>
          </div>
        </div>
        <button
          v-if="isSidebarCollapsed"
          type="button"
          class="app-sidebar-theme-collapsed"
          :title="theme.isDark ? '切换到浅色主题' : '切换到深色主题'"
          :aria-pressed="theme.isDark"
          @click="toggleSidebarTheme"
        >
          <Sun v-if="theme.isDark" class="h-5 w-5" />
          <Moon v-else class="h-5 w-5" />
        </button>
        <div v-if="isDesktop && isSidebarCollapsed" class="app-sidebar-zoom-collapsed">
          <button
            type="button"
            class="app-sidebar-zoom__button"
            :disabled="!canZoomOutDesktop"
            title="缩小界面"
            @click="zoomOutDesktop"
          >
            -
          </button>
          <button
            type="button"
            class="app-sidebar-zoom__value app-sidebar-zoom__value--compact"
            :disabled="desktopZoomFactor === 1"
            title="恢复默认缩放"
            @click="resetDesktopZoom"
          >
            {{ Math.round(desktopZoomFactor * 100) }}
          </button>
          <button
            type="button"
            class="app-sidebar-zoom__button"
            :disabled="!canZoomInDesktop"
            title="放大界面"
            @click="zoomInDesktop"
          >
            +
          </button>
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
    <main
      class="app-main custom-scroll relative z-10 min-h-0 flex-1 overflow-y-auto overscroll-contain pb-20 md:pb-0"
      :class="{ 'app-main--clean': shouldUseCleanMain }"
    >
      <BlobBackground v-if="!shouldUseCleanMain" />
      <div class="relative z-10 min-h-full">
        <div v-if="!isGuestPage" class="pointer-events-none absolute right-4 top-4 z-20 flex items-center gap-2 sm:gap-3 md:hidden">
          <button
            type="button"
            class="app-theme-switch pointer-events-auto"
            :class="{ 'app-theme-switch--dark': theme.isDark }"
            :title="theme.isDark ? '切换到浅色模式' : '切换到深色模式'"
            :aria-pressed="theme.isDark"
            @click="handleThemeToggle"
          >
            <span class="app-theme-switch__label hidden sm:inline">{{ theme.isDark ? '深色' : '浅色' }}</span>
            <span class="app-theme-switch__track">
              <Sun class="app-theme-switch__track-icon app-theme-switch__track-icon--sun h-3.5 w-3.5" />
              <Moon class="app-theme-switch__track-icon app-theme-switch__track-icon--moon h-3.5 w-3.5" />
              <span class="app-theme-switch__thumb">
                <Moon v-if="theme.isDark" class="h-3.5 w-3.5" />
                <Sun v-else class="h-3.5 w-3.5" />
              </span>
            </span>
          </button>
          <button
            type="button"
            class="app-top-chip pointer-events-auto inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold md:hidden"
            :class="{ 'app-top-chip--active': isSettingsRoute }"
            @click="openSettings"
          >
            <Settings class="h-4 w-4" />
            <span class="hidden sm:inline">应用设置</span>
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
  --sidebar-bg: var(--ui-sidebar-bg);
  --sidebar-border: var(--ui-sidebar-border);
  --sidebar-text: var(--ui-sidebar-text);
  --sidebar-text-soft: var(--ui-sidebar-text-soft);
  --sidebar-text-muted: var(--ui-sidebar-text-muted);
  --sidebar-hover-bg: var(--ui-sidebar-hover-bg);
  --sidebar-active-bg: var(--ui-sidebar-active-bg);
  --sidebar-indicator: var(--ui-sidebar-indicator);
  --sidebar-logo-bg: var(--ui-sidebar-logo-bg);
  --sidebar-logo-fg: var(--ui-sidebar-logo-fg);
  background: var(--ui-shell-background);
  color: var(--ui-text-primary);
}

.app-sidebar {
  position: relative;
  border-right: 1px solid var(--sidebar-border);
  background: var(--sidebar-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: var(--ui-shadow-md);
}

.app-sidebar::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 22%);
}

.app-sidebar__toggle {
  position: absolute;
  top: 28px;
  right: -12px;
  z-index: 30;
  display: inline-flex;
  height: 24px;
  width: 24px;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--sidebar-border);
  border-radius: 9999px;
  background: var(--ui-surface-raised);
  color: var(--sidebar-text-muted);
  cursor: pointer;
  box-shadow: var(--ui-shadow-sm);
  transition:
    color 180ms ease,
    background-color 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.app-sidebar__toggle:hover {
  color: var(--sidebar-text);
  background: var(--ui-surface-3);
  border-color: var(--ui-border-strong);
  box-shadow: var(--ui-shadow-md);
}

.app-sidebar__toggle-icon {
  transition: transform 220ms ease;
}

.app-sidebar--collapsed .app-sidebar__toggle-icon {
  transform: rotate(180deg);
}

.app-sidebar__header {
  position: relative;
  border-bottom: 1px solid var(--sidebar-border);
}

.app-logo-mark {
  background: var(--sidebar-logo-bg);
  color: var(--sidebar-logo-fg);
  transition: background-color 220ms ease, color 220ms ease;
}

.app-logo-text {
  color: var(--sidebar-text);
  transition: color 220ms ease;
}

.app-top-chip,
.app-theme-switch,
.app-sidebar-theme-collapsed {
  border: 1px solid var(--ui-border-default);
  background: var(--ui-surface-floating);
  color: var(--ui-text-secondary);
  cursor: pointer;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: var(--ui-shadow-sm);
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease,
    color 180ms ease,
    background-color 180ms ease;
}

.app-top-chip,
.app-theme-switch {
  border-radius: 9999px;
}

.app-top-chip:hover,
.app-theme-switch:hover,
.app-sidebar-theme-collapsed:hover {
  transform: translateY(-1px);
  border-color: var(--ui-border-strong);
  background: var(--ui-surface-raised);
  color: var(--ui-text-primary);
  box-shadow: var(--ui-shadow-md);
}

.app-top-chip:hover,
.app-theme-switch:hover {
  border-radius: 9999px;
}

.app-top-chip--active {
  color: var(--ui-text-primary);
  border-color: var(--ui-border-strong);
  background: var(--ui-surface-3);
  box-shadow: var(--ui-shadow-sm);
}

.app-theme-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 118px;
  padding: 0.45rem 0.5rem 0.45rem 0.85rem;
  border-radius: 9999px;
}

.app-theme-switch__label {
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--ui-text-muted);
}

.app-theme-switch__track {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 74px;
  height: 38px;
  padding: 0 0.55rem;
  border-radius: 9999px;
  border: 1px solid var(--ui-border-subtle);
  background: var(--ui-surface-3);
  box-shadow: inset 0 1px 2px rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.app-theme-switch__track-icon {
  position: relative;
  z-index: 1;
  transition: opacity 180ms ease, color 180ms ease;
}

.app-theme-switch__track-icon--sun {
  color: var(--ui-text-muted);
}

.app-theme-switch__track-icon--moon {
  color: var(--ui-accent-strong);
  opacity: 0.5;
}

.app-theme-switch__thumb {
  position: absolute;
  top: 4px;
  left: 4px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 9999px;
  border: 1px solid var(--ui-border-subtle);
  background: var(--ui-surface-raised);
  color: var(--ui-text-secondary);
  box-shadow: var(--ui-shadow-sm);
  transition:
    transform 220ms ease,
    background 220ms ease,
    color 220ms ease,
    border-color 220ms ease,
    box-shadow 220ms ease;
}

.app-theme-switch--dark .app-theme-switch__label {
  color: var(--ui-text-secondary);
}

.app-theme-switch--dark .app-theme-switch__track {
  background: var(--ui-surface-2);
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.18);
}

.app-theme-switch--dark .app-theme-switch__track-icon--sun {
  color: var(--ui-text-muted);
  opacity: 0.38;
}

.app-theme-switch--dark .app-theme-switch__track-icon--moon {
  color: var(--ui-accent-strong);
  opacity: 1;
}

.app-theme-switch--dark .app-theme-switch__thumb {
  transform: translateX(36px);
  border-color: rgba(127, 151, 186, 0.28);
  background: var(--ui-accent-soft);
  color: var(--ui-accent-strong);
  box-shadow: var(--ui-shadow-sm);
}

.app-nav-group-title {
  margin-bottom: 0.75rem;
  padding-left: 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--sidebar-text-muted);
  white-space: nowrap;
  overflow: hidden;
}

.app-nav-button {
  position: relative;
  overflow: hidden;
  width: 100%;
  border: 1px solid transparent;
  border-radius: 0.75rem;
  background: transparent;
  text-align: left;
  white-space: nowrap;
  transition:
    color 220ms ease,
    background-color 220ms ease,
    border-color 220ms ease;
}

.app-nav-button--idle {
  color: var(--sidebar-text-soft);
}

.app-nav-button--idle:hover {
  color: var(--sidebar-text);
  background: var(--sidebar-hover-bg);
}

.app-nav-button--active {
  color: var(--sidebar-text);
  background: var(--sidebar-active-bg);
  border-color: var(--sidebar-border);
  font-weight: 600;
}

.app-nav-button--active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 15%;
  width: 3px;
  height: 70%;
  border-radius: 0 9999px 9999px 0;
  background: var(--sidebar-indicator);
}

.app-nav-button--disabled {
  color: var(--sidebar-text-soft);
  opacity: 0.5;
  cursor: not-allowed;
}

.app-nav-button--disabled:hover {
  color: var(--sidebar-text-soft);
  background: transparent;
}

.app-sidebar__footer {
  position: relative;
  border-top: 1px solid var(--sidebar-border);
}

.app-sidebar-theme {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border: 1px solid var(--sidebar-border);
  border-radius: 9999px;
  background: var(--ui-surface-2);
  padding: 0.5rem;
  box-shadow: var(--ui-shadow-sm);
  transition: background-color 220ms ease, border-color 220ms ease, box-shadow 220ms ease;
}

.app-sidebar-zoom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.75rem;
  border: 1px solid var(--sidebar-border);
  border-radius: 9999px;
  background: var(--ui-surface-2);
  padding: 0.5rem;
  box-shadow: var(--ui-shadow-sm);
}

.app-sidebar-theme__label {
  padding-left: 0.45rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--sidebar-text-soft);
  white-space: nowrap;
}

.app-sidebar-theme__actions,
.app-sidebar-zoom__actions,
.app-sidebar-zoom-collapsed {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  border-radius: 9999px;
  background: var(--ui-surface-3);
  padding: 0.25rem;
}

.app-sidebar-zoom-collapsed {
  margin-top: 0.75rem;
  justify-content: center;
}

.app-sidebar-theme__option {
  display: inline-flex;
  height: 2rem;
  width: 2rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  border: 1px solid transparent;
  color: var(--sidebar-text-muted);
  cursor: pointer;
  transition: background-color 220ms ease, color 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
}

.app-sidebar-zoom__button,
.app-sidebar-zoom__value {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  min-width: 2rem;
  border-radius: 9999px;
  border: 1px solid transparent;
  color: var(--sidebar-text-muted);
  cursor: pointer;
  transition: background-color 220ms ease, color 220ms ease, box-shadow 220ms ease, border-color 220ms ease;
}

.app-sidebar-zoom__value {
  min-width: 3.6rem;
  padding: 0 0.7rem;
  font-size: 0.78rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.app-sidebar-zoom__value--compact {
  min-width: 2.7rem;
  padding: 0 0.45rem;
}

.app-sidebar-theme__option:hover {
  color: var(--sidebar-text);
  background: var(--ui-surface-raised);
  border-color: var(--ui-border-subtle);
}

.app-sidebar-zoom__button:hover,
.app-sidebar-zoom__value:hover {
  color: var(--sidebar-text);
  background: var(--ui-surface-raised);
  border-color: var(--ui-border-subtle);
}

.app-sidebar-theme__option--active {
  background: var(--sidebar-text);
  color: var(--sidebar-bg);
  box-shadow: var(--ui-shadow-sm);
}

.app-sidebar-zoom__button:disabled,
.app-sidebar-zoom__value:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.app-sidebar-theme-collapsed {
  display: flex;
  height: 2.5rem;
  width: 2.5rem;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  margin-inline: auto;
}

.app-sidebar--collapsed .app-sidebar__nav {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.app-sidebar--collapsed .app-nav-button {
  padding-left: 0;
  padding-right: 0;
}

.app-sidebar--collapsed .app-nav-button--active::before {
  left: 0;
}

.app-mobile-nav {
  border-top: 1px solid var(--ui-border-default);
  background: var(--ui-surface-floating);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: var(--ui-shadow-md);
}

.app-mobile-tab {
  position: relative;
  transition: color 180ms ease, transform 180ms ease;
}

.app-mobile-tab--active {
  color: var(--ui-accent-strong);
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
  background: var(--ui-accent);
}

.app-mobile-tab--idle {
  color: var(--ui-text-secondary);
}

.app-mobile-tab--idle:hover {
  color: var(--ui-text-primary);
  transform: translateY(-1px);
}

.app-mobile-tab--disabled {
  color: var(--ui-text-muted);
}

.app-main {
  background: transparent;
  transition: background-color 220ms ease;
}

.app-main--clean {
  background: var(--ui-main-clean-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

@media (max-width: 639px) {
  .app-theme-switch {
    min-width: auto;
    gap: 0;
    padding: 0.35rem;
  }

  .app-theme-switch__track {
    width: 68px;
    height: 36px;
  }

  .app-theme-switch__thumb {
    width: 28px;
    height: 28px;
  }

  .app-theme-switch--dark .app-theme-switch__thumb {
    transform: translateX(32px);
  }
}
</style>
