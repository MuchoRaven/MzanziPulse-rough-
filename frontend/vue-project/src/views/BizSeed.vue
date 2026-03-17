<template>
  <div class="min-h-screen bg-neutral-50">
    <!-- Header -->
    <div class="bg-gradient-to-r from-success to-success-dark text-white px-4 py-6 lg:px-6">
      <div class="max-w-7xl mx-auto">
        <div class="flex items-center gap-3 mb-2">
          <span class="text-4xl">🌱</span>
          <h1 class="text-3xl font-bold">Biz-Seed</h1>
        </div>
        <p class="text-green-100 text-lg">Investment Readiness Platform</p>
      </div>
    </div>

    <!-- Investment Readiness Score -->
    <div class="max-w-7xl mx-auto px-4 lg:px-6 mt-6 mb-6">
      <div class="bg-white rounded-2xl shadow-xl p-6">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-xl font-bold text-neutral-900">Investment Readiness Score</h2>
            <p class="text-sm text-neutral-600">Your journey to formal funding</p>
          </div>
          <div class="text-right">
            <div class="text-4xl font-bold text-success">{{ dashboardData.investmentReadiness }}%</div>
            <p class="text-sm text-neutral-500">{{ getReadinessLabel(dashboardData.investmentReadiness) }}</p>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-neutral-200 rounded-full h-4 overflow-hidden">
          <div
            class="progress-bar-fill bg-gradient-to-r from-success to-success-dark h-full transition-all duration-1000 ease-out"
            :style="{ width: `${dashboardData.investmentReadiness}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- 4 Pillars -->
    <div class="max-w-7xl mx-auto px-4 lg:px-6 pb-8 space-y-6">
      
      <!-- Pillar 1: Compliance & Formalization -->
      <section class="bg-white rounded-xl shadow-md overflow-hidden">
        <div 
          @click="togglePillar('compliance')"
          class="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-2xl">
              ✅
            </div>
            <div>
              <h3 class="text-lg font-bold text-neutral-900">Compliance & Formalization</h3>
              <p class="text-sm text-neutral-600">CIPC, SARS, B-BBEE, POPIA</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <div class="text-2xl font-bold" :class="getScoreColor(dashboardData.pillars.compliance.score)">
                {{ dashboardData.pillars.compliance.score }}%
              </div>
              <span class="text-xs px-2 py-1 rounded" :class="getStatusBadge(dashboardData.pillars.compliance.status)">
                {{ dashboardData.pillars.compliance.status }}
              </span>
            </div>
            <span class="text-2xl transition-transform" :class="{ 'rotate-180': expandedPillars.compliance }">
              ▼
            </span>
          </div>
        </div>

        <div v-if="expandedPillars.compliance" class="border-t border-neutral-200 p-6">
          <ComplianceTracker :userId="authStore.user.id" />
        </div>
      </section>

      <!-- Pillar 2: Investor-Ready Vault -->
      <section class="bg-white rounded-xl shadow-md overflow-hidden">
        <div 
          @click="togglePillar('investorVault')"
          class="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center text-2xl">
              📊
            </div>
            <div>
              <h3 class="text-lg font-bold text-neutral-900">Investor-Ready Vault</h3>
              <p class="text-sm text-neutral-600">Pitch decks, financials, forecasts</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <div class="text-2xl font-bold" :class="getScoreColor(dashboardData.pillars.investorVault.score)">
                {{ dashboardData.pillars.investorVault.score }}%
              </div>
              <span class="text-xs px-2 py-1 rounded" :class="getStatusBadge(dashboardData.pillars.investorVault.status)">
                {{ dashboardData.pillars.investorVault.status }}
              </span>
            </div>
            <span class="text-2xl transition-transform" :class="{ 'rotate-180': expandedPillars.investorVault }">
              ▼
            </span>
          </div>
        </div>

        <div v-if="expandedPillars.investorVault" class="border-t border-neutral-200 p-6">
          <InvestorVault :userId="authStore.user.id" />
        </div>
      </section>

      <!-- Pillar 3: Funding & Grant Matching -->
      <section class="bg-white rounded-xl shadow-md overflow-hidden">
        <div 
          @click="togglePillar('fundingAccess')"
          class="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-success/10 rounded-full flex items-center justify-center text-2xl">
              💰
            </div>
            <div>
              <h3 class="text-lg font-bold text-neutral-900">Funding & Grant Matching</h3>
              <p class="text-sm text-neutral-600">NYDA, SEFA, NEF, Private funding</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <div class="text-2xl font-bold" :class="getScoreColor(dashboardData.pillars.fundingAccess.score)">
                {{ dashboardData.pillars.fundingAccess.score }}%
              </div>
              <span class="text-xs px-2 py-1 rounded" :class="getStatusBadge(dashboardData.pillars.fundingAccess.status)">
                {{ dashboardData.pillars.fundingAccess.status }}
              </span>
            </div>
            <span class="text-2xl transition-transform" :class="{ 'rotate-180': expandedPillars.fundingAccess }">
              ▼
            </span>
          </div>
        </div>

        <div v-if="expandedPillars.fundingAccess" class="border-t border-neutral-200 p-6">
          <GrantMatcher :userId="authStore.user.id" />
        </div>
      </section>

      <!-- Pillar 4: Supply Chain & Market Access -->
      <section class="bg-white rounded-xl shadow-md overflow-hidden">
        <div 
          @click="togglePillar('marketAccess')"
          class="flex items-center justify-between p-6 cursor-pointer hover:bg-neutral-50 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-warning/10 rounded-full flex items-center justify-center text-2xl">
              🏪
            </div>
            <div>
              <h3 class="text-lg font-bold text-neutral-900">Supply Chain & Market Access</h3>
              <p class="text-sm text-neutral-600">Vendor onboarding, pricing optimization</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <div class="text-2xl font-bold" :class="getScoreColor(dashboardData.pillars.marketAccess.score)">
                {{ dashboardData.pillars.marketAccess.score }}%
              </div>
              <span class="text-xs px-2 py-1 rounded" :class="getStatusBadge(dashboardData.pillars.marketAccess.status)">
                {{ dashboardData.pillars.marketAccess.status }}
              </span>
            </div>
            <span class="text-2xl transition-transform" :class="{ 'rotate-180': expandedPillars.marketAccess }">
              ▼
            </span>
          </div>
        </div>

        <div v-if="expandedPillars.marketAccess" class="border-t border-neutral-200 p-6">
          <MarketAccess :userId="authStore.user.id" />
        </div>
      </section>

      <!-- Next Steps -->
      <section class="bg-gradient-to-br from-primary/5 to-success/5 rounded-xl p-6 border border-primary/20">
        <h3 class="text-lg font-bold text-neutral-900 mb-4">🎯 Recommended Next Steps</h3>
        <div class="space-y-3">
          <div
            v-for="(step, index) in dashboardData.nextSteps"
            :key="index"
            class="flex items-center gap-3 p-3 bg-white rounded-lg"
          >
            <span class="text-2xl">{{ getPriorityIcon(step.priority) }}</span>
            <div class="flex-1">
              <p class="font-medium text-neutral-900">{{ step.action }}</p>
              <p class="text-xs text-neutral-500">{{ step.pillar }}</p>
            </div>
            <span
              class="text-xs font-bold px-2 py-1 rounded"
              :class="getPriorityClass(step.priority)"
            >
              {{ step.priority }}
            </span>
          </div>
        </div>
      </section>

      <!-- AI Investment Insights -->
      <section v-if="dashboardData.aiInsight" class="bg-white rounded-xl shadow-md p-6 border-l-4 border-primary">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-2xl">🧠</span>
          <h3 class="text-lg font-bold text-neutral-900">AI Investment Analysis</h3>
          <span class="text-xs bg-primary/10 text-primary px-2 py-1 rounded ml-auto">Powered by DeepSeek</span>
        </div>
        <p class="text-neutral-700 leading-relaxed mb-5">{{ dashboardData.aiInsight }}</p>

        <h4 class="text-sm font-bold text-neutral-800 mb-3">This week's actions:</h4>
        <div class="space-y-3">
          <div
            v-for="(action, i) in dashboardData.aiWeeklyActions"
            :key="i"
            class="flex items-start gap-3 p-3 bg-neutral-50 rounded-lg"
          >
            <span class="text-lg mt-0.5">{{ i === 0 ? '1️⃣' : i === 1 ? '2️⃣' : '3️⃣' }}</span>
            <div class="flex-1">
              <p class="font-medium text-neutral-900 text-sm">{{ action.action }}</p>
              <p class="text-xs text-neutral-500 mt-0.5">{{ action.why }}</p>
            </div>
            <span
              class="text-xs font-bold px-2 py-1 rounded shrink-0"
              :class="{
                'bg-success/10 text-success': action.effort === 'LOW',
                'bg-warning/10 text-warning': action.effort === 'MEDIUM',
                'bg-danger/10 text-danger': action.effort === 'HIGH'
              }"
            >{{ action.effort }}</span>
          </div>
        </div>
      </section>

      <!-- AI Insights loading placeholder -->
      <section v-else-if="loadingDashboard" class="bg-white rounded-xl shadow-md p-6 border-l-4 border-neutral-200 animate-pulse">
        <div class="flex items-center gap-2 mb-3">
          <div class="w-8 h-8 bg-neutral-200 rounded-full"></div>
          <div class="h-5 w-48 bg-neutral-200 rounded"></div>
        </div>
        <div class="space-y-2">
          <div class="h-4 bg-neutral-200 rounded w-full"></div>
          <div class="h-4 bg-neutral-200 rounded w-5/6"></div>
          <div class="h-4 bg-neutral-200 rounded w-4/6"></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import API_BASE from '@/config/api'
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import ComplianceTracker from '../components/bizseed/ComplianceTracker.vue'
import InvestorVault from '../components/bizseed/InvestorVault.vue'
import GrantMatcher from '../components/bizseed/GrantMatcher.vue'
import MarketAccess from '../components/bizseed/MarketAccess.vue'

