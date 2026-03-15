<template>
  <div class="relative" ref="container">
    <!-- Trigger button -->
    <button
      @click="open = !open"
      class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
      :class="variant === 'dark'
        ? 'text-neutral-300 hover:text-white hover:bg-white/10'
        : 'text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100'"
    >
      <span class="text-base leading-none">{{ current.flag }}</span>
      <span class="hidden sm:inline">{{ current.label }}</span>
      <span class="text-xs opacity-60">{{ open ? '▴' : '▾' }}</span>
    </button>

    <!-- Dropdown -->
    <div
      v-if="open"
      class="absolute right-0 bottom-full mb-1 w-44 bg-white rounded-xl shadow-lg border border-neutral-200 py-1 z-50"
    >
      <button
        v-for="lang in languages"
        :key="lang.code"
        @click="select(lang.code)"
        class="w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors hover:bg-neutral-50"
        :class="locale === lang.code ? 'text-primary font-semibold' : 'text-neutral-700'"
      >
        <span class="text-lg leading-none">{{ lang.flag }}</span>
        <span>{{ lang.label }}</span>
        <span v-if="locale === lang.code" class="ml-auto text-primary text-xs">✓</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  // 'light' (default) for white backgrounds, 'dark' for colored headers
  variant: { type: String, default: 'light' }
})

const { locale } = useI18n()
const open = ref(false)
const container = ref(null)

const languages = [
  { code: 'en', label: 'English',  flag: '🇬🇧' },
  { code: 'zu', label: 'isiZulu',  flag: '🇿🇦' },
  { code: 'st', label: 'Sesotho',  flag: '🇿🇦' },
  { code: 'xh', label: 'isiXhosa', flag: '🇿🇦' }
]

const current = computed(() =>
  languages.find(l => l.code === locale.value) ?? languages[0]
)

function select(code) {
  locale.value = code
  localStorage.setItem('mp_locale', code)
  open.value = false
}

// Close on outside click
function handleClickOutside(e) {
  if (container.value && !container.value.contains(e.target)) {
    open.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside))
</script>
