<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Check } from 'lucide-vue-next'

interface Option {
  value: number | string
  label: string
}

interface Props {
  modelValue: number | string
  options: Option[]
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择'
})

const emit = defineEmits<{
  'update:modelValue': [value: number | string]
}>()

const isOpen = ref(false)
const selectRef = ref<HTMLDivElement | null>(null)

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

function selectOption(value: number | string) {
  emit('update:modelValue', value)
  isOpen.value = false
}

function closeDropdown() {
  isOpen.value = false
}

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

// 点击外部关闭下拉菜单
function handleClickOutside(event: MouseEvent) {
  if (selectRef.value && !selectRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div
    ref="selectRef"
    class="custom-select-wrapper"
    :class="{ 'custom-select-wrapper--open': isOpen }"
    @keydown.esc.stop="closeDropdown"
  >
    <button
      type="button"
      @click="toggleDropdown"
      class="custom-select-trigger"
      :class="{ 'custom-select-open': isOpen }"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
    >
      <span class="custom-select-value" :class="{ 'custom-select-value--placeholder': !selectedOption }">
        {{ selectedOption?.label || placeholder }}
      </span>
      <ChevronDown class="custom-select-icon" :class="{ 'rotate-180': isOpen }" />
    </button>

    <Transition name="dropdown">
      <div v-if="isOpen" class="custom-select-dropdown custom-scroll" role="listbox">
        <button
          v-for="option in options"
          :key="option.value"
          type="button"
          @click="selectOption(option.value)"
          class="custom-select-option"
          :class="{ 'custom-select-option-selected': option.value === modelValue }"
        >
          <span>{{ option.label }}</span>
          <Check v-if="option.value === modelValue" class="w-4 h-4" />
        </button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.custom-select-wrapper {
  @apply relative;
  z-index: 1;
}

.custom-select-wrapper--open {
  z-index: 40;
}

.custom-select-trigger {
  @apply flex w-full items-center justify-between gap-3 px-4 py-3 text-left outline-none transition-all;
  border-radius: var(--ui-radius-sm);
  border: 1px solid var(--ui-border-default);
  background: var(--ui-surface-raised);
  color: var(--ui-text-primary);
  box-shadow: var(--ui-shadow-sm);
}

.custom-select-trigger:hover {
  border-color: var(--ui-border-strong);
  background: var(--ui-surface-1);
}

.custom-select-open {
  border-color: var(--ui-accent) !important;
  box-shadow:
    var(--ui-shadow-sm),
    0 0 0 4px var(--ui-focus-ring);
}

.custom-select-value {
  @apply flex-1 text-left text-sm font-medium;
  color: var(--ui-text-primary);
}

.custom-select-value--placeholder {
  color: var(--ui-text-muted);
}

.custom-select-icon {
  @apply h-4 w-4 shrink-0 transition-transform;
  color: var(--ui-text-muted);
}

.custom-select-dropdown {
  @apply absolute left-0 right-0 z-50 mt-2 overflow-hidden;
  max-height: 240px;
  overflow-y: auto;
  padding: 0.4rem;
  border-radius: calc(var(--ui-radius-sm) + 0.125rem);
  border: 1px solid var(--ui-border-default);
  background: var(--ui-surface-raised);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: var(--ui-shadow-lg);
}

.custom-select-option {
  @apply flex w-full items-center justify-between gap-3 px-3 py-2.5 text-left text-sm transition-colors;
  border-radius: calc(var(--ui-radius-sm) - 0.1rem);
  color: var(--ui-text-primary);
}

.custom-select-option:hover {
  background: var(--ui-surface-3);
}

.custom-select-option-selected {
  background: var(--ui-accent-soft);
  color: var(--ui-accent-strong);
  font-weight: 600;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
