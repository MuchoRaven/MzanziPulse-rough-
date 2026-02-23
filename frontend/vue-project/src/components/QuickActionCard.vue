<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, required: true },
  icon: { type: String, required: true },
  color: { type: String, default: 'primary' }
})

const emit = defineEmits(['click'])
</script>

<template>
  <button
    @click="emit('click')"
    :class="[
      'bg-white rounded-xl shadow-sm border border-neutral-200',
      'p-4 lg:p-5 flex flex-col items-start gap-2',
      'hover:shadow-md hover:border-primary/30 transition-all active:scale-95 min-h-touch'
    ]"
  >
    <div :class="[
      'w-12 h-12 rounded-lg flex items-center justify-center text-2xl',
      color === 'primary' && 'bg-primary/10',
      color === 'success' && 'bg-success/10',
      color === 'accent' && 'bg-accent/10',
      color === 'neutral' && 'bg-neutral-100'
    ]">
      {{ icon }}
    </div>

    <div class="text-left">
      <h3 class="font-semibold text-neutral-900 text-sm lg:text-base mb-0.5">{{ title }}</h3>
      <p class="text-xs text-neutral-500">{{ description }}</p>
    </div>
  </button>
</template>