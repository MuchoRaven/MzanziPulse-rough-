<template>
  <div class="space-y-4">
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-accent mx-auto"></div>
      <p class="text-neutral-500 mt-4">Loading investor documents...</p>
    </div>

    <div v-else class="space-y-6">
      <!-- Key Metrics -->
      <div class="bg-gradient-to-br from-accent/5 to-primary/5 rounded-lg p-4 border border-accent/20">
        <h4 class="font-bold text-neutral-900 mb-3">📊 Your Business Metrics</h4>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <p class="text-xs text-neutral-600">Monthly Revenue</p>
            <p class="text-xl font-bold text-success">R{{ vault.keyMetrics.monthlyRevenue.toFixed(0) }}</p>
          </div>
          <div>
            <p class="text-xs text-neutral-600">Monthly Expenses</p>
            <p class="text-xl font-bold text-danger">R{{ vault.keyMetrics.monthlyExpenses.toFixed(0) }}</p>
          </div>
          <div>
            <p class="text-xs text-neutral-600">Monthly Profit</p>
            <p class="text-xl font-bold text-primary">R{{ vault.keyMetrics.monthlyProfit.toFixed(0) }}</p>
          </div>
          <div>
            <p class="text-xs text-neutral-600">Profit Margin</p>
            <p class="text-xl font-bold text-accent">{{ vault.keyMetrics.profitMargin.toFixed(1) }}%</p>
          </div>
        </div>
      </div>

      
      <!-- Available Documents -->
      <div>
        <h4 class="font-bold text-neutral-900 mb-3">📁 Available Documents</h4>
        <div class="space-y-3">
          
          <!-- Pitch Deck -->
          <div class="border border-neutral-200 rounded-lg p-4 hover:border-accent transition-colors">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-2xl">📊</span>
                  <h5 class="font-bold text-neutral-900">{{ vault.documents.pitchDeck.name }}</h5>
                  <span class="px-2 py-0.5 bg-success/10 text-success text-xs rounded font-medium">
                    {{ vault.documents.pitchDeck.status }}
                  </span>
                </div>
                <p class="text-sm text-neutral-600 mb-2">{{ vault.documents.pitchDeck.description }}</p>
                <p class="text-xs text-neutral-500">Format: {{ vault.documents.pitchDeck.format }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="generatePitchDeck"
                  :disabled="generatingPitchDeck"
                  class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ generatingPitchDeck ? 'Generating...' : 'Generate' }}
                </button>
                <button
                  v-if="vault.documents.pitchDeck.lastUpdated"
                  @click="downloadDocument('pitchDeck')"
                  class="px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-sm font-medium transition-colors"
                >
                  Download
                </button>
              </div>
            </div>
          </div>

          <!-- Financial Statements -->
          <div class="border border-neutral-200 rounded-lg p-4 hover:border-accent transition-colors">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-2xl">📈</span>
                  <h5 class="font-bold text-neutral-900">{{ vault.documents.financialStatements.name }}</h5>
                  <span class="px-2 py-0.5 bg-success/10 text-success text-xs rounded font-medium">
                    {{ vault.documents.financialStatements.status }}
                  </span>
                </div>
                <p class="text-sm text-neutral-600 mb-2">
                  Includes: {{ vault.documents.financialStatements.includes?.join(', ') }}
                </p>
                <p class="text-xs text-neutral-500">Format: {{ vault.documents.financialStatements.format }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="generateFinancials"
                  :disabled="generatingFinancials"
                  class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ generatingFinancials ? 'Generating...' : 'Generate' }}
                </button>
                <button
                  v-if="vault.documents.financialStatements.lastUpdated"
                  @click="downloadDocument('financials')"
                  class="px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-sm font-medium transition-colors"
                >
                  Download
                </button>
              </div>
            </div>
          </div>

          <!-- Business Plan -->
          <div class="border border-neutral-200 rounded-lg p-4 hover:border-accent transition-colors">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-2xl">📄</span>
                  <h5 class="font-bold text-neutral-900">{{ vault.documents.businessPlan.name }}</h5>
                  <span class="px-2 py-0.5 bg-warning/10 text-warning text-xs rounded font-medium">
                    {{ vault.documents.businessPlan.status }}
                  </span>
                </div>
                <p class="text-sm text-neutral-600 mb-2">{{ vault.documents.businessPlan.description }}</p>
                <p class="text-xs text-neutral-500">Format: {{ vault.documents.businessPlan.format }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="generateBusinessPlan"
                  :disabled="generatingBusinessPlan"
                  class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ generatingBusinessPlan ? 'Generating...' : 'Generate' }}
                </button>
                <button
                  v-if="vault.documents.businessPlan.lastUpdated"
                  @click="downloadDocument('businessPlan')"
                  class="px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-sm font-medium transition-colors"
                >
                  Download
                </button>
              </div>
            </div>
          </div>

          <!-- Growth Forecast -->
          <div class="border border-neutral-200 rounded-lg p-4 hover:border-accent transition-colors">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-2xl">📊</span>
                  <h5 class="font-bold text-neutral-900">{{ vault.documents.growthForecast.name }}</h5>
                  <span class="px-2 py-0.5 bg-success/10 text-success text-xs rounded font-medium">
                    {{ vault.documents.growthForecast.status }}
                  </span>
                </div>
                <p class="text-sm text-neutral-600 mb-2">12-month projection based on your data</p>
                <p class="text-xs text-neutral-500">Format: {{ vault.documents.growthForecast.format }}</p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="generateForecast"
                  :disabled="generatingForecast"
                  class="px-4 py-2 bg-accent hover:bg-accent-dark text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {{ generatingForecast ? 'Generating...' : 'Generate' }}
                </button>
                <button
                  v-if="vault.documents.growthForecast.lastUpdated"
                  @click="downloadDocument('forecast')"
                  class="px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-sm font-medium transition-colors"
                >
                  Download
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Missing Documents -->
      <div v-if="vault.missingDocuments.length > 0" class="bg-warning/5 rounded-lg p-4 border border-warning/20">
        <h4 class="font-bold text-neutral-900 mb-2">⚠️ Missing Documents</h4>
        <ul class="space-y-1">
          <li v-for="doc in vault.missingDocuments" :key="doc" class="text-sm text-neutral-700">
            • {{ doc }}
          </li>
        </ul>
      </div>

      <!-- Vault Readiness -->
      <div class="bg-neutral-50 rounded-lg p-4">
        <h4 class="font-bold text-neutral-900 mb-3">Vault Readiness Score</h4>
        <div class="w-full bg-neutral-200 rounded-full h-3 overflow-hidden">
          <div 
            class="bg-accent h-full transition-all duration-500"
            :style="{ width: `${vault.readinessScore}%` }"
          ></div>
        </div>
        <p class="text-sm text-neutral-600 mt-2">
          {{ vault.readinessScore }}% Complete - {{ getReadinessLabel(vault.readinessScore) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import API_BASE from '@/config/api'
import { ref, onMounted } from 'vue'

const props = defineProps({
  userId: Number
})

const loading = ref(true)
const generatingPitchDeck = ref(false)
const generatingFinancials = ref(false)
const generatingBusinessPlan = ref(false)
const generatingForecast = ref(false)

// Store the filenames returned by the API so Download buttons use real paths
const downloadFilenames = ref({
  pitchDeck:    null,
  financials:   null,
  businessPlan: null,
  forecast:     null
})

const vault = ref({
  documents: {
    pitchDeck: {},
    financialStatements: {},
    businessPlan: {},
    growthForecast: {}
  },
  readinessScore: 0,
  missingDocuments: [],
  keyMetrics: {
    monthlyRevenue: 0,
    monthlyExpenses: 0,
    monthlyProfit: 0,
    profitMargin: 0
  }
})

const fetchVault = async () => {
  loading.value = true
  try {
    const response = await fetch(`${API_BASE}/api/bizseed/vault/documents/${props.userId}`)
    const data = await response.json()
    
    if (data.success) {
      vault.value = data.vault
    }
  } catch (error) {
    console.error('Failed to fetch vault:', error)
  } finally {
    loading.value = false
  }
}

// ✅ FUNCTIONAL: Generate Pitch Deck
const generatePitchDeck = async () => {
  generatingPitchDeck.value = true
  try {
    const response = await fetch(`${API_BASE}/api/bizseed/vault/generate/pitch-deck`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: props.userId })
    })
    
    const data = await response.json()
    
    if (data.success) {
      downloadFilenames.value.pitchDeck = data.filename
      vault.value.documents.pitchDeck.lastUpdated = new Date().toISOString()
      alert('✅ Pitch deck generated! Click Download to get your PowerPoint.')
    } else {
      alert('❌ Failed: ' + data.error)
    }
  } catch (error) {
    console.error('Pitch deck error:', error)
    alert('❌ Failed to generate pitch deck')
  } finally {
    generatingPitchDeck.value = false
  }
}

