<script setup>
defineProps({
  transaction: { type: Object, required: true }
})
</script>

<template>
  <div class="flex items-center gap-3 p-4 hover:bg-neutral-50 transition-colors">
    <div :class="[
      'w-10 h-10 rounded-lg flex items-center justify-center text-xl flex-shrink-0',
      transaction.type === 'income' ? 'bg-success/10' : 'bg-neutral-100'
    ]">
      {{ transaction.icon }}
    </div>

    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-neutral-900 truncate">{{ transaction.description }}</p>
      <p class="text-xs text-neutral-500 mt-0.5">{{ transaction.date }} • {{ transaction.category }}</p>
    </div>

    <div class="text-right">
      <p :class="[
        'text-sm font-bold',
        transaction.type === 'income' ? 'text-success' : 'text-neutral-600'
      ]">
        {{ transaction.type === 'income' ? '+' : '-' }}R{{ Math.abs(transaction.amount).toFixed(2) }}
      </p>
    </div>
  </div>
</template>