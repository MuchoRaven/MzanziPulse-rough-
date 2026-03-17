<template>
  <div class="space-y-6">

    <!-- ── Balance Cards ──────────────────────────────────────── -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <!-- Total -->
      <div class="sm:col-span-3 bg-gradient-to-br from-primary to-primary-dark text-white rounded-2xl p-6 shadow-lg">
        <p class="text-primary-100 text-sm mb-1">Total Wallet Balance</p>
        <h2 class="text-4xl font-bold mb-4">R{{ balance.total_balance?.toFixed(2) ?? '0.00' }}</h2>
        <div class="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p class="text-primary-100">💵 Cash on Hand</p>
            <p class="text-xl font-semibold">R{{ balance.cash_on_hand?.toFixed(2) ?? '0.00' }}</p>
          </div>
          <div>
            <p class="text-primary-100">🏦 Digital / Bank</p>
            <p class="text-xl font-semibold">R{{ balance.digital_balance?.toFixed(2) ?? '0.00' }}</p>
          </div>
          <div>
            <p class="text-primary-100">📝 Credit Owed</p>
            <p class="text-xl font-semibold">R{{ balance.outstanding_credit?.toFixed(2) ?? '0.00' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Action Buttons ─────────────────────────────────────── -->
    <div class="flex flex-wrap gap-3">
      <button
        @click="openAddModal('INCOME')"
        class="flex items-center gap-2 px-5 py-2.5 bg-success hover:bg-success-dark text-white rounded-xl font-medium transition-colors shadow-sm"
      >
        <span>➕</span> Add Income
      </button>
      <button
        @click="openAddModal('EXPENSE')"
        class="flex items-center gap-2 px-5 py-2.5 bg-danger hover:bg-red-700 text-white rounded-xl font-medium transition-colors shadow-sm"
      >
        <span>➖</span> Add Expense
      </button>
      <button
        @click="showReconcile = true"
        class="flex items-center gap-2 px-5 py-2.5 bg-white border border-neutral-300 hover:border-primary text-neutral-700 rounded-xl font-medium transition-colors shadow-sm"
      >
        <span>🔄</span> Reconcile Cash
      </button>
    </div>

    <!-- ── Today's Summary ────────────────────────────────────── -->
    <div class="bg-white rounded-xl shadow-sm border border-neutral-200 p-5">
      <h3 class="text-sm font-bold text-neutral-500 uppercase tracking-wide mb-3">Today's Summary</h3>
      <div class="grid grid-cols-3 gap-4 text-center">
        <div class="bg-success/5 rounded-xl p-3">
          <p class="text-xs text-neutral-500">Income</p>
          <p class="text-xl font-bold text-success">+R{{ daily.income?.toFixed(2) ?? '0.00' }}</p>
        </div>
        <div class="bg-danger/5 rounded-xl p-3">
          <p class="text-xs text-neutral-500">Expenses</p>
          <p class="text-xl font-bold text-danger">-R{{ daily.expense?.toFixed(2) ?? '0.00' }}</p>
        </div>
        <div
          class="rounded-xl p-3"
          :class="(daily.net ?? 0) >= 0 ? 'bg-primary/5' : 'bg-warning/5'"
        >
          <p class="text-xs text-neutral-500">Net</p>
          <p
            class="text-xl font-bold"
            :class="(daily.net ?? 0) >= 0 ? 'text-primary' : 'text-warning'"
          >{{ (daily.net ?? 0) >= 0 ? '+' : '' }}R{{ daily.net?.toFixed(2) ?? '0.00' }}</p>
        </div>
      </div>
      <p class="text-xs text-neutral-400 mt-3 text-center">{{ daily.transaction_count ?? 0 }} transactions today</p>
    </div>

    <!-- ── Analytics Period Toggle ────────────────────────────── -->
    <div class="bg-white rounded-xl shadow-sm border border-neutral-200 p-5">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-neutral-900">📊 Analytics</h3>
        <div class="flex gap-1 bg-neutral-100 rounded-lg p-1 text-xs">
          <button
            v-for="p in periods"
            :key="p.value"
            @click="selectPeriod(p.value)"
            :class="['px-3 py-1 rounded-md font-medium transition-colors',
              activePeriod === p.value ? 'bg-white shadow text-primary' : 'text-neutral-500 hover:text-neutral-700']"
          >{{ p.label }}</button>
        </div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-success/5 rounded-xl p-4">
          <p class="text-xs text-neutral-500">Income</p>
          <p class="text-lg font-bold text-success">R{{ fmtK(analytics.total_income) }}</p>
        </div>
        <div class="bg-danger/5 rounded-xl p-4">
          <p class="text-xs text-neutral-500">Expenses</p>
          <p class="text-lg font-bold text-danger">R{{ fmtK(analytics.total_expenses) }}</p>
        </div>
        <div class="bg-primary/5 rounded-xl p-4">
          <p class="text-xs text-neutral-500">Profit</p>
          <p class="text-lg font-bold" :class="(analytics.net_profit ?? 0) >= 0 ? 'text-primary' : 'text-warning'">
            R{{ fmtK(analytics.net_profit) }}
          </p>
        </div>
        <div class="bg-neutral-50 rounded-xl p-4">
          <p class="text-xs text-neutral-500">Margin</p>
          <p class="text-lg font-bold text-neutral-700">{{ analytics.profit_margin?.toFixed(1) ?? '0.0' }}%</p>
        </div>
      </div>

      <!-- Payment method split -->
      <div v-if="analytics.payment_method_breakdown" class="mt-4">
        <p class="text-xs font-semibold text-neutral-500 uppercase tracking-wide mb-2">Payment Split</p>
        <div class="flex gap-3 text-sm">
          <div class="flex-1 bg-neutral-50 rounded-lg p-3">
            <p class="text-xs text-neutral-500">💵 Cash Income</p>
            <p class="font-bold">R{{ fmtK(analytics.payment_method_breakdown.CASH?.income) }}</p>
          </div>
          <div class="flex-1 bg-neutral-50 rounded-lg p-3">
            <p class="text-xs text-neutral-500">🏦 Digital Income</p>
            <p class="font-bold">R{{ fmtK(analytics.payment_method_breakdown.DIGITAL?.income) }}</p>
          </div>
        </div>
      </div>

      <div v-if="analytics.top_income_category" class="mt-4 flex flex-wrap gap-3 text-xs">
        <span class="px-3 py-1.5 bg-success/10 text-success rounded-full font-medium">
          🏆 Top income: {{ fmtCategory(analytics.top_income_category) }}
        </span>
        <span v-if="analytics.top_expense_category" class="px-3 py-1.5 bg-danger/10 text-danger rounded-full font-medium">
          💸 Top expense: {{ fmtCategory(analytics.top_expense_category) }}
        </span>
        <span class="px-3 py-1.5 rounded-full font-medium"
          :class="analytics.cash_flow_trend === 'POSITIVE' ? 'bg-success/10 text-success'
                : analytics.cash_flow_trend === 'NEGATIVE' ? 'bg-danger/10 text-danger'
                : 'bg-neutral-100 text-neutral-600'"
        >{{ analytics.cash_flow_trend === 'POSITIVE' ? '📈' : analytics.cash_flow_trend === 'NEGATIVE' ? '📉' : '➡️' }} {{ analytics.cash_flow_trend }}</span>
      </div>
    </div>

    <!-- ── Transaction History ─────────────────────────────────── -->
    <div class="bg-white rounded-xl shadow-sm border border-neutral-200 overflow-hidden">
      <div class="px-5 py-4 border-b border-neutral-200 flex items-center justify-between">
        <h3 class="font-bold text-neutral-900">Transaction History</h3>
        <button
          @click="showFilters = !showFilters"
          class="flex items-center gap-1.5 text-xs font-medium text-neutral-500 hover:text-primary transition-colors"
        >🔍 Filter</button>
      </div>

      <!-- Filters -->
      <div v-if="showFilters" class="px-5 py-3 bg-neutral-50 border-b border-neutral-200 flex flex-wrap gap-3">
        <select v-model="filter.type" class="text-sm border border-neutral-200 rounded-lg px-3 py-1.5 bg-white">
          <option value="">All Types</option>
          <option value="INCOME">Income</option>
          <option value="EXPENSE">Expense</option>
        </select>
        <select v-model="filter.paymentMethod" class="text-sm border border-neutral-200 rounded-lg px-3 py-1.5 bg-white">
          <option value="">All Methods</option>
          <option value="CASH">💵 Cash</option>
          <option value="DIGITAL">🏦 Digital</option>
          <option value="CREDIT">📝 Credit</option>
        </select>
        <button
          @click="fetchTransactions"
          class="px-4 py-1.5 bg-primary text-white text-sm rounded-lg font-medium"
        >Apply</button>
        <button
          @click="clearFilters"
          class="px-4 py-1.5 text-neutral-500 text-sm rounded-lg font-medium hover:text-neutral-700"
        >Clear</button>
      </div>

      <!-- Loading -->
      <div v-if="txLoading" class="py-10 text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="transactions.length === 0" class="py-12 text-center">
        <span class="text-5xl block mb-3">📊</span>
        <p class="text-neutral-600 font-medium">No transactions yet</p>
        <p class="text-neutral-400 text-sm mt-1">Add your first income or expense above</p>
      </div>

      <!-- List -->
      <div v-else class="divide-y divide-neutral-100">
        <div
          v-for="tx in visibleTransactions"
          :key="tx.transaction_id"
          class="px-5 py-4 hover:bg-neutral-50 transition-colors flex items-start justify-between gap-4"
        >
          <div class="flex items-start gap-3 flex-1 min-w-0">
            <div
              class="w-9 h-9 rounded-full flex items-center justify-center text-lg shrink-0"
              :class="tx.type === 'INCOME' ? 'bg-success/10' : 'bg-danger/10'"
            >{{ payIcon(tx.payment_method) }}</div>
            <div class="min-w-0">
              <p class="font-medium text-neutral-900 truncate">{{ tx.description || '—' }}</p>
              <div class="flex flex-wrap items-center gap-2 mt-0.5">
                <span class="text-xs text-neutral-400">{{ fmtDate(tx.date) }}</span>
                <span class="text-xs text-neutral-300">•</span>
                <span class="text-xs px-2 py-0.5 bg-neutral-100 rounded-full text-neutral-600">
                  {{ fmtCategory(tx.category) }}
                </span>
                <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                  :class="tx.payment_method === 'CASH' ? 'bg-amber-50 text-amber-700'
                        : tx.payment_method === 'DIGITAL' ? 'bg-blue-50 text-blue-700'
                        : 'bg-purple-50 text-purple-700'"
                >{{ tx.payment_method }}</span>
              </div>
            </div>
          </div>
          <div class="text-right shrink-0">
            <p
              class="text-base font-bold"
              :class="tx.type === 'INCOME' ? 'text-success' : 'text-danger'"
            >{{ tx.type === 'INCOME' ? '+' : '-' }}R{{ tx.amount.toFixed(2) }}</p>
            <button
              @click="confirmDelete(tx)"
              class="text-xs text-neutral-300 hover:text-danger transition-colors mt-0.5"
            >✕</button>
          </div>
        </div>
      </div>

      <!-- Expand / Collapse -->
      <div v-if="transactions.length > COLLAPSED_LIMIT" class="px-5 py-3 border-t border-neutral-100">
        <button
          @click="txExpanded = !txExpanded"
          class="w-full text-sm font-medium text-primary hover:text-primary-dark transition-colors"
        >
          {{ txExpanded ? 'Show less ▴' : `Show ${transactions.length - COLLAPSED_LIMIT} more ▾` }}
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════ -->
    <!-- ADD TRANSACTION MODAL                                      -->
    <!-- ══════════════════════════════════════════════════════════ -->
    <div
      v-if="showAddModal"
      class="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-0 sm:p-4"
      @click.self="showAddModal = false"
    >
      <div class="bg-white w-full sm:max-w-md sm:rounded-2xl rounded-t-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-lg font-bold text-neutral-900">
            {{ newTx.type === 'INCOME' ? '➕ Add Income' : '➖ Add Expense' }}
          </h3>
          <button @click="showAddModal = false" class="text-neutral-400 hover:text-neutral-700 text-2xl leading-none">×</button>
        </div>

        <!-- Type toggle -->
        <div class="flex gap-2 mb-5">
          <button
            @click="newTx.type = 'INCOME'"
            :class="['flex-1 py-2.5 rounded-xl font-semibold text-sm transition-colors',
              newTx.type === 'INCOME' ? 'bg-success text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200']"
          >💰 Income</button>
          <button
            @click="newTx.type = 'EXPENSE'"
            :class="['flex-1 py-2.5 rounded-xl font-semibold text-sm transition-colors',
              newTx.type === 'EXPENSE' ? 'bg-danger text-white' : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200']"
          >💸 Expense</button>
        </div>

        <!-- Amount -->
        <div class="mb-4">
          <label class="text-sm font-medium text-neutral-700 block mb-1">Amount (R)</label>
          <input
            v-model.number="newTx.amount"
            type="number"
            placeholder="0.00"
            step="0.01"
            min="0.01"
            class="w-full border border-neutral-300 rounded-xl px-4 py-3 text-xl font-bold focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Description -->
        <div class="mb-4">
          <label class="text-sm font-medium text-neutral-700 block mb-1">Description</label>
          <input
            v-model="newTx.description"
            type="text"
            placeholder="What is this for?"
            class="w-full border border-neutral-300 rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Payment Method + Category -->
        <div class="grid grid-cols-2 gap-3 mb-5">
          <div>
            <label class="text-sm font-medium text-neutral-700 block mb-1">Payment Method</label>
            <select v-model="newTx.paymentMethod"
              class="w-full border border-neutral-300 rounded-xl px-3 py-2.5 focus:outline-none focus:border-primary text-sm">
              <option value="CASH">💵 Cash</option>
              <option value="DIGITAL">🏦 Bank / EFT</option>
              <option value="CREDIT">📝 Credit (Book)</option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-neutral-700 block mb-1">Category</label>
            <select v-model="newTx.category"
              class="w-full border border-neutral-300 rounded-xl px-3 py-2.5 focus:outline-none focus:border-primary text-sm">
              <option value="SALES">Sales</option>
              <option value="SERVICES">Services</option>
              <option value="STOCK_PURCHASE">Stock Purchase</option>
              <option value="RENT">Rent</option>
              <option value="UTILITIES">Utilities</option>
              <option value="TRANSPORT">Transport</option>
              <option value="MARKETING">Marketing</option>
              <option value="GROCERIES">Groceries</option>
              <option value="AIRTIME">Airtime</option>
              <option value="OTHER">Other</option>
            </select>
          </div>
        </div>

        <!-- Error -->
        <div v-if="txError" class="mb-4 bg-danger/10 text-danger rounded-xl px-4 py-3 text-sm font-medium">
          {{ txError }}
        </div>

        <button
          @click="submitTransaction"
          :disabled="!canSubmit || txSaving"
          class="w-full py-3 rounded-xl font-bold text-white transition-colors disabled:opacity-50"
          :class="newTx.type === 'INCOME' ? 'bg-success hover:bg-success-dark' : 'bg-danger hover:bg-red-700'"
        >
          {{ txSaving ? 'Saving…' : 'Save Transaction' }}
        </button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════ -->
    <!-- RECONCILE MODAL                                            -->
    <!-- ══════════════════════════════════════════════════════════ -->
    <div
      v-if="showReconcile"
      class="fixed inset-0 bg-black/50 flex items-end sm:items-center justify-center z-50 p-0 sm:p-4"
      @click.self="showReconcile = false"
    >
      <div class="bg-white w-full sm:max-w-md sm:rounded-2xl rounded-t-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-lg font-bold text-neutral-900">🔄 Reconcile Cash</h3>
          <button @click="showReconcile = false" class="text-neutral-400 hover:text-neutral-700 text-2xl leading-none">×</button>
        </div>

        <div class="bg-neutral-50 rounded-xl p-4 mb-4 text-sm">
          <p class="text-neutral-500">According to your records, you should have:</p>
          <p class="text-2xl font-bold text-neutral-900 mt-1">R{{ balance.cash_on_hand?.toFixed(2) ?? '0.00' }} cash</p>
        </div>

        <div class="mb-5">
          <label class="text-sm font-medium text-neutral-700 block mb-1">Actual cash you counted (R)</label>
          <input
            v-model.number="reconcileInput"
            type="number"
            placeholder="0.00"
            step="0.01"
            class="w-full border border-neutral-300 rounded-xl px-4 py-3 text-xl font-bold focus:outline-none focus:border-primary"
          />
        </div>

        <!-- Result -->
        <div v-if="reconcileResult" class="mb-5 rounded-xl p-4 border"
          :class="reconcileResult.status === 'MATCH' ? 'bg-success/5 border-success/30'
                : reconcileResult.status === 'MINOR_DISCREPANCY' ? 'bg-warning/5 border-warning/30'
                : 'bg-danger/5 border-danger/30'"
        >
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xl">{{ reconcileResult.status === 'MATCH' ? '✅' : reconcileResult.status === 'MINOR_DISCREPANCY' ? '⚠️' : '🚨' }}</span>
            <span class="font-bold">{{ reconcileResult.status.replace(/_/g, ' ') }}</span>
          </div>
          <div class="grid grid-cols-2 gap-2 text-sm mb-3">
            <div>
              <p class="text-neutral-500 text-xs">Expected</p>
              <p class="font-bold">R{{ reconcileResult.expected_cash.toFixed(2) }}</p>
            </div>
            <div>
              <p class="text-neutral-500 text-xs">Actual</p>
              <p class="font-bold">R{{ reconcileResult.actual_cash.toFixed(2) }}</p>
            </div>
            <div>
              <p class="text-neutral-500 text-xs">Difference</p>
              <p class="font-bold" :class="reconcileResult.difference < 0 ? 'text-danger' : 'text-success'">
                {{ reconcileResult.difference >= 0 ? '+' : '' }}R{{ reconcileResult.difference.toFixed(2) }}
              </p>
            </div>
            <div>
              <p class="text-neutral-500 text-xs">% Off</p>
              <p class="font-bold">{{ Math.abs(reconcileResult.difference_percentage).toFixed(2) }}%</p>
            </div>
          </div>
          <ul v-if="reconcileResult.suggestions.length" class="space-y-1">
            <li v-for="s in reconcileResult.suggestions" :key="s" class="flex items-start gap-1.5 text-xs text-neutral-600">
              <span class="mt-0.5 text-warning">💡</span> {{ s }}
            </li>
          </ul>
        </div>

        <button
          @click="doReconcile"
          :disabled="reconcileInput === '' || reconcileInput === null"
          class="w-full py-3 bg-primary hover:bg-primary-dark text-white rounded-xl font-bold disabled:opacity-50 transition-colors"
        >Check</button>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════ -->
    <!-- DELETE CONFIRM MODAL                                       -->
    <!-- ══════════════════════════════════════════════════════════ -->
    <div
      v-if="txToDelete"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      @click.self="txToDelete = null"
    >
      <div class="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
        <h3 class="font-bold text-neutral-900 mb-2">Delete Transaction?</h3>
        <p class="text-sm text-neutral-600 mb-1">
          <strong>{{ txToDelete.description }}</strong>
        </p>
        <p class="text-sm text-neutral-500 mb-5">
          {{ txToDelete.type === 'INCOME' ? '+' : '-' }}R{{ txToDelete.amount.toFixed(2) }} · {{ fmtDate(txToDelete.date) }}
        </p>
        <p class="text-xs text-neutral-400 mb-5">This will reverse the balance effect permanently.</p>
        <div class="flex gap-3">
          <button
            @click="txToDelete = null"
            class="flex-1 py-2.5 border border-neutral-300 rounded-xl text-sm font-medium text-neutral-600 hover:bg-neutral-50"
          >Cancel</button>
          <button
            @click="deleteTransaction"
            class="flex-1 py-2.5 bg-danger text-white rounded-xl text-sm font-bold hover:bg-red-700"
          >Delete</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
