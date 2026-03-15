<template>
  <div class="min-h-screen bg-neutral-50">
    <!-- Header -->
    <div class="bg-white border-b border-neutral-200 px-4 py-4 lg:px-6">
      <div class="flex items-center gap-3">
        <span class="text-2xl">💰</span>
        <div>
          <h1 class="text-xl font-bold text-neutral-900">Cash Wallet</h1>
          <p class="text-neutral-500 text-sm">{{ userData.businessName }}</p>
        </div>
      </div>
    </div>

    <div class="p-4 lg:p-6 max-w-3xl mx-auto">
      <CashWallet />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import CashWallet from '../components/CashWallet.vue'

const authStore = useAuthStore()

const userData = computed(() => ({
  businessName: authStore.user?.businessName || 'Your Business',
}))
</script>
