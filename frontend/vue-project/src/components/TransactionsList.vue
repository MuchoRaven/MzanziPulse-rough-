<template>
  <div class="bg-white rounded-xl shadow-md overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-primary to-primary-dark text-white px-6 py-4 flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold">Recent Transactions</h2>
        <p class="text-sm text-primary-100">Last 30 days</p>
      </div>
      <button
        @click="refreshTransactions"
        class="p-2 hover:bg-white/10 rounded-lg transition-colors"
        title="Refresh"
      >
        <span class="text-xl">🔄</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-8 text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
      <p class="text-neutral-500 mt-4">Loading transactions...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="transactions.length === 0" class="p-8 text-center">
      <span class="text-6xl mb-4 block">📊</span>
      <h3 class="text-lg font-semibold text-neutral-700 mb-2">No Transactions Yet</h3>
      <p class="text-neutral-500 mb-4">Start tracking your business by adding your first transaction</p>
      <button
        @click="$emit('add-transaction')"
        class="px-6 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors"
      >
        Add Transaction
      </button>
    </div>

    <!-- Transactions List -->
    <div v-else class="divide-y divide-neutral-200">
      <div
        v-for="transaction in visibleTransactions"
        :key="transaction.id"
        class="p-4 hover:bg-neutral-50 transition-colors"
      >
        <div class="flex items-start justify-between">
          <!-- Left: Icon + Details -->
          <div class="flex items-start gap-3 flex-1">
            <!-- Icon -->
            <div
              :class="[
                'w-10 h-10 rounded-full flex items-center justify-center text-xl',
                transaction.type === 'CASH_IN' || transaction.type === 'DIGITAL_IN'
                  ? 'bg-success/10 text-success'
                  : 'bg-danger/10 text-danger'
              ]"
            >
              {{ transaction.type === 'CASH_IN' || transaction.type === 'DIGITAL_IN' ? '💰' : '💸' }}
            </div>

            <!-- Details -->
            <div class="flex-1">
              <p class="font-medium text-neutral-900">{{ transaction.description }}</p>
              <div class="flex items-center gap-3 mt-1 text-sm text-neutral-500">
                <span>{{ formatDate(transaction.date) }}</span>
                <span>•</span>
                <span class="capitalize">{{ formatPaymentMethod(transaction.paymentMethod) }}</span>
                <span v-if="transaction.category" class="px-2 py-0.5 bg-neutral-100 rounded text-xs">
                  {{ formatCategory(transaction.category) }}
                </span>
              </div>
              
              <!-- Entry Method Badge -->
              <div v-if="transaction.entryMethod === 'OCR'" class="mt-1">
                <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                  📷 Scanned
                </span>
              </div>
            </div>
          </div>

          <!-- Right: Amount -->
          <div class="text-right ml-4">
            <p
              :class="[
                'text-lg font-bold',
                transaction.type === 'CASH_IN' || transaction.type === 'DIGITAL_IN'
                  ? 'text-success'
                  : 'text-danger'
              ]"
            >
              {{ transaction.type === 'CASH_IN' || transaction.type === 'DIGITAL_IN' ? '+' : '-' }}R{{ transaction.amount.toFixed(2) }}
            </p>
            <p class="text-xs text-neutral-500 mt-1">
              {{ formatTransactionType(transaction.type) }}
            </p>
          </div>
        </div>

        <!-- Receipt Image Preview (if exists) -->
        <div v-if="transaction.receiptImage" class="mt-3 pl-13">
          <img
            :src="`/uploads/receipts/${transaction.receiptImage}`"
            alt="Receipt"
            class="h-20 w-auto rounded border border-neutral-200 cursor-pointer hover:opacity-80 transition-opacity"
            @click="viewReceipt(transaction.receiptImage)"
          />
        </div>
      </div>
    </div>

    <!-- Expand / Collapse -->
    <div v-if="transactions.length > 0 && hasMore" class="p-4 border-t border-neutral-200">
      <button
        @click="expanded = !expanded"
        class="w-full py-2 text-primary hover:text-primary-dark font-medium transition-colors flex items-center justify-center gap-1"
      >
        <span v-if="!expanded">Show {{ transactions.length - COLLAPSED_LIMIT }} more ▾</span>
        <span v-else>Show less ▴</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['add-transaction'])

const authStore = useAuthStore()
const transactions = ref([])
const loading = ref(false)
const expanded = ref(false)
const COLLAPSED_LIMIT = 10

const visibleTransactions = computed(() =>
  expanded.value ? transactions.value : transactions.value.slice(0, COLLAPSED_LIMIT)
)

const hasMore = computed(() => transactions.value.length > COLLAPSED_LIMIT)

const fetchTransactions = async () => {
  loading.value = true
  try {
    const response = await fetch(
      `http://localhost:5000/api/transactions?userId=${authStore.user.id}&limit=50`
    )
    const data = await response.json()
    if (data.success) {
      transactions.value = data.transactions
    } else {
      console.error('Failed to fetch transactions:', data.error)
    }
  } catch (error) {
    console.error('Fetch transactions error:', error)
  } finally {
    loading.value = false
  }
}

const refreshTransactions = () => {
  fetchTransactions()
}

const viewReceipt = (imagePath) => {
  // TODO: Open receipt in modal/lightbox
  window.open(`/uploads/receipts/${imagePath}`, '_blank')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  
  return date.toLocaleDateString('en-ZA', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const formatPaymentMethod = (method) => {
  const methods = {
    'CASH': 'Cash',
    'DIGITAL': 'Digital',
    'CREDIT': 'Credit (Book)'
  }
  return methods[method] || method
}

const formatCategory = (category) => {
  return category.replace(/_/g, ' ').toLowerCase()
}

const formatTransactionType = (type) => {
  const types = {
    'CASH_IN': 'Cash In',
    'DIGITAL_IN': 'Digital In',
    'CASH_OUT': 'Expense',
    'CREDIT_GIVEN': 'Credit Given',
    'CREDIT_COLLECTED': 'Credit Collected'
  }
  return types[type] || type
}

onMounted(() => {
  fetchTransactions()
})

defineExpose({
  refreshTransactions
})
</script>