import API_BASE from '@/config/api'
const API = API_BASE

// ── State ─────────────────────────────────────────────────────
const balance        = ref({})
const daily          = ref({})
const analytics      = ref({})
const transactions   = ref([])
const txLoading      = ref(false)
const txExpanded     = ref(false)
const COLLAPSED_LIMIT = 10

const showAddModal   = ref(false)
const showReconcile  = ref(false)
const showFilters    = ref(false)
const txError        = ref('')
const txSaving       = ref(false)
const txToDelete     = ref(null)

const activePeriod   = ref('30days')
const periods = [
  { label: '7d',  value: '7days'  },
  { label: '30d', value: '30days' },
  { label: '90d', value: '90days' },
  { label: 'All', value: 'all'    },
]

const filter = ref({ type: '', paymentMethod: '' })

const newTx = ref({
  type:          'INCOME',
  amount:        '',
  description:   '',
  paymentMethod: 'CASH',
  category:      'SALES',
})

const reconcileInput  = ref('')
const reconcileResult = ref(null)

// ── Computed ──────────────────────────────────────────────────
const walletId = computed(() => authStore.user?.walletId)

const visibleTransactions = computed(() =>
  txExpanded.value ? transactions.value : transactions.value.slice(0, COLLAPSED_LIMIT)
)

