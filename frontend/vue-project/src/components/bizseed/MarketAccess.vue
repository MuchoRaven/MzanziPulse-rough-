<template>
  <div class="space-y-5">
    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-warning mx-auto"></div>
      <p class="text-neutral-500 mt-4">Analysing your business data...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-10 bg-red-50 rounded-xl border border-red-200 p-6">
      <p class="text-red-600 font-medium">Could not load market analysis</p>
      <p class="text-sm text-red-400 mt-1">{{ error }}</p>
    </div>

    <template v-else>

      <!-- ══════════════════════════════════════════════════════
           SECTION 1: Revenue Trend
      ══════════════════════════════════════════════════════ -->
      <div class="bg-white border border-neutral-200 rounded-xl p-5">
        <h4 class="font-bold text-neutral-900 mb-4 flex items-center gap-2">
          <span class="text-xl">📈</span> Revenue Trend
        </h4>

        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-neutral-50 rounded-lg p-3 text-center">
            <p class="text-xs text-neutral-500 mb-1">This Month</p>
            <p class="text-xl font-bold text-neutral-900">R{{ fmt(data.revenueTrend.thisMonthRands) }}</p>
          </div>
          <div class="bg-neutral-50 rounded-lg p-3 text-center">
            <p class="text-xs text-neutral-500 mb-1">Last Month</p>
            <p class="text-xl font-bold text-neutral-500">R{{ fmt(data.revenueTrend.lastMonthRands) }}</p>
          </div>
          <div class="bg-neutral-50 rounded-lg p-3 text-center">
            <p class="text-xs text-neutral-500 mb-1">Daily Average</p>
            <p class="text-xl font-bold text-primary">R{{ fmt(data.revenueTrend.dailyAverageRands) }}</p>
          </div>
          <div class="rounded-lg p-3 text-center"
            :class="trendBg(data.revenueTrend.direction)">
            <p class="text-xs text-neutral-500 mb-1">Change</p>
            <p class="text-xl font-bold" :class="trendColor(data.revenueTrend.direction)">
              <span v-if="data.revenueTrend.changePercent !== null">
                {{ data.revenueTrend.changePercent > 0 ? '+' : '' }}{{ data.revenueTrend.changePercent }}%
              </span>
              <span v-else class="text-neutral-400 text-base">No data</span>
            </p>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           SECTION 2: Day-of-Week Performance
      ══════════════════════════════════════════════════════ -->
      <div class="bg-white border border-neutral-200 rounded-xl p-5">
        <h4 class="font-bold text-neutral-900 mb-1 flex items-center gap-2">
          <span class="text-xl">📅</span> Best & Worst Trading Days
        </h4>
        <p class="text-xs text-neutral-400 mb-4">Based on last 90 days of transactions</p>

        <div v-if="data.dayOfWeekPerformance.days.length > 0" class="space-y-2">
          <div
            v-for="d in sortedDays"
            :key="d.day"
            class="flex items-center gap-3"
          >
            <span class="text-xs text-neutral-500 w-20 shrink-0">{{ d.day }}</span>
            <div class="flex-1 bg-neutral-100 rounded-full h-3 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="d.day === data.dayOfWeekPerformance.bestDay ? 'bg-success'
                       : d.day === data.dayOfWeekPerformance.worstDay ? 'bg-red-400' : 'bg-primary'"
                :style="{ width: `${dayBarWidth(d.avgRevenueRands)}%` }"
              ></div>
            </div>
            <span class="text-xs font-semibold text-neutral-700 w-16 text-right shrink-0">
              R{{ fmt(d.avgRevenueRands) }}/day
            </span>
          </div>
        </div>
        <p v-else class="text-sm text-neutral-400 italic">Not enough transactions yet — keep recording sales.</p>

        <div class="mt-4 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          <p class="text-xs text-amber-800">
            <span class="font-semibold">📦 Restock tip: </span>{{ data.dayOfWeekPerformance.restockRecommendation }}
          </p>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           SECTION 3: Category Breakdown
      ══════════════════════════════════════════════════════ -->
      <div class="bg-white border border-neutral-200 rounded-xl p-5">
        <h4 class="font-bold text-neutral-900 mb-4 flex items-center gap-2">
          <span class="text-xl">🏷️</span> Revenue by Category
        </h4>

        <div v-if="data.categoryBreakdown.categories.length > 0" class="space-y-3">
          <div
            v-for="cat in data.categoryBreakdown.categories.slice(0, 6)"
            :key="cat.category"
            class="flex items-center gap-3"
          >
            <span class="text-xs text-neutral-600 w-32 shrink-0 truncate">{{ cat.category.replace(/_/g, ' ') }}</span>
            <div class="flex-1 bg-neutral-100 rounded-full h-3 overflow-hidden">
              <div
                class="h-full bg-primary rounded-full transition-all"
                :style="{ width: `${cat.pctOfRevenue}%` }"
              ></div>
            </div>
            <span class="text-xs font-semibold text-neutral-700 w-12 text-right shrink-0">{{ cat.pctOfRevenue }}%</span>
            <span class="text-xs text-neutral-400 w-20 text-right shrink-0">R{{ fmt(cat.totalRands) }}</span>
          </div>
        </div>

        <!-- Untapped suggestions -->
        <div v-if="data.categoryBreakdown.untappedSuggestions.length" class="mt-4 bg-primary/5 border border-primary/20 rounded-lg p-3">
          <p class="text-xs font-semibold text-primary mb-2">💡 Untapped Revenue Opportunities</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="cat in data.categoryBreakdown.untappedSuggestions"
              :key="cat"
              class="px-2 py-1 bg-white border border-primary/30 text-primary text-xs rounded-full"
            >+ {{ cat.replace(/_/g, ' ') }}</span>
          </div>
          <p class="text-xs text-neutral-500 mt-2">Other {{ data.business.businessType }} businesses earn from these categories — consider adding them.</p>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           SECTION 4: Transaction Quality
      ══════════════════════════════════════════════════════ -->
      <div class="bg-white border border-neutral-200 rounded-xl p-5">
        <h4 class="font-bold text-neutral-900 mb-4 flex items-center gap-2">
          <span class="text-xl">💳</span> Transaction Quality
        </h4>

        <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-xs text-neutral-500 mb-1">Avg Transaction</p>
            <p class="text-2xl font-bold text-neutral-900">R{{ fmt(data.transactionQuality.avgTransactionRands) }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-neutral-500 mb-1">Sales / Active Day</p>
            <p class="text-2xl font-bold text-primary">{{ data.transactionQuality.txnsPerActiveDay }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-neutral-500 mb-1">Total Transactions</p>
            <p class="text-2xl font-bold text-neutral-900">{{ data.transactionQuality.totalIncomeTxns }}</p>
          </div>
        </div>

        <!-- Cash vs Digital bar -->
        <div class="mt-4">
          <div class="flex justify-between text-xs text-neutral-500 mb-1">
            <span>💵 Cash {{ data.transactionQuality.cashPct }}%</span>
            <span>💳 Digital {{ data.transactionQuality.digitalPct }}%</span>
          </div>
          <div class="w-full h-4 bg-neutral-200 rounded-full overflow-hidden flex">
            <div
              class="h-full bg-neutral-500 transition-all"
              :style="{ width: `${data.transactionQuality.cashPct}%` }"
            ></div>
            <div
              class="h-full bg-primary transition-all"
              :style="{ width: `${data.transactionQuality.digitalPct}%` }"
            ></div>
          </div>
          <p v-if="data.transactionQuality.digitalPct < 20" class="text-xs text-warning mt-2">
            ⚠️ Less than 20% digital payments — you may be losing cashless customers.
          </p>
        </div>

        <div class="mt-3 flex gap-4 text-xs text-neutral-500">
          <span>🟡 Micro sales (&lt;R50): {{ data.transactionQuality.microTransactionPct }}%</span>
          <span>🟢 Large sales (R500+): {{ data.transactionQuality.largeTransactionPct }}%</span>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           SECTION 5: Supply Chain Readiness
      ══════════════════════════════════════════════════════ -->
      <div class="bg-white border border-neutral-200 rounded-xl p-5">
        <div class="flex items-center justify-between mb-4">
          <h4 class="font-bold text-neutral-900 flex items-center gap-2">
            <span class="text-xl">🔗</span> Supply Chain Readiness
          </h4>
          <div class="text-right">
            <span
              class="text-2xl font-bold"
              :class="readinessColor(data.supplyChainReadiness.score)"
            >{{ data.supplyChainReadiness.score }}/100</span>
            <p class="text-xs font-semibold" :class="readinessColor(data.supplyChainReadiness.score)">
              {{ data.supplyChainReadiness.scoreLabel }}
            </p>
          </div>
        </div>

        <div class="space-y-3">
          <div
            v-for="(check, key) in data.supplyChainReadiness.breakdown"
            :key="key"
            class="flex items-start gap-3"
          >
            <span class="text-lg mt-0.5 shrink-0">{{ check.met ? '✅' : '❌' }}</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-neutral-800">{{ check.label }}</p>
              <p class="text-xs text-neutral-500">{{ check.impact }}</p>
              <p v-if="check.currentPct !== undefined" class="text-xs text-neutral-400">
                Current: {{ check.currentPct }}%
              </p>
              <p v-if="check.monthsTrading !== undefined" class="text-xs text-neutral-400">
                Trading for: {{ check.monthsTrading }} months
              </p>
              <p v-if="check.estimatedAnnualRands !== undefined" class="text-xs text-neutral-400">
                Est. annual: R{{ fmt(check.estimatedAnnualRands) }}
              </p>
            </div>
            <span class="text-xs font-bold shrink-0" :class="check.met ? 'text-success' : 'text-neutral-300'">
              +{{ check.points }}/{{ check.max }}
            </span>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           SECTION 6: Supplier Opportunities
      ══════════════════════════════════════════════════════ -->
      <div>
        <h4 class="font-bold text-neutral-900 mb-3 flex items-center gap-2">
          <span class="text-xl">🏪</span> Wholesale & Supplier Opportunities
        </h4>

        <div class="space-y-3">
          <div
            v-for="s in data.supplierOpportunities"
            :key="s.company"
            class="bg-white border border-neutral-200 rounded-xl p-4 hover:border-warning transition-colors"
          >
            <div class="flex items-start justify-between gap-3 mb-2">
              <div>
                <h5 class="font-bold text-neutral-900">{{ s.company }}</h5>
                <p class="text-xs text-neutral-500">{{ s.type }}</p>
              </div>
              <div class="text-right shrink-0">
                <p class="text-xs text-neutral-500">Min. order</p>
                <p class="text-sm font-semibold text-neutral-700">{{ s.minOrder }}</p>
              </div>
            </div>

            <p class="text-sm text-neutral-600 mb-3">{{ s.description }}</p>

            <!-- Readiness bar -->
            <div class="mb-3">
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs text-neutral-500">Your readiness</span>
                <span class="text-xs font-bold" :class="s.readinessPct >= 50 ? 'text-success' : 'text-warning'">
                  {{ s.readinessPct }}%
                </span>
              </div>
              <div class="w-full bg-neutral-200 rounded-full h-2 overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="s.readinessPct >= 80 ? 'bg-success' : s.readinessPct >= 50 ? 'bg-warning' : 'bg-red-400'"
                  :style="{ width: `${s.readinessPct}%` }"
                ></div>
              </div>
            </div>

            <!-- Requirements tags -->
            <div class="flex flex-wrap gap-1 mb-3">
              <span
                v-for="req in s.requirements"
                :key="req"
                class="px-2 py-0.5 text-xs rounded-full"
                :class="checkMet(req) ? 'bg-success/10 text-success' : 'bg-neutral-100 text-neutral-500'"
              >
                {{ checkMet(req) ? '✓' : '○' }} {{ req.replace(/_/g, ' ') }}
              </span>
              <span v-if="s.requirements.length === 0" class="text-xs text-success">Open to all businesses</span>
            </div>

            <a
              :href="`https://${s.website}`"
              target="_blank"
              rel="noopener noreferrer"
              class="block w-full text-center px-4 py-2 bg-warning/10 hover:bg-warning/20 text-warning border border-warning/30 rounded-lg text-sm font-medium transition-colors"
            >
              Visit {{ s.website }} ↗
            </a>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════════════════════
           SECTION 7: Growth Opportunities
      ══════════════════════════════════════════════════════ -->
      <div class="bg-gradient-to-br from-primary/5 to-success/5 border border-primary/20 rounded-xl p-5">
        <h4 class="font-bold text-neutral-900 mb-4 flex items-center gap-2">
          <span class="text-xl">🚀</span> Growth Opportunities For You
        </h4>

        <div class="space-y-3">
          <div
            v-for="opp in data.growthOpportunities"
            :key="opp.suggestion"
            class="bg-white rounded-lg p-4 border border-neutral-100"
          >
            <div class="flex items-start gap-3">
              <span
                class="px-2 py-0.5 text-xs font-bold rounded-full shrink-0 mt-0.5"
                :class="impactClass(opp.impact)"
              >{{ opp.impact }}</span>
              <div>
                <p class="font-semibold text-neutral-900 text-sm">{{ opp.suggestion }}</p>
                <p class="text-xs text-neutral-500 mt-0.5">{{ opp.reason }}</p>
                <p class="text-xs text-primary font-medium mt-1.5">→ {{ opp.actionStep }}</p>
              </div>
            </div>
          </div>

          <div v-if="data.growthOpportunities.length === 0" class="text-center py-4 text-neutral-400 text-sm italic">
            Keep recording transactions to unlock personalised growth tips.
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup>
import API_BASE from '@/config/api'
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({ userId: Number })

const loading = ref(true)
const error   = ref(null)
const data    = ref(null)

const authStore = useAuthStore()

const fetchAnalysis = async () => {
  loading.value = true
  error.value   = null
  try {
    const res  = await fetch(`${API_BASE}/api/bizseed/market/analysis/${props.userId}`)
    const json = await res.json()
    if (json.success) {
      data.value = json
    } else {
      error.value = json.error || 'Unknown error'
    }
  } catch (e) {
    error.value = 'Could not connect to server'
    console.error(e)
  } finally {
    loading.value = false
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────

const fmt = (n) => {
  if (n === null || n === undefined) return '—'
  const num = Number(n)
  if (isNaN(num)) return '—'
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + 'M'
  if (num >= 1_000)     return (num / 1_000).toFixed(1) + 'K'
  return num.toLocaleString('en-ZA', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

const trendColor = (dir) => {
  if (dir === 'UP')   return 'text-success'
  if (dir === 'DOWN') return 'text-red-500'
  return 'text-neutral-500'
}

const trendBg = (dir) => {
  if (dir === 'UP')   return 'bg-success/5'
  if (dir === 'DOWN') return 'bg-red-50'
  return 'bg-neutral-50'
}

const readinessColor = (score) => {
  if (score >= 80) return 'text-success'
  if (score >= 55) return 'text-warning'
  if (score >= 30) return 'text-orange-500'
  return 'text-red-500'
}

const impactClass = (impact) => {
  if (impact === 'HIGH')   return 'bg-red-100 text-red-600'
  if (impact === 'MEDIUM') return 'bg-warning/20 text-warning'
  return 'bg-neutral-100 text-neutral-500'
}

// Sort days by DOW (Sun→Sat) for display
const sortedDays = computed(() => {
  if (!data.value) return []
  return [...data.value.dayOfWeekPerformance.days].sort((a, b) => a.dow - b.dow)
})

// Width of day bar as % of the best day
const dayBarWidth = (avgRev) => {
  if (!data.value || !data.value.dayOfWeekPerformance.days.length) return 0
  const max = Math.max(...data.value.dayOfWeekPerformance.days.map(d => d.avgRevenueRands))
  return max > 0 ? Math.round(avgRev / max * 100) : 0
}

// Check whether a readiness check is met (for supplier requirement badges)
const checkMet = (key) => {
  if (!data.value) return false
  const bd = data.value.supplyChainReadiness.breakdown
  const keyMap = {
    'cipc':              'cipc',
    'tax_number':        'taxNumber',
    'consistent_revenue':'consistentRevenue',
    'annual_turnover':   'annualTurnover',
    'digital_payments':  'digitalPayments',
    'trading_history':   'tradingHistory',
  }
  const check = bd[keyMap[key]]
  return check ? check.met : false
}

onMounted(fetchAnalysis)
</script>
