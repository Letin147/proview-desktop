<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  score: number
  compact?: boolean
}>(), {
  compact: false,
})

const MAX_SCORE = 10
const dashArray = ref('0, 100')

const normalizedScore = computed(() => {
  const value = Number(props.score)
  if (!Number.isFinite(value)) return 0
  return Math.min(Math.max(value, 0), MAX_SCORE)
})

const progressPercent = computed(() => normalizedScore.value * 10)

const displayScore = computed(() => (
  Number.isInteger(normalizedScore.value)
    ? String(normalizedScore.value)
    : normalizedScore.value.toFixed(1)
))

const scoreTone = computed(() => {
  if (normalizedScore.value >= 8) return 'strong'
  if (normalizedScore.value >= 6) return 'accent'
  if (normalizedScore.value >= 4) return 'warning'
  return 'danger'
})

const scoreLabel = computed(() => {
  if (normalizedScore.value >= 8) return '表现稳定'
  if (normalizedScore.value >= 6) return '继续加强'
  if (normalizedScore.value >= 4) return '存在短板'
  return '需要补强'
})

function syncDashArray() {
  dashArray.value = `${progressPercent.value}, 100`
}

onMounted(() => {
  requestAnimationFrame(syncDashArray)
})

watch(progressPercent, syncDashArray)
</script>

<template>
  <div class="score-circle" :class="[`score-circle--${scoreTone}`, { 'score-circle--compact': compact }]">
    <div class="score-circle__halo" aria-hidden="true"></div>
    <svg class="score-circle__svg" viewBox="0 0 36 36" aria-hidden="true">
      <path
        class="score-circle__track"
        stroke-width="3"
        stroke="currentColor"
        fill="none"
        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
      />
      <path
        class="score-circle__progress"
        :stroke-dasharray="dashArray"
        stroke-width="3"
        stroke-linecap="round"
        stroke="currentColor"
        fill="none"
        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
      />
    </svg>
    <div class="score-circle__center">
      <span class="score-circle__value">{{ displayScore }}</span>
      <span v-if="!compact" class="score-circle__label">{{ scoreLabel }}</span>
    </div>
  </div>
</template>

<style scoped>
.score-circle {
  --score-accent: var(--ui-accent);
  --score-accent-soft: var(--ui-accent-soft);
  --score-track: var(--ui-border-subtle);
  --score-text: var(--ui-text-primary);
  position: relative;
  display: grid;
  height: 10.5rem;
  width: 10.5rem;
  margin-bottom: 0.5rem;
  place-items: center;
  border: 1px solid var(--ui-border-subtle);
  border-radius: 9999px;
  background: linear-gradient(180deg, var(--ui-surface-raised) 0%, var(--ui-surface-1) 100%);
  box-shadow: var(--ui-shadow-sm);
  overflow: hidden;
}

.score-circle__halo {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(circle at center, var(--score-accent-soft) 0%, transparent 66%);
  opacity: 0.95;
}

.score-circle__svg {
  position: relative;
  z-index: 1;
  height: 100%;
  width: 100%;
  transform: rotate(-90deg);
}

.score-circle__track {
  color: var(--score-track);
}

.score-circle__progress {
  color: var(--score-accent);
  transition: stroke-dasharray 1000ms ease-out, color 220ms ease;
  filter: drop-shadow(0 0 8px var(--score-accent-soft));
}

.score-circle__center {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-circle__value {
  font-size: 2.75rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -0.06em;
  color: var(--score-text);
}

.score-circle__label {
  margin-top: 0.45rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--ui-text-muted);
}

.score-circle--strong {
  --score-accent: #2563eb;
  --score-accent-soft: rgba(37, 99, 235, 0.22);
  --score-track: rgba(37, 99, 235, 0.14);
}

.score-circle--accent {
  --score-accent: #4f46e5;
  --score-accent-soft: rgba(79, 70, 229, 0.2);
  --score-track: rgba(79, 70, 229, 0.14);
}

.score-circle--warning {
  --score-accent: #d97706;
  --score-accent-soft: rgba(245, 158, 11, 0.2);
  --score-track: rgba(245, 158, 11, 0.14);
}

.score-circle--danger {
  --score-accent: #e11d48;
  --score-accent-soft: rgba(244, 63, 94, 0.18);
  --score-track: rgba(244, 63, 94, 0.14);
}

.score-circle--compact {
  height: 7rem;
  width: 7rem;
  margin-bottom: 0;
}

.score-circle--compact .score-circle__value {
  font-size: 2.1rem;
}

:global(html.dark) .score-circle {
  box-shadow: var(--ui-shadow-md);
}

:global(html.dark) .score-circle--strong {
  --score-accent: #60a5fa;
  --score-accent-soft: rgba(96, 165, 250, 0.24);
  --score-track: rgba(96, 165, 250, 0.16);
}

:global(html.dark) .score-circle--accent {
  --score-accent: #818cf8;
  --score-accent-soft: rgba(129, 140, 248, 0.26);
  --score-track: rgba(129, 140, 248, 0.16);
}

:global(html.dark) .score-circle--warning {
  --score-accent: #fbbf24;
  --score-accent-soft: rgba(251, 191, 36, 0.22);
  --score-track: rgba(251, 191, 36, 0.14);
}

:global(html.dark) .score-circle--danger {
  --score-accent: #fb7185;
  --score-accent-soft: rgba(251, 113, 133, 0.22);
  --score-track: rgba(251, 113, 133, 0.14);
}
</style>