const canSubmit = computed(() =>
  newTx.value.amount > 0 && newTx.value.description.trim().length > 0
)

// ── Fetch helpers ─────────────────────────────────────────────
const fetchBalance = async () => {
  try {
    const r = await fetch(`${API}/api/wallet/${authStore.user.id}/balance`)
    const d = await r.json()
    if (d.success) balance.value = d
  } catch (e) { console.error('balance fetch:', e) }
}

const fetchDaily = async () => {
  if (!walletId.value) return
  try {
    const today = new Date().toISOString().split('T')[0]
    const r = await fetch(`${API}/api/wallet/${walletId.value}/daily-summary?date=${today}`)
    const d = await r.json()
    if (d.success) daily.value = d
  } catch (e) { console.error('daily fetch:', e) }
}

const fetchAnalytics = async (period = activePeriod.value) => {
  if (!walletId.value) return
  try {
    const r = await fetch(`${API}/api/wallet/${walletId.value}/analytics?period=${period}`)
    const d = await r.json()
    if (d.success) analytics.value = d
  } catch (e) { console.error('analytics fetch:', e) }
}

const fetchTransactions = async () => {
  if (!walletId.value) return
  txLoading.value = true
  try {
    let url = `${API}/api/wallet/${walletId.value}/transactions?limit=50`
    if (filter.value.type)          url += `&type=${filter.value.type}`
    if (filter.value.paymentMethod) url += `&paymentMethod=${filter.value.paymentMethod}`
    const r = await fetch(url)
    const d = await r.json()
    if (d.success) transactions.value = d.transactions
  } catch (e) { console.error('tx fetch:', e) }
  finally { txLoading.value = false }
}

