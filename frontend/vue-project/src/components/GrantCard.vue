<script setup>
const props = defineProps({
  grant: { type: Object, required: true }
})

const typeIcon = (type) => {
  if (type === 'GRANT') return '🌱'
  if (type === 'REVENUE_ADVANCE') return '💳'
  return '💼'
}

const typeBadge = (type) => {
  if (type === 'GRANT') return { label: 'Grant', cls: 'bg-success/20 text-success' }
  if (type === 'REVENUE_ADVANCE') return { label: 'Revenue Advance', cls: 'bg-purple-100 text-purple-700' }
  return { label: 'Loan', cls: 'bg-primary/20 text-primary' }
}

const formatAmount = (amount) => {
  if (!amount) return ''
  const fmt = (n) => n >= 1000000 ? `R${(n/1000000).toFixed(1)}M` : n >= 1000 ? `R${(n/1000).toFixed(0)}K` : `R${n}`
  if (amount.min === amount.max) return fmt(amount.max)
  return `${fmt(amount.min)} – ${fmt(amount.max)}`
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm border border-neutral-200 p-5 hover:shadow-md hover:border-success/30 transition-all flex flex-col">
    <div class="flex items-start justify-between mb-3">
      <div class="w-12 h-12 bg-success/10 rounded-lg flex items-center justify-center text-2xl">
        {{ typeIcon(grant.fundingType) }}
      </div>
      <div class="flex flex-col items-end gap-1">
        <span
          class="px-2 py-0.5 rounded-full text-xs font-bold"
          :class="grant.match >= 90 ? 'bg-success/20 text-success' : 'bg-primary/20 text-primary'"
        >{{ grant.match }}% Match</span>
        <span
          class="px-2 py-0.5 rounded-full text-xs font-semibold"
          :class="typeBadge(grant.fundingType).cls"
        >{{ typeBadge(grant.fundingType).label }}</span>
      </div>
    </div>

    <h3 class="font-semibold text-neutral-900 mb-1">{{ grant.name }}</h3>
    <p class="text-xs text-neutral-500 mb-2">{{ grant.provider }}</p>

    <p class="text-sm font-bold text-success mb-3">{{ formatAmount(grant.amount) }}</p>

    <div class="flex items-center justify-between pt-3 border-t border-neutral-100 mt-auto">
      <p class="text-xs text-neutral-500">⏰ {{ grant.deadlineLabel }}</p>
      <a
        :href="grant.applicationUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="text-xs font-semibold text-primary hover:text-primary-dark transition-colors"
      >Apply →</a>
    </div>
  </div>
</template>