// ✅ FUNCTIONAL: Generate Financial Statements
const generateFinancials = async () => {
  generatingFinancials.value = true
  try {
    const response = await fetch(`${API_BASE}/api/bizseed/vault/generate/financials`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: props.userId })
    })
    
    const data = await response.json()
    
    if (data.success) {
      downloadFilenames.value.financials = data.filename
      vault.value.documents.financialStatements.lastUpdated = new Date().toISOString()
      alert('✅ Financial statements generated! Click Download to get your PDF.')
    } else {
      alert('❌ Failed: ' + data.error)
    }
  } catch (error) {
    console.error('Financials error:', error)
    alert('❌ Failed to generate financial statements')
  } finally {
    generatingFinancials.value = false
  }
}

// ✅ FUNCTIONAL: Generate Business Plan
const generateBusinessPlan = async () => {
  generatingBusinessPlan.value = true
  try {
    const response = await fetch(`${API_BASE}/api/bizseed/vault/generate/business-plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: props.userId })
    })
    
    const data = await response.json()
    
    if (data.success) {
      downloadFilenames.value.businessPlan = data.filename
      vault.value.documents.businessPlan.lastUpdated = new Date().toISOString()
      alert('✅ Business plan generated! Click Download to get your PDF.')
    } else {
      alert('❌ Failed: ' + data.error)
    }
  } catch (error) {
    console.error('Business plan error:', error)
    alert('❌ Failed to generate business plan')
  } finally {
    generatingBusinessPlan.value = false
  }
}

// ✅ FUNCTIONAL: Generate Growth Forecast
const generateForecast = async () => {
  generatingForecast.value = true
  try {
    const response = await fetch(`${API_BASE}/api/bizseed/vault/generate/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId: props.userId })
    })
    
    const data = await response.json()
    
    if (data.success) {
      downloadFilenames.value.forecast = data.filename
      vault.value.documents.growthForecast.lastUpdated = new Date().toISOString()
      alert('✅ Growth forecast generated! Click Download to get your Excel.')
    } else {
      alert('❌ Failed: ' + data.error)
    }
  } catch (error) {
    console.error('Forecast error:', error)
    alert('❌ Failed to generate forecast')
  } finally {
    generatingForecast.value = false
  }
}

// ✅ FUNCTIONAL: Download Document
const downloadDocument = (documentType) => {
  const filenameMap = {
    pitchDeck:    downloadFilenames.value.pitchDeck,
    financials:   downloadFilenames.value.financials,
    businessPlan: downloadFilenames.value.businessPlan,
    forecast:     downloadFilenames.value.forecast
  }

  const filename = filenameMap[documentType]
  if (!filename) {
    alert('Please generate the document first before downloading.')
    return
  }

  const url = `${API_BASE}/api/bizseed/downloads/${filename}`
  window.open(url, '_blank')
}

const getReadinessLabel = (score) => {
  if (score < 25) return 'Just Starting'
  if (score < 50) return 'Building Foundation'
  if (score < 75) return 'Nearly Ready'
  return 'Investor Ready'
}

onMounted(() => {
  fetchVault()
})
</script>