const refreshAll = () => Promise.all([fetchBalance(), fetchDaily(), fetchAnalytics(), fetchTransactions()])

// ── Actions ───────────────────────────────────────────────────
const openAddModal = (type) => {
  newTx.value.type = type
  txError.value    = ''
  showAddModal.value = true
}

const submitTransaction = async () => {
  if (!walletId.value) return
  txSaving.value = true
  txError.value  = ''
  try {
    const r = await fetch(`${API}/api/wallet/${walletId.value}/transactions`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(newTx.value),
    })
    const d = await r.json()
    if (d.success) {
      showAddModal.value = false
      resetNewTx()
      await refreshAll()
    } else if (d.code === 'INSUFFICIENT_BALANCE') {
      txError.value = `❌ ${d.error}`
    } else {
      txError.value = d.error || 'Failed to save'
    }
  } catch (e) {
    txError.value = 'Network error — please try again'
  } finally {
    txSaving.value = false
  }
}

const confirmDelete = (tx) => { txToDelete.value = tx }

const deleteTransaction = async () => {
  if (!txToDelete.value || !walletId.value) return
  try {
    await fetch(
      `${API}/api/wallet/transactions/${txToDelete.value.transaction_id}?walletId=${walletId.value}`,
      { method: 'DELETE' }
    )
    txToDelete.value = null
    await refreshAll()
  } catch (e) { console.error('delete error:', e) }
}

