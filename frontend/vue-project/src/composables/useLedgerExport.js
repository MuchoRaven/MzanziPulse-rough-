/**
 * useLedgerExport — pure-browser export functions (no external deps)
 * Supports: CSV, Excel (HTML table), Print/PDF
 */
export function useLedgerExport() {

  // ── Helpers ──────────────────────────────────────────────────────────────
  const fmt = (n) => (typeof n === 'number' ? n.toFixed(2) : '0.00')

  const formatCategory = (cat) =>
    cat ? cat.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) : 'Other'

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

  const triggerDownload = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // ── CSV Export ────────────────────────────────────────────────────────────
  const exportToCSV = (transactions, summary, filters, businessName) => {
    const escCSV = (v) => {
      const s = String(v ?? '')
      return s.includes(',') || s.includes('"') || s.includes('\n')
        ? `"${s.replace(/"/g, '""')}"`
        : s
    }

    const lines = []

    // Header block
    lines.push(`MzansiPulse Transaction Ledger`)
    lines.push(`Business:,${escCSV(businessName)}`)
    lines.push(`Period:,${filters.startDate} to ${filters.endDate}`)
    lines.push(`Generated:,${new Date().toLocaleDateString('en-ZA')}`)
    lines.push('')

    // Summary
    lines.push('ACCOUNT SUMMARY')
    lines.push(`Opening Balance,R${fmt(summary.openingBalance)}`)
    lines.push(`Total Income,R${fmt(summary.totalIncome)}`)
    lines.push(`Total Expenses,R${fmt(summary.totalExpenses)}`)
    lines.push(`Net Change,R${fmt(summary.totalIncome - summary.totalExpenses)}`)
    lines.push(`Closing Balance,R${fmt(summary.closingBalance)}`)
    lines.push(`Transactions,${summary.transactionCount}`)
    lines.push('')

    // Column headers
    lines.push([
      'Date', 'Time', 'Reference', 'Description', 'Category',
      'Type', 'Payment Method', 'Debit (R)', 'Credit (R)', 'Balance (R)', 'Verified'
    ].map(escCSV).join(','))

    // Data rows
    transactions.forEach(tx => {
      lines.push([
        tx.date,
        tx.time || '',
        tx.reference,
        tx.description,
        formatCategory(tx.category),
        formatTxType(tx.type),
        formatMethod(tx.paymentMethod),
        tx.debit  > 0 ? fmt(tx.debit)  : '',
        tx.credit > 0 ? fmt(tx.credit) : '',
        tx.balance !== null ? fmt(tx.balance) : '',
        tx.verified ? 'Yes' : 'No',
      ].map(escCSV).join(','))
    })

    const filename = `MzansiPulse_Ledger_${filters.startDate}_${filters.endDate}.csv`
    triggerDownload(lines.join('\r\n'), filename, 'text/csv;charset=utf-8;')
  }

  // ── Excel Export (HTML table → .xls, opens in Excel/LibreOffice) ─────────
  const exportToExcel = (transactions, summary, filters, businessName) => {
    const periodLabel = `${filters.startDate} to ${filters.endDate}`

    const html = `
<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
<head>
  <meta charset="UTF-8">
  <!--[if gte mso 9]>
  <xml><x:ExcelWorkbook><x:ExcelWorksheets>
    <x:ExcelWorksheet><x:Name>Summary</x:Name><x:WorksheetOptions><x:Selected/></x:WorksheetOptions></x:ExcelWorksheet>
    <x:ExcelWorksheet><x:Name>Transactions</x:Name></x:ExcelWorksheet>
  </x:ExcelWorksheets></x:ExcelWorkbook></xml>
  <![endif]-->
  <style>
    body  { font-family: Arial, sans-serif; font-size: 11pt; }
    table { border-collapse: collapse; width: 100%; }
    th    { background: #F3F4F6; font-weight: bold; padding: 6px 10px; border: 1px solid #D1D5DB; }
    td    { padding: 5px 10px; border: 1px solid #E5E7EB; }
    .title { font-size: 16pt; font-weight: bold; color: #0066CC; }
    .label { font-weight: bold; color: #374151; }
    .income  { color: #059669; font-weight: bold; }
    .expense { color: #EF4444; font-weight: bold; }
    .balance { color: #0066CC; font-weight: bold; }
    .section { background: #F9FAFB; font-weight: bold; color: #111827; }
  </style>
</head>
<body>
  <!-- Sheet 1: Summary -->
  <table>
    <tr><td colspan="2" class="title">Transaction Ledger</td></tr>
    <tr><td class="label">Business:</td><td>${businessName}</td></tr>
    <tr><td class="label">Period:</td><td>${periodLabel}</td></tr>
    <tr><td class="label">Generated:</td><td>${new Date().toLocaleDateString('en-ZA')}</td></tr>
    <tr><td>&nbsp;</td></tr>
    <tr><td colspan="2" class="section">Account Summary</td></tr>
    <tr><td class="label">Opening Balance</td><td>R${fmt(summary.openingBalance)}</td></tr>
    <tr><td class="label income">Total Income</td><td class="income">R${fmt(summary.totalIncome)}</td></tr>
    <tr><td class="label expense">Total Expenses</td><td class="expense">R${fmt(summary.totalExpenses)}</td></tr>
    <tr><td class="label">Net Change</td><td>R${fmt(summary.totalIncome - summary.totalExpenses)}</td></tr>
    <tr><td class="label balance">Closing Balance</td><td class="balance">R${fmt(summary.closingBalance)}</td></tr>
    <tr><td class="label">Transaction Count</td><td>${summary.transactionCount}</td></tr>
    <tr><td>&nbsp;</td></tr>
  </table>
  <br/><br/>
  <!-- Sheet 2: Transactions -->
  <table>
    <thead>
      <tr>
        <th>Date</th>
        <th>Time</th>
        <th>Reference</th>
        <th>Description</th>
        <th>Category</th>
        <th>Type</th>
        <th>Payment Method</th>
        <th>Debit (R)</th>
        <th>Credit (R)</th>
        <th>Balance (R)</th>
        <th>Verified</th>
      </tr>
    </thead>
    <tbody>
      ${transactions.map(tx => `
      <tr>
        <td>${tx.date || ''}</td>
        <td>${tx.time || ''}</td>
        <td>${tx.reference || ''}</td>
        <td>${(tx.description || '').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</td>
        <td>${formatCategory(tx.category)}</td>
        <td>${formatTxType(tx.type)}</td>
        <td>${formatMethod(tx.paymentMethod)}</td>
        <td class="expense">${tx.debit  > 0 ? fmt(tx.debit)  : ''}</td>
        <td class="income">${tx.credit > 0 ? fmt(tx.credit) : ''}</td>
        <td class="balance">${tx.balance !== null ? fmt(tx.balance) : ''}</td>
        <td>${tx.verified ? 'Yes' : 'No'}</td>
      </tr>`).join('')}
    </tbody>
    <tfoot>
      <tr>
        <th colspan="7">Page Totals</th>
        <th class="expense">R${fmt(transactions.reduce((s, t) => s + (t.debit  || 0), 0))}</th>
        <th class="income">R${fmt(transactions.reduce((s, t) => s + (t.credit || 0), 0))}</th>
        <th colspan="2"></th>
      </tr>
    </tfoot>
  </table>
</body>
</html>`

    const filename = `MzansiPulse_Ledger_${filters.startDate}_${filters.endDate}.xls`
    triggerDownload(html, filename, 'application/vnd.ms-excel;charset=utf-8;')
  }

  // ── Print / PDF ───────────────────────────────────────────────────────────
  const printStatement = () => {
    window.print()
  }

  return { exportToCSV, exportToExcel, printStatement }
}
