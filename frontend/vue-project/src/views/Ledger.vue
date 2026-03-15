<template>
  <div class="min-h-screen bg-neutral-50 ledger-container">

    <!-- ═══════════════════════════════════════════════════════════
         STATEMENT HEADER
    ═══════════════════════════════════════════════════════════ -->
    <div class="bg-white border-b-2 border-neutral-200 px-4 py-6 lg:px-8 ledger-header">
      <div class="max-w-7xl mx-auto">
        <!-- Letterhead -->
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
          <div>
            <div class="flex items-center gap-3 mb-1">
              <span class="text-3xl">📖</span>
              <h1 class="text-2xl lg:text-3xl font-bold text-neutral-900">Transaction Ledger</h1>
            </div>
            <p class="text-lg font-semibold text-primary">{{ businessName }}</p>
            <p class="text-sm text-neutral-500">{{ userLocation }}</p>
          </div>
          <div class="text-left sm:text-right">
            <p class="text-xs text-neutral-500 uppercase tracking-wide mb-1">Statement Period</p>
            <p class="font-semibold text-neutral-900">
              {{ formatDisplayDate(filters.startDate) }} — {{ formatDisplayDate(filters.endDate) }}
            </p>
            <p class="text-xs text-neutral-500 mt-1">Ref: STMT-{{ statementRef }}</p>
            <p class="text-xs text-neutral-400">Generated {{ formatDisplayDate(today) }}</p>
          </div>
        </div>

        <!-- Account Summary Strip -->
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 p-4 bg-neutral-50 rounded-xl border border-neutral-200">
          <div class="text-center">
            <p class="text-xs text-neutral-500 uppercase tracking-wide mb-1">Opening Balance</p>
            <p class="text-lg font-bold text-neutral-900 font-mono">R{{ fmt(summary.openingBalance) }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-neutral-500 uppercase tracking-wide mb-1">Total Income</p>
            <p class="text-lg font-bold text-emerald-600 font-mono">+R{{ fmt(summary.totalIncome) }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-neutral-500 uppercase tracking-wide mb-1">Total Expenses</p>
            <p class="text-lg font-bold text-red-500 font-mono">-R{{ fmt(summary.totalExpenses) }}</p>
          </div>
          <div class="text-center">
            <p class="text-xs text-neutral-500 uppercase tracking-wide mb-1">Net Change</p>
            <p
              class="text-lg font-bold font-mono"
              :class="netChange >= 0 ? 'text-emerald-600' : 'text-red-500'"
            >{{ netChange >= 0 ? '+' : '' }}R{{ fmt(netChange) }}</p>
          </div>
          <div class="text-center col-span-2 sm:col-span-1">
            <p class="text-xs text-neutral-500 uppercase tracking-wide mb-1">Closing Balance</p>
            <p class="text-lg font-bold text-primary font-mono">R{{ fmt(summary.closingBalance) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════════
         MAIN CONTENT
    ═══════════════════════════════════════════════════════════ -->
    <div class="max-w-7xl mx-auto px-4 lg:px-8 py-6 space-y-5">

      <!-- Filters & Export Panel -->
      <div class="bg-white rounded-xl shadow-sm border border-neutral-200 no-print">
        <!-- Panel Header -->
        <div
          class="flex items-center justify-between px-5 py-4 cursor-pointer"
          @click="filtersExpanded = !filtersExpanded"
        >
          <div class="flex items-center gap-2">
            <span class="text-base">🔍</span>
            <h3 class="font-semibold text-neutral-900">Filters & Search</h3>
            <span
              v-if="activeFilterCount > 0"
              class="px-2 py-0.5 text-xs bg-primary text-white rounded-full"
            >{{ activeFilterCount }}</span>
          </div>
          <div class="flex items-center gap-3">
            <button
              v-if="activeFilterCount > 0"
              @click.stop="resetFilters"
              class="text-xs text-neutral-500 hover:text-red-500 transition-colors"
            >Reset filters</button>
            <span class="text-neutral-400 text-sm">{{ filtersExpanded ? '▲' : '▼' }}</span>
          </div>
        </div>

        <!-- Filter Fields -->
        <div v-show="filtersExpanded" class="px-5 pb-5 border-t border-neutral-100">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mt-4">
            <!-- Start Date -->
            <div>
              <label class="block text-xs font-medium text-neutral-600 mb-1">Start Date</label>
              <input
                v-model="filters.startDate"
                type="date"
                class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary outline-none"
              />
            </div>
            <!-- End Date -->
            <div>
              <label class="block text-xs font-medium text-neutral-600 mb-1">End Date</label>
              <input
                v-model="filters.endDate"
                type="date"
                class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary outline-none"
              />
            </div>
            <!-- Category -->
            <div>
              <label class="block text-xs font-medium text-neutral-600 mb-1">Category</label>
              <select v-model="filters.category" class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary outline-none bg-white">
                <option value="">All Categories</option>
                <option value="GROCERIES">Groceries</option>
                <option value="AIRTIME">Airtime</option>
                <option value="BEVERAGES">Beverages</option>
                <option value="TOILETRIES">Toiletries</option>
                <option value="STOCK_PURCHASE">Stock Purchase</option>
                <option value="UTILITIES">Utilities</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
            <!-- Payment Method -->
            <div>
              <label class="block text-xs font-medium text-neutral-600 mb-1">Payment Method</label>
              <select v-model="filters.paymentMethod" class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary outline-none bg-white">
                <option value="">All Methods</option>
                <option value="CASH">Cash</option>
                <option value="DIGITAL">Digital</option>
                <option value="CREDIT">Credit (Book)</option>
              </select>
            </div>
            <!-- Type -->
            <div>
              <label class="block text-xs font-medium text-neutral-600 mb-1">Transaction Type</label>
              <select v-model="filters.type" class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary outline-none bg-white">
                <option value="">All Types</option>
                <option value="CASH_IN">Cash In</option>
                <option value="CASH_OUT">Cash Out</option>
                <option value="DIGITAL_IN">Digital In</option>
                <option value="CREDIT_GIVEN">Credit Given</option>
                <option value="CREDIT_COLLECTED">Credit Collected</option>
              </select>
            </div>
          </div>

          <!-- Second row: search + sort + apply -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
            <!-- Search -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium text-neutral-600 mb-1">Search Description</label>
              <input
                v-model="filters.search"
                type="text"
                placeholder="e.g. bread, Shoprite..."
                class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary outline-none"
              />
            </div>
            <!-- Sort -->
            <div>
              <label class="block text-xs font-medium text-neutral-600 mb-1">Sort By</label>
              <select v-model="filters.sort" class="w-full px-3 py-2 border border-neutral-300 rounded-lg text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary outline-none bg-white">
                <option value="date_desc">Date (Newest first)</option>
                <option value="date_asc">Date (Oldest first)</option>
                <option value="amount_desc">Amount (Highest first)</option>
                <option value="amount_asc">Amount (Lowest first)</option>
              </select>
            </div>
            <!-- Apply / Reset -->
            <div class="flex items-end gap-2">
              <button
                @click="applyFilters"
                class="flex-1 px-4 py-2 bg-primary hover:bg-primary-dark text-white rounded-lg text-sm font-medium transition-colors"
              >Apply</button>
              <button
                @click="resetFilters"
                class="px-4 py-2 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-lg text-sm transition-colors"
              >Reset</button>
            </div>
          </div>

          <!-- Quick date presets -->
          <div class="flex flex-wrap gap-2 mt-3">
            <span class="text-xs text-neutral-500 self-center">Quick:</span>
            <button
              v-for="preset in datePresets"
              :key="preset.label"
              @click="applyPreset(preset)"
              class="px-3 py-1 text-xs bg-neutral-100 hover:bg-primary hover:text-white text-neutral-700 rounded-full transition-colors"
            >{{ preset.label }}</button>
          </div>
        </div>

        <!-- Export Row -->
        <div class="flex flex-wrap items-center gap-2 px-5 py-3 border-t border-neutral-100">
          <span class="text-xs text-neutral-500 mr-1">Export:</span>
          <button
            @click="exportToCSV"
            class="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-700 hover:bg-neutral-900 text-white rounded-lg text-xs font-medium transition-colors"
          >📋 CSV</button>
          <button
            @click="exportToExcel"
            class="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-medium transition-colors"
          >📊 Excel</button>
          <button
            @click="printStatement"
            class="flex items-center gap-1.5 px-3 py-1.5 bg-primary hover:bg-primary-dark text-white rounded-lg text-xs font-medium transition-colors"
          >🖨️ Print / PDF</button>
          <div class="ml-auto flex items-center gap-2">
            <span class="text-xs text-neutral-500">Per page:</span>
            <select
              v-model="perPage"
              @change="currentPage = 1; fetchLedger()"
              class="px-2 py-1.5 border border-neutral-300 rounded text-xs focus:outline-none"
            >
              <option :value="10">10</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
          </div>
        </div>
      </div>

      <!-- ─────────────────────────────────────────────────────────
           DESKTOP TABLE
      ───────────────────────────────────────────────────────── -->
      <div class="bg-white rounded-xl shadow-sm border border-neutral-200 overflow-hidden hidden md:block">
        <!-- Loading overlay -->
        <div v-if="loading" class="p-16 text-center">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-3"></div>
          <p class="text-neutral-500 text-sm">Loading transactions...</p>
        </div>

        <!-- Empty state -->
        <div v-else-if="transactions.length === 0" class="p-16 text-center">
          <span class="text-6xl block mb-4">📭</span>
          <h3 class="text-lg font-semibold text-neutral-700 mb-2">No transactions found</h3>
          <p class="text-neutral-500 text-sm max-w-xs mx-auto">
            Try adjusting your date range or filters, or add your first transaction.
          </p>
          <button
            @click="resetFilters"
            class="mt-4 px-4 py-2 bg-primary text-white rounded-lg text-sm hover:bg-primary-dark transition-colors"
          >Clear Filters</button>
        </div>

        <!-- Table -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-neutral-100 border-b-2 border-neutral-200">
                <th
                  v-for="col in columns"
                  :key="col.key"
                  class="px-4 py-3 text-xs font-semibold text-neutral-600 uppercase tracking-wide cursor-pointer select-none whitespace-nowrap"
                  :class="col.align === 'right' ? 'text-right' : 'text-left'"
                  @click="col.sortable && toggleSort(col.sortKey)"
                >
                  {{ col.label }}
                  <span v-if="col.sortable" class="ml-1 text-neutral-400">
                    {{ filters.sort === col.sortKey + '_asc' ? '↑' : filters.sort === col.sortKey + '_desc' ? '↓' : '⇅' }}
                  </span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-neutral-100">
              <template v-for="(tx, index) in transactions" :key="tx.id">
                <!-- Main row -->
                <tr
                  @click="toggleExpand(tx.id)"
                  class="cursor-pointer transition-colors hover:bg-blue-50"
                  :class="[
                    index % 2 === 0 ? 'bg-white' : 'bg-neutral-50/60',
                    expandedRows.includes(tx.id) ? 'bg-blue-50' : ''
                  ]"
                >
                  <!-- Date -->
                  <td class="px-4 py-3 whitespace-nowrap font-medium text-neutral-900">
                    {{ formatDisplayDate(tx.date) }}
                  </td>
                  <!-- Time -->
                  <td class="px-4 py-3 whitespace-nowrap text-neutral-500">
                    {{ tx.time || '—' }}
                  </td>
                  <!-- Description -->
                  <td class="px-4 py-3 max-w-xs">
                    <div class="flex items-center gap-2">
                      <span class="text-base leading-none">{{ paymentIcon(tx.paymentMethod) }}</span>
                      <div class="min-w-0">
                        <p class="truncate text-neutral-900">{{ tx.description || '—' }}</p>
                        <p v-if="tx.entryMethod === 'OCR'" class="text-xs text-blue-600">📷 Scanned</p>
                      </div>
                      <span
                        v-if="tx.verified"
                        class="flex-shrink-0 w-4 h-4 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs font-bold"
                        title="Verified"
                      >✓</span>
                      <span v-if="tx.receiptImage" class="flex-shrink-0 text-neutral-400 text-xs" title="Receipt attached">📎</span>
                    </div>
                  </td>
                  <!-- Category -->
                  <td class="px-4 py-3 whitespace-nowrap">
                    <span class="px-2 py-0.5 bg-neutral-100 text-neutral-700 rounded text-xs font-medium">
                      {{ formatCategory(tx.category) }}
                    </span>
                  </td>
                  <!-- Reference -->
                  <td class="px-4 py-3 whitespace-nowrap text-neutral-500 font-mono text-xs">
                    {{ tx.reference }}
                  </td>
                  <!-- Debit -->
                  <td class="px-4 py-3 text-right whitespace-nowrap font-mono font-semibold text-red-500">
                    {{ tx.debit > 0 ? `R${fmt(tx.debit)}` : '—' }}
                  </td>
                  <!-- Credit -->
                  <td class="px-4 py-3 text-right whitespace-nowrap font-mono font-semibold text-emerald-600">
                    {{ tx.credit > 0 ? `R${fmt(tx.credit)}` : '—' }}
                  </td>
                  <!-- Balance -->
                  <td class="px-4 py-3 text-right whitespace-nowrap font-mono font-bold text-primary">
                    {{ tx.balance !== null ? `R${fmt(tx.balance)}` : '—' }}
                  </td>
                </tr>

                <!-- Expanded detail row -->
                <tr v-if="expandedRows.includes(tx.id)">
                  <td colspan="8" class="bg-blue-50 px-6 py-4 border-b border-blue-100">
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                      <div>
                        <p class="text-xs text-neutral-500 mb-0.5">Transaction Type</p>
                        <p class="font-medium">{{ formatTxType(tx.type) }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-neutral-500 mb-0.5">Payment Method</p>
                        <p class="font-medium">{{ paymentIcon(tx.paymentMethod) }} {{ formatMethod(tx.paymentMethod) }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-neutral-500 mb-0.5">Entry Method</p>
                        <p class="font-medium capitalize">{{ tx.entryMethod?.toLowerCase() || 'Manual' }}</p>
                      </div>
                      <div>
                        <p class="text-xs text-neutral-500 mb-0.5">Recorded At</p>
                        <p class="font-medium text-xs">{{ tx.recordedAt || '—' }}</p>
                      </div>
                    </div>
                    <div v-if="tx.receiptImage" class="mt-3">
                      <p class="text-xs text-neutral-500 mb-1">Receipt</p>
                      <img
                        :src="`/uploads/receipts/${tx.receiptImage}`"
                        alt="Receipt"
                        class="h-24 w-auto rounded border border-neutral-200 cursor-pointer hover:opacity-80 transition-opacity"
                        @click.stop="openReceipt(tx.receiptImage)"
                      />
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>

            <!-- Table footer totals -->
            <tfoot>
              <tr class="bg-neutral-100 border-t-2 border-neutral-300 font-semibold">
                <td colspan="5" class="px-4 py-3 text-sm text-neutral-700">
                  Page totals ({{ transactions.length }} rows)
                </td>
                <td class="px-4 py-3 text-right font-mono text-red-500">
                  R{{ fmt(pageTotalDebit) }}
                </td>
                <td class="px-4 py-3 text-right font-mono text-emerald-600">
                  R{{ fmt(pageTotalCredit) }}
                </td>
                <td class="px-4 py-3 text-right font-mono text-primary">
                  R{{ fmt(summary.closingBalance) }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      <!-- ─────────────────────────────────────────────────────────
           MOBILE CARD LIST
      ───────────────────────────────────────────────────────── -->
      <div class="block md:hidden space-y-3">
        <div v-if="loading" class="p-8 text-center bg-white rounded-xl">
          <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-3"></div>
          <p class="text-neutral-500 text-sm">Loading...</p>
        </div>

        <div
          v-for="tx in transactions"
          :key="tx.id"
          class="bg-white rounded-xl shadow-sm border border-neutral-200 p-4 cursor-pointer"
          @click="toggleExpand(tx.id)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-lg">{{ paymentIcon(tx.paymentMethod) }}</span>
                <p class="font-semibold text-neutral-900 truncate">{{ tx.description || '—' }}</p>
                <span v-if="tx.verified" class="text-emerald-500 text-xs">✓</span>
              </div>
              <div class="flex flex-wrap gap-2 text-xs text-neutral-500">
                <span>{{ formatDisplayDate(tx.date) }}</span>
                <span>•</span>
                <span class="px-1.5 py-0.5 bg-neutral-100 rounded">{{ formatCategory(tx.category) }}</span>
                <span class="font-mono text-neutral-400">{{ tx.reference }}</span>
              </div>
            </div>
            <div class="text-right ml-3 flex-shrink-0">
              <p
                class="text-base font-bold font-mono"
                :class="tx.credit > 0 ? 'text-emerald-600' : 'text-red-500'"
              >
                {{ tx.credit > 0 ? '+' : '-' }}R{{ fmt(tx.credit > 0 ? tx.credit : tx.debit) }}
              </p>
              <p v-if="tx.balance !== null" class="text-xs text-primary font-mono mt-0.5">
                Bal: R{{ fmt(tx.balance) }}
              </p>
            </div>
          </div>

          <!-- Expanded mobile details -->
          <div v-if="expandedRows.includes(tx.id)" class="mt-3 pt-3 border-t border-neutral-100 grid grid-cols-2 gap-2 text-xs text-neutral-600">
            <div><span class="text-neutral-400">Type:</span> {{ formatTxType(tx.type) }}</div>
            <div><span class="text-neutral-400">Method:</span> {{ formatMethod(tx.paymentMethod) }}</div>
            <div><span class="text-neutral-400">Entry:</span> {{ tx.entryMethod || 'MANUAL' }}</div>
            <div class="col-span-2 truncate"><span class="text-neutral-400">Recorded:</span> {{ tx.recordedAt }}</div>
          </div>
        </div>

        <div v-if="!loading && transactions.length === 0" class="bg-white rounded-xl p-10 text-center">
          <span class="text-5xl block mb-3">📭</span>
          <p class="text-neutral-600 font-medium">No transactions found</p>
          <button @click="resetFilters" class="mt-3 text-sm text-primary underline">Clear filters</button>
        </div>
      </div>

      <!-- ─────────────────────────────────────────────────────────
           PAGINATION
      ───────────────────────────────────────────────────────── -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white rounded-xl border border-neutral-200 px-5 py-3 no-print">
        <p class="text-sm text-neutral-600">
          Showing
          <span class="font-semibold">{{ paginationStart }}</span>–<span class="font-semibold">{{ paginationEnd }}</span>
          of <span class="font-semibold">{{ pagination.total }}</span> transactions
        </p>
        <div class="flex items-center gap-2">
          <button
            @click="goToPage(1)"
            :disabled="currentPage <= 1"
            class="px-2 py-1 rounded text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:bg-neutral-100 transition-colors"
          >«</button>
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="px-3 py-1.5 rounded text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:bg-neutral-100 transition-colors"
          >Previous</button>

          <div class="flex gap-1">
            <button
              v-for="p in pageNumbers"
              :key="p"
              @click="goToPage(p)"
              class="w-8 h-8 rounded text-sm transition-colors"
              :class="p === currentPage ? 'bg-primary text-white' : 'hover:bg-neutral-100 text-neutral-700'"
            >{{ p }}</button>
          </div>

          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage >= pagination.totalPages"
            class="px-3 py-1.5 rounded text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:bg-neutral-100 transition-colors"
          >Next</button>
          <button
            @click="goToPage(pagination.totalPages)"
            :disabled="currentPage >= pagination.totalPages"
            class="px-2 py-1 rounded text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:bg-neutral-100 transition-colors"
          >»</button>
        </div>
      </div>

    </div><!-- /max-w-7xl -->

    <!-- ═══════════════════════════════════════════════════════════
         PRINT FOOTER (only in print)
    ═══════════════════════════════════════════════════════════ -->
    <div class="print-only-footer hidden">
      <div class="text-center text-xs text-neutral-500 mt-8 pt-4 border-t border-neutral-300">
        <p>MzansiPulse — Empowering South African Township Entrepreneurs</p>
        <p>This statement was generated on {{ formatDisplayDate(today) }} and is for record-keeping purposes only.</p>
        <p>Ref: STMT-{{ statementRef }}</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLedgerExport } from '../composables/useLedgerExport'

const authStore = useAuthStore()
const { exportToCSV: doCSV, exportToExcel: doExcel, printStatement: doPrint } = useLedgerExport()

// ── State ─────────────────────────────────────────────────────────────────
const loading      = ref(false)
const transactions = ref([])
const expandedRows = ref([])

const summary = ref({
  openingBalance:   0,
  totalIncome:      0,
  totalExpenses:    0,
  closingBalance:   0,
  transactionCount: 0,
})
const pagination = ref({ page: 1, perPage: 50, total: 0, totalPages: 1 })
const currentPage   = ref(1)
const perPage       = ref(50)
const filtersExpanded = ref(true)

const today = new Date().toISOString().slice(0, 10)
const thirtyDaysAgo = (() => {
  const d = new Date()
  d.setDate(d.getDate() - 30)
  return d.toISOString().slice(0, 10)
})()

const filters = ref({
  startDate:     thirtyDaysAgo,
  endDate:       today,
  category:      '',
  paymentMethod: '',
  type:          '',
  search:        '',
  sort:          'date_desc',
})

// ── Computed ──────────────────────────────────────────────────────────────
const businessName  = computed(() => authStore.user?.businessName || 'My Business')
const userLocation  = computed(() => authStore.user?.location     || 'South Africa')
const statementRef  = computed(() => {
  const id = authStore.user?.id || 0
  const ts = Date.now().toString(36).toUpperCase()
  return `${id}-${ts}`
})

const netChange = computed(() => summary.value.totalIncome - summary.value.totalExpenses)

const pageTotalDebit  = computed(() => transactions.value.reduce((s, t) => s + (t.debit  || 0), 0))
const pageTotalCredit = computed(() => transactions.value.reduce((s, t) => s + (t.credit || 0), 0))

const paginationStart = computed(() => pagination.value.total === 0 ? 0 : (currentPage.value - 1) * perPage.value + 1)
const paginationEnd   = computed(() => Math.min(currentPage.value * perPage.value, pagination.value.total))

const pageNumbers = computed(() => {
  const total = pagination.value.totalPages
  const cur   = currentPage.value
  const delta = 2
  const pages = []
  for (let i = Math.max(1, cur - delta); i <= Math.min(total, cur + delta); i++) {
    pages.push(i)
  }
  return pages
})

const activeFilterCount = computed(() => {
  let n = 0
  if (filters.value.category)      n++
  if (filters.value.paymentMethod)  n++
  if (filters.value.type)           n++
  if (filters.value.search)         n++
  return n
})

const columns = [
  { key: 'date',        label: 'Date',        align: 'left',  sortable: true,  sortKey: 'date' },
  { key: 'time',        label: 'Time',        align: 'left',  sortable: false },
  { key: 'description', label: 'Description', align: 'left',  sortable: false },
  { key: 'category',    label: 'Category',    align: 'left',  sortable: false },
  { key: 'reference',   label: 'Reference',   align: 'left',  sortable: false },
  { key: 'debit',       label: 'Debit (R)',   align: 'right', sortable: true,  sortKey: 'amount' },
  { key: 'credit',      label: 'Credit (R)',  align: 'right', sortable: true,  sortKey: 'amount' },
  { key: 'balance',     label: 'Balance (R)', align: 'right', sortable: false },
]

const datePresets = [
  {
    label: 'This month',
    fn: () => {
      const n = new Date()
      const s = new Date(n.getFullYear(), n.getMonth(), 1).toISOString().slice(0, 10)
      return { startDate: s, endDate: today }
    }
  },
  {
    label: 'Last 30 days',
    fn: () => ({ startDate: thirtyDaysAgo, endDate: today })
  },
  {
    label: 'Last 90 days',
    fn: () => {
      const d = new Date(); d.setDate(d.getDate() - 90)
      return { startDate: d.toISOString().slice(0, 10), endDate: today }
    }
  },
  {
    label: 'This year',
    fn: () => {
      const y = new Date().getFullYear()
      return { startDate: `${y}-01-01`, endDate: today }
    }
  },
]

// ── Methods ───────────────────────────────────────────────────────────────
const fmt = (n) => (typeof n === 'number' ? n.toFixed(2) : '0.00')

const formatDisplayDate = (dateStr) => {
  if (!dateStr) return '—'
  try {
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-ZA', {
      day: '2-digit', month: 'short', year: 'numeric'
    })
  } catch { return dateStr }
}

const formatCategory = (cat) => {
  if (!cat) return 'Other'
  return cat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const formatTxType = (type) => {
  const m = {
    CASH_IN: 'Cash In', CASH_OUT: 'Cash Out',
    DIGITAL_IN: 'Digital In', CREDIT_GIVEN: 'Credit Given',
    CREDIT_COLLECTED: 'Credit Collected',
  }
  return m[type] || type
}

const formatMethod = (m) => {
  const map = { CASH: 'Cash', DIGITAL: 'Digital', CREDIT: 'Credit (Book)' }
  return map[m] || m || 'Cash'
}

const paymentIcon = (m) => {
  const map = { CASH: '💵', DIGITAL: '💳', CREDIT: '📝' }
  return map[m] || '💵'
}

const toggleExpand = (id) => {
  const idx = expandedRows.value.indexOf(id)
  if (idx >= 0) expandedRows.value.splice(idx, 1)
  else expandedRows.value.push(id)
}

const openReceipt = (path) => window.open(`/uploads/receipts/${path}`, '_blank')

const toggleSort = (key) => {
  const cur = filters.value.sort
  if (cur === `${key}_desc`) filters.value.sort = `${key}_asc`
  else filters.value.sort = `${key}_desc`
  currentPage.value = 1
  fetchLedger()
}

const applyFilters = () => {
  currentPage.value = 1
  fetchLedger()
}

const resetFilters = () => {
  filters.value = {
    startDate:     thirtyDaysAgo,
    endDate:       today,
    category:      '',
    paymentMethod: '',
    type:          '',
    search:        '',
    sort:          'date_desc',
  }
  currentPage.value = 1
  fetchLedger()
}

const applyPreset = (preset) => {
  const vals = preset.fn()
  filters.value.startDate = vals.startDate
  filters.value.endDate   = vals.endDate
  currentPage.value = 1
  fetchLedger()
}

const goToPage = (p) => {
  if (p < 1 || p > pagination.value.totalPages) return
  currentPage.value = p
  fetchLedger()
}

const fetchLedger = async () => {
  if (!authStore.user?.id) return
  loading.value     = true
  expandedRows.value = []

  try {
    const params = new URLSearchParams({
      start_date:     filters.value.startDate,
      end_date:       filters.value.endDate,
      sort:           filters.value.sort,
      page:           currentPage.value,
      per_page:       perPage.value,
    })
    if (filters.value.category)      params.set('category',       filters.value.category)
    if (filters.value.paymentMethod) params.set('payment_method', filters.value.paymentMethod)
    if (filters.value.type)          params.set('type',           filters.value.type)
    if (filters.value.search)        params.set('search',         filters.value.search)

    const res  = await fetch(`http://localhost:5000/api/ledger/${authStore.user.id}?${params}`)
    const data = await res.json()

    if (data.success) {
      transactions.value = data.transactions
      summary.value      = data.summary
      pagination.value   = data.pagination
    } else {
      console.error('Ledger fetch failed:', data.error)
    }
  } catch (err) {
    console.error('Ledger fetch error:', err)
  } finally {
    loading.value = false
  }
}

// ── Export wrappers ───────────────────────────────────────────────────────
const exportToCSV = () => doCSV(transactions.value, summary.value, filters.value, businessName.value)
const exportToExcel = () => doExcel(transactions.value, summary.value, filters.value, businessName.value)
const printStatement = () => doPrint()

// ── Init ──────────────────────────────────────────────────────────────────
onMounted(() => fetchLedger())
</script>

<style scoped>
.font-mono { font-family: 'Courier New', Courier, monospace; }

/* ── Print styles ─────────────────────────────────────────────────────── */
@media print {
  .no-print { display: none !important; }
  .print-only-footer { display: block !important; }

  .ledger-container {
    background: white !important;
  }

  .ledger-header {
    border-bottom: 2px solid #000 !important;
    margin-bottom: 16px;
  }

  /* Full width on print */
  .max-w-7xl {
    max-width: 100% !important;
    padding: 0 8px !important;
  }

  /* Force desktop table to show on print */
  .hidden.md\:block { display: block !important; }
  .block.md\:hidden  { display: none  !important; }

  table {
    width: 100%;
    font-size: 11px;
    page-break-inside: auto;
    border-collapse: collapse;
  }

  thead { display: table-header-group; }
  tfoot { display: table-footer-group; }

  tr { page-break-inside: avoid; page-break-after: auto; }

  th, td {
    padding: 6px 8px !important;
    border: 1px solid #ddd;
  }

  thead tr { background: #f3f4f6 !important; }

  /* Color-safe print */
  .text-emerald-600 { color: #059669 !important; }
  .text-red-500     { color: #ef4444 !important; }
}
</style>
