<script setup lang="ts">
import { computed, defineAsyncComponent } from 'vue'
import { useResumeBuilderStore } from '../../stores/resumeBuilder'
import type { TemplateId, ResumeDocument } from '../../types/resume-builder'
import { renderContent } from '../../utils/renderContent'

const props = defineProps<{
  document?: ResumeDocument
}>()

const store = useResumeBuilderStore()

const sourceDoc = computed(() => props.document ?? store.document)

const doc = computed<ResumeDocument>(() => ({
  ...sourceDoc.value,
  settings: { ...sourceDoc.value.settings },
  basicInfo: { ...sourceDoc.value.basicInfo },
  polishSuggestions: sourceDoc.value.polishSuggestions.map(suggestion => ({ ...suggestion })),
  modules: sourceDoc.value.modules.map(module => ({
    ...module,
    intention: module.intention ? { ...module.intention } : undefined,
    skillBars: module.skillBars?.map(skill => ({ ...skill })),
    tags: module.tags ? [...module.tags] : undefined,
    content: module.content !== undefined ? renderContent(module.content) : module.content,
    entries: module.entries?.map(entry => ({
      ...entry,
      detail: entry.detail ? renderContent(entry.detail) : entry.detail,
    })),
  })),
}))

const templateComponents: Record<TemplateId, ReturnType<typeof defineAsyncComponent>> = {
  classic: defineAsyncComponent(() => import('./TemplateClassic.vue')),
  modern: defineAsyncComponent(() => import('./TemplateModern.vue')),
  minimal: defineAsyncComponent(() => import('./TemplateMinimal.vue')),
  fresh: defineAsyncComponent(() => import('./TemplateFresh.vue')),
  tech: defineAsyncComponent(() => import('./TemplateTech.vue')),
  creative: defineAsyncComponent(() => import('./TemplateCreative.vue')),
  executive: defineAsyncComponent(() => import('./TemplateExecutive.vue')),
  compact: defineAsyncComponent(() => import('./TemplateCompact.vue')),
  elegant: defineAsyncComponent(() => import('./TemplateElegant.vue')),
}

const currentTemplate = computed(() =>
  templateComponents[doc.value.settings.templateId] || templateComponents.classic
)
</script>

<template>
  <div class="resume-renderer">
    <component :is="currentTemplate" :document="doc" />
  </div>
</template>
