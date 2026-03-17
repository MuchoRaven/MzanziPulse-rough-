<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-2xl w-full max-w-md shadow-2xl">
      <!-- Header -->
      <div class="bg-primary text-white px-6 py-4 rounded-t-2xl flex items-center justify-between">
        <h2 class="text-xl font-bold">Add Transaction</h2>
        <button @click="close" class="text-white hover:text-neutral-200">
          <span class="text-2xl">×</span>
        </button>
      </div>

      <!-- Form -->
      <div class="p-6 space-y-4">
        <!-- Transaction Type -->
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-2">Transaction Type</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              @click="form.type = 'CASH_IN'"
              :class="[
                'py-3 px-4 rounded-lg font-medium transition-all',
                form.type === 'CASH_IN'
                  ? 'bg-success text-white'
                  : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
              ]"
            >
              💰 Income
            </button>
            <button
              @click="form.type = 'CASH_OUT'"
              :class="[
                'py-3 px-4 rounded-lg font-medium transition-all',
                form.type === 'CASH_OUT'
                  ? 'bg-danger text-white'
                  : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
              ]"
            >
              💸 Expense
            </button>
          </div>
        </div>

        <!-- Amount -->
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-2">Amount (R)</label>
          <input
            v-model="form.amount"
            type="number"
            step="0.01"
            placeholder="0.00"
            class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-2">Description</label>
          <input
            v-model="form.description"
            type="text"
            placeholder="e.g., Sold bread, Bought flour"
            class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          />
        </div>

        <!-- Payment Method -->
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-2">Payment Method</label>
          <select
            v-model="form.paymentMethod"
            class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="CASH">Cash</option>
            <option value="DIGITAL">Digital (Card/EFT)</option>
            <option value="CREDIT">Credit (Book)</option>
          </select>
        </div>

        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-neutral-700 mb-2">Category</label>
          <select
            v-model="form.category"
            class="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          >
            <option value="GROCERIES">Groceries</option>
            <option value="AIRTIME">Airtime</option>
            <option value="BEVERAGES">Beverages</option>
            <option value="TOILETRIES">Toiletries</option>
            <option value="STOCK_PURCHASE">Stock Purchase</option>
            <option value="UTILITIES">Utilities</option>
            <option value="OTHER">Other</option>
          </select>
        </div>

        <!-- Camera/OCR Button -->
        <div class="border-2 border-dashed rounded-lg p-4 transition-colors"
             :class="ocrState === 'success' ? 'border-success/40 bg-success/5'
                   : ocrState === 'error'   ? 'border-danger/40 bg-danger/5'
                   : 'border-neutral-300'">
          <button
            @click="handleCameraClick"
            type="button"
            :disabled="loading"
            class="w-full flex items-center justify-center gap-2 py-3 px-4 bg-neutral-100 hover:bg-neutral-200 rounded-lg transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <span class="text-2xl">{{ loading ? '⏳' : '📷' }}</span>
            <span class="font-medium">{{ loading ? 'Scanning...' : 'Scan Receipt / Logbook' }}</span>
          </button>

          <!-- OCR status line -->
          <p v-if="ocrStatus" class="text-xs text-center mt-2 font-medium"
             :class="ocrState === 'success' ? 'text-success'
                   : ocrState === 'error'   ? 'text-danger'
                   : 'text-neutral-500'">
            {{ ocrStatus }}
          </p>
          <p v-else class="text-xs text-neutral-500 text-center mt-2">
            Auto-fill amount &amp; description from photo
          </p>

          <!-- Merchant pill (shown after successful scan) -->
          <div v-if="ocrMerchant" class="mt-2 flex justify-center">
            <span class="text-xs px-3 py-1 bg-success/10 text-success rounded-full font-medium">
              🏪 {{ ocrMerchant }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3 pt-4">
          <button
            @click="close"
            class="flex-1 py-3 px-4 bg-neutral-200 hover:bg-neutral-300 text-neutral-700 font-medium rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            @click="submitTransaction"
            :disabled="!isValid || loading"
            :class="[
              'flex-1 py-3 px-4 font-medium rounded-lg transition-colors',
              isValid && !loading
                ? 'bg-primary hover:bg-primary-dark text-white'
                : 'bg-neutral-300 text-neutral-500 cursor-not-allowed'
            ]"
          >
            {{ loading ? 'Adding...' : 'Add Transaction' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import API_BASE from '@/config/api'
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'success'])

const authStore = useAuthStore()
const loading    = ref(false)
const ocrStatus  = ref('')
const ocrState   = ref('')   // '' | 'success' | 'error'
const ocrMerchant = ref('')

const form = ref({
  type: 'CASH_IN',
  amount: '',
  description: '',
  paymentMethod: 'CASH',
  category: 'OTHER'
})

const isValid = computed(() => {
  return form.value.amount > 0 && form.value.description.trim().length > 0
})

const close = () => {
  emit('close')
}

const handleCameraClick = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.capture = 'environment'

  input.onchange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    loading.value   = true
    ocrStatus.value = 'Scanning receipt...'
    ocrState.value  = ''
    ocrMerchant.value = ''

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('userId', authStore.user.id)

      const response = await fetch(`${API_BASE}/api/transactions/ocr`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()
      const ext  = data.extractedData || {}
      const conf = data.confidence ?? 0
      const pct  = (conf * 100).toFixed(0)
      const THRESHOLD = 0.7

      if (data.success && ext.amount) {
        // Auto-fill amount
        form.value.amount = ext.amount.toFixed(2)

        // Auto-fill description from first item or merchant
        if (ext.items && ext.items.length > 0) {
          form.value.description = ext.items[0]
        } else if (ext.merchantName) {
          form.value.description = `Purchase at ${ext.merchantName}`
        }

        // Show merchant pill
        if (ext.merchantName) {
          ocrMerchant.value = ext.merchantName
        }

        if (conf < THRESHOLD) {
          ocrState.value  = 'error'
          ocrStatus.value = `⚠️ Low confidence (${pct}%) — please verify`
        } else {
          ocrState.value  = 'success'
          ocrStatus.value = `✅ Scanned! Confidence: ${pct}%`
        }
      } else {
        ocrState.value  = 'error'
        ocrStatus.value = data.warning
          ? `⚠️ ${data.warning} — enter manually`
          : '❌ Could not read receipt — enter manually'
      }
    } catch (error) {
      console.error('OCR error:', error)
      ocrState.value  = 'error'
      ocrStatus.value = '❌ Scan failed — check connection'
    } finally {
      loading.value = false
    }
  }

  input.click()
}

const submitTransaction = async () => {
  if (!isValid.value) return

  loading.value = true

  try {
    const response = await fetch(`${API_BASE}/api/transactions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        userId: authStore.user.id,
        type: form.value.type,
        amount: parseFloat(form.value.amount),
        description: form.value.description,
        paymentMethod: form.value.paymentMethod,
        category: form.value.category,
        entryMethod: 'MANUAL'
      })
    })

    const data = await response.json()

    if (data.success) {
      emit('success')
      close()
      
      // Reset form
      form.value = {
        type: 'CASH_IN',
        amount: '',
        description: '',
        paymentMethod: 'CASH',
        category: 'OTHER'
      }
    } else {
      alert('Error: ' + data.error)
    }
  } catch (error) {
    console.error('Add transaction error:', error)
    alert('Failed to add transaction')
  } finally {
    loading.value = false
  }
}
</script>