const authStore = useAuthStore()

const loadingDashboard = ref(true)

const dashboardData = ref({
  investmentReadiness: 0,
  pillars: {
    compliance: { score: 0, status: 'LOADING' },
    investorVault: { score: 0, status: 'LOADING' },
    fundingAccess: { score: 0, status: 'LOADING' },
    marketAccess: { score: 0, status: 'LOADING' }
  },
  nextSteps: [],
  estimatedFunding: 0,
  documentsReady: 0,
  documentsMissing: 0,
  grantsMatched: 0
})

const expandedPillars = ref({
  compliance: true,
  investorVault: false,
  fundingAccess: false,
  marketAccess: false
})

const togglePillar = (pillar) => {
  expandedPillars.value[pillar] = !expandedPillars.value[pillar]
}

const fetchDashboard = async () => {
  try {
    const response = await fetch(`${API_BASE}/api/bizseed/dashboard/${authStore.user.id}`)
    const data = await response.json()
    
    if (data.success) {
      // ✅ Use REAL calculated scores
      dashboardData.value = data.dashboard
      loadingDashboard.value = false

      // Animate progress bars
      setTimeout(() => {
        animateProgressBars()
      }, 100)
    }
  } catch (error) {
    console.error('Failed to fetch Biz-Seed dashboard:', error)
    loadingDashboard.value = false
  }
}

// ✅ NEW: Animate progress bars on load
const animateProgressBars = () => {
  const progressBars = document.querySelectorAll('.progress-bar-fill')
  progressBars.forEach(bar => {
    const targetWidth = bar.style.width
    bar.style.width = '0%'
    setTimeout(() => {
      bar.style.width = targetWidth
    }, 50)
  })
}

const getReadinessLabel = (score) => {
  if (score < 25) return 'Just Starting'
  if (score < 50) return 'Building Foundation'
  if (score < 75) return 'Nearly Ready'
  return 'Investor Ready'
}

const getScoreColor = (score) => {
  if (score < 25) return 'text-danger'
  if (score < 50) return 'text-warning'
  if (score < 75) return 'text-primary'
  return 'text-success'
}

const getStatusBadge = (status) => {
  const badges = {
    'CRITICAL': 'bg-danger/10 text-danger',
    'NEEDS_WORK': 'bg-warning/10 text-warning',
    'MODERATE': 'bg-primary/10 text-primary',
    'GOOD': 'bg-success/10 text-success',
    'EXCELLENT': 'bg-success/20 text-success-dark'
  }
  return badges[status] || 'bg-neutral-100 text-neutral-600'
}

const getPriorityIcon = (priority) => {
  return priority === 'HIGH' ? '🔥' : priority === 'MEDIUM' ? '⚡' : '💡'
}

const getPriorityClass = (priority) => {
  const classes = {
    'HIGH': 'bg-danger text-white',
    'MEDIUM': 'bg-warning text-white',
    'LOW': 'bg-neutral-200 text-neutral-700'
  }
  return classes[priority] || 'bg-neutral-100'
}

onMounted(() => {
  fetchDashboard()
})
</script>