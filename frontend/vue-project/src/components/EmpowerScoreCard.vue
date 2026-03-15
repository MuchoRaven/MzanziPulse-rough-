<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, required: true },
  tier: { type: String, required: true },
  balance: { type: Number, required: true },
  cashBalance: { type: Number, required: true },
  digitalBalance: { type: Number, required: true }
})

const progressPercentage = computed(() => (props.score / 1000) * 100)

const tierConfig = computed(() => {
  const configs = {
    'DEVELOPING': { emoji: '🌱', color: 'text-neutral-400' },
    'STARTER':    { emoji: '🚀', color: 'text-accent' },
    'BUILDER':    { emoji: '📈', color: 'text-primary' },
    'GOOD':       { emoji: '💪', color: 'text-primary' },
    'EXCELLENT':  { emoji: '🏆', color: 'text-success' },
    'PRIME':      { emoji: '⭐', color: 'text-success' }
  }
  return configs[props.tier] || configs['DEVELOPING']
})
</script>

<template>
  <div class="bg-gradient-to-br from-primary via-primary-light to-accent rounded-2xl shadow-xl overflow-hidden">
    <div class="p-6 lg:p-8">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="flex items-center gap-6">
          <div class="relative w-28 h-28 lg:w-32 lg:h-32 flex-shrink-0">
            <div class="absolute inset-0 rounded-full bg-white/20"></div>
            <div 
              class="absolute inset-0 rounded-full"
              :style="{
                background: `conic-gradient(white ${progressPercentage}%, transparent ${progressPercentage}%)`
              }"
            ></div>
            <div class="absolute inset-2 rounded-full bg-white flex items-center justify-center">
              <div class="text-center">
                <p class="text-3xl lg:text-4xl font-bold text-neutral-900">{{ score }}</p>
                <p class="text-xs text-neutral-500 font-medium">/ 1000</p>
              </div>
            </div>
          </div>

          <div class="text-white">
            <p class="text-sm font-medium opacity-90 mb-1">Your EmpowerScore</p>
            <div class="flex items-center gap-2 mb-2">
              <span class="text-2xl">{{ tierConfig.emoji }}</span>
              <h2 class="text-2xl lg:text-3xl font-bold">{{ tier }} Tier</h2>
            </div>
            <p class="text-sm opacity-80">
              {{
                tier === 'PRIME'      ? 'Excellent credit!' :
                tier === 'EXCELLENT'  ? 'Strong performance!' :
                tier === 'GOOD'       ? 'Good standing' :
                tier === 'BUILDER'    ? 'Growing steadily' :
                tier === 'STARTER'    ? 'Getting started' :
                                        'Building foundation'
              }}
            </p>
          </div>
        </div>

        <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4 lg:p-6 border border-white/20">
          <p class="text-white/80 text-sm font-medium mb-3">💰 Wallet Balance</p>
          
          <div class="space-y-3">
            <div>
              <p class="text-white text-3xl lg:text-4xl font-bold">
                R{{ balance.toLocaleString('en-ZA', { minimumFractionDigits: 2 }) }}
              </p>
              <p class="text-white/70 text-xs mt-1">Total Available</p>
            </div>

            <div class="flex gap-4 pt-3 border-t border-white/20">
              <div class="flex-1">
                <p class="text-white/70 text-xs mb-1">💵 Cash</p>
                <p class="text-white font-semibold">R{{ cashBalance.toLocaleString('en-ZA') }}</p>
              </div>
              <div class="flex-1">
                <p class="text-white/70 text-xs mb-1">💳 Digital</p>
                <p class="text-white font-semibold">R{{ digitalBalance.toLocaleString('en-ZA') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>