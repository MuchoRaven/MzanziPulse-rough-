<script setup>
defineProps({
  grant: { type: Object, required: true }
})
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-neutral-200 p-5 hover:shadow-md hover:border-success/30 transition-all">
    <div class="flex items-start justify-between mb-3">
      <div class="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center text-2xl">
        {{ grant.icon }}
      </div>
      
      <div :class="[
        'px-2 py-1 rounded-full text-xs font-bold',
        grant.match >= 90 ? 'bg-success/20 text-success-dark' : 'bg-primary/20 text-primary-dark'
      ]">
        {{ grant.match }}% Match
      </div>
    </div>

    <h3 class="font-semibold text-neutral-900 mb-1">{{ grant.name }}</h3>
    <p class="text-xs text-neutral-600 mb-3">{{ grant.provider }}</p>

    <div class="flex items-center gap-2 mb-3">
      <span class="text-lg font-bold text-success">{{ grant.amount }}</span>
    </div>

    <div class="flex items-center justify-between pt-3 border-t border-neutral-100">
      <p class="text-xs text-neutral-500">⏰ {{ grant.deadline }}</p>
      <button class="text-xs font-semibold text-primary hover:text-primary-dark">Apply →</button>
    </div>
  </div>
</template>