const doReconcile = async () => {
  if (!walletId.value) return
  reconcileResult.value = null
  try {
    const r = await fetch(`${API}/api/wallet/${walletId.value}/reconcile`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ actualCash: reconcileInput.value }),
    })
    const d = await r.json()
    if (d.success) reconcileResult.value = d
  } catch (e) { console.error('reconcile error:', e) }
}

const selectPeriod = (p) => {
  activePeriod.value = p
  fetchAnalytics(p)
}

const clearFilters = () => {
  filter.value = { type: '', paymentMethod: '' }
  fetchTransactions()
}

const resetNewTx = () => {
  newTx.value = { type: 'INCOME', amount: '', description: '', paymentMethod: 'CASH', category: 'SALES' }
}

// ── Formatters ────────────────────────────────────────────────
const payIcon = (m) => ({ CASH: '💵', DIGITAL: '🏦', CREDIT: '📝' }[m] || '💰')

const fmtDate = (d) => {
  if (!d) return ''
  const date = new Date(d)
  const now  = new Date()
  const diff = Math.floor((now - date) / 86400000)
  if (diff === 0) return 'Today'
  if (diff === 1) return 'Yesterday'
  if (diff < 7)  return `${diff} days ago`
  return date.toLocaleDateString('en-ZA', { day: 'numeric', month: 'short' })
}

const fmtCategory = (c) => (c || 'Other').replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

const fmtK = (n) => {
  if (n == null) return '0'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000)    return (n / 1000).toFixed(1) + 'K'
  return n.toFixed(2)
}

onMounted(refreshAll)
</script>
