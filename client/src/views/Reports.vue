<template>
  <div class="reports">
    <div class="page-header">
      <h2>{{ t('reports.title') }}</h2>
      <p>{{ t('reports.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('reports.loading') }}</div>
    <div v-else-if="error" class="error">{{ t('reports.loadFailed', { message: error }) }}</div>
    <div v-else>
      <!-- Quarterly Performance -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.quarterly.title') }}</h3>
        </div>
        <div v-if="quarterRows.length === 0" class="empty">{{ t('common.noData') }}</div>
        <div v-else class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t('reports.quarterly.quarter') }}</th>
                <th>{{ t('reports.quarterly.totalOrders') }}</th>
                <th>{{ t('reports.quarterly.totalRevenue') }}</th>
                <th>{{ t('reports.quarterly.avgOrderValue') }}</th>
                <th>{{ t('reports.quarterly.fulfillmentRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in quarterRows" :key="row.quarter">
                <td><strong>{{ row.label }}</strong></td>
                <td>{{ row.totalOrders }}</td>
                <td>{{ row.revenue }}</td>
                <td>{{ row.avgOrderValue }}</td>
                <td>
                  <span :class="row.fulfillmentClass">
                    {{ row.fulfillmentRate }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Monthly Trends Chart -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.monthlyTrend.title') }}</h3>
        </div>
        <div v-if="chartBars.length === 0" class="empty">{{ t('common.noData') }}</div>
        <div v-else class="chart-container">
          <div class="bar-chart" role="img" :aria-label="t('reports.monthlyTrend.title')">
            <div v-for="bar in chartBars" :key="bar.month" class="bar-wrapper">
              <div class="bar-container">
                <div
                  class="bar"
                  :style="{ height: bar.height + 'px' }"
                  :title="bar.revenue"
                ></div>
              </div>
              <div class="bar-label">{{ bar.label }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Month-over-Month Comparison -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('reports.monthOverMonth.title') }}</h3>
        </div>
        <div v-if="monthRows.length === 0" class="empty">{{ t('common.noData') }}</div>
        <div v-else class="table-container">
          <table class="reports-table">
            <thead>
              <tr>
                <th>{{ t('reports.monthOverMonth.month') }}</th>
                <th>{{ t('reports.monthOverMonth.orders') }}</th>
                <th>{{ t('reports.monthOverMonth.revenue') }}</th>
                <th>{{ t('reports.monthOverMonth.change') }}</th>
                <th>{{ t('reports.monthOverMonth.growthRate') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in monthRows" :key="row.month">
                <td><strong>{{ row.label }}</strong></td>
                <td>{{ row.orders }}</td>
                <td>{{ row.revenue }}</td>
                <td>
                  <span :class="row.changeClass">{{ row.change }}</span>
                </td>
                <td>
                  <span :class="row.growthClass">{{ row.growth }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.totalRevenueYtd') }}</div>
          <div class="stat-value">{{ formatMoney(totalRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.avgMonthlyRevenue') }}</div>
          <div class="stat-value">{{ formatMoney(avgMonthlyRevenue) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.totalOrdersYtd') }}</div>
          <div class="stat-value">{{ totalOrders }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('reports.stats.bestQuarter') }}</div>
          <div class="stat-value">{{ bestQuarterLabel }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

// Same order as the months.* locale keys, so "2025-03" -> index 2 -> months.mar
const MONTH_KEYS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

// Tallest chart bar in px; must match the .bar-container height in the styles below
const MAX_BAR_HEIGHT = 200

// Placeholder shown instead of NaN / Infinity / missing values
const EMPTY_VALUE = '-'

export default {
  name: 'Reports',
  setup() {
    const { t, currentCurrency } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const quarterlyData = ref([])
    const monthlyData = ref([])

    // Missing or non-numeric values count as 0 so one bad row cannot turn a total into NaN
    const toNumber = (value) => (Number.isFinite(value) ? value : 0)

    // Whole-number counts (orders): raw value, or "-" when it is missing
    const formatCount = (value) => (Number.isFinite(value) ? value : EMPTY_VALUE)

    // All amounts from the API are USD; formatCurrencyWithDecimals converts to JPY in Japanese mode.
    // Two decimals keeps English output identical to the old hand-rolled "1,234.50" format.
    // These are all revenue aggregates, so yen is shown whole: with 2 decimals the converted
    // cents would surface as "¥389,585,663.63".
    const formatMoney = (amount) => {
      if (!Number.isFinite(amount)) return EMPTY_VALUE
      return formatCurrencyWithDecimals(amount, currentCurrency.value, currentCurrency.value === 'JPY' ? 0 : 2)
    }

    // API sends quarters as "Q1-2025"; rebuild the label through the locale template.
    // Anything that does not match is shown as-is rather than guessed at.
    const formatQuarter = (quarter) => {
      const match = /^Q([1-4])-(\d{4})$/.exec(quarter || '')
      if (!match) return quarter || EMPTY_VALUE
      return t('reports.quarterLabel', { quarter: match[1], year: match[2] })
    }

    // API sends months as "YYYY-MM". Parsed from the string (no Date) so time zones cannot shift
    // the month; an unparseable value yields "-" instead of "undefined NaN".
    const formatMonth = (monthStr) => {
      const match = /^(\d{4})-(\d{2})$/.exec(monthStr || '')
      if (!match) return EMPTY_VALUE
      const monthKey = MONTH_KEYS[parseInt(match[2], 10) - 1]
      if (!monthKey) return EMPTY_VALUE
      return t('reports.monthLabel', { month: t(`months.${monthKey}`), year: match[1] })
    }

    // Fulfillment badge colour: 90%+ green, 75%+ amber, below that red
    const getFulfillmentClass = (rate) => {
      if (!Number.isFinite(rate)) return ''
      if (rate >= 90) return 'badge success'
      if (rate >= 75) return 'badge warning'
      return 'badge danger'
    }

    const getChangeClass = (change) => {
      if (change > 0) return 'positive-change'
      if (change < 0) return 'negative-change'
      return ''
    }

    // Summary stats
    const totalRevenue = computed(() => {
      return monthlyData.value.reduce((sum, m) => sum + toNumber(m.revenue), 0)
    })

    const avgMonthlyRevenue = computed(() => {
      // No months yet: avoid 0 / 0
      if (monthlyData.value.length === 0) return 0
      return totalRevenue.value / monthlyData.value.length
    })

    const totalOrders = computed(() => {
      return monthlyData.value.reduce((sum, m) => sum + toNumber(m.order_count), 0)
    })

    // Highest-revenue quarter. Strict ">" means the earliest quarter wins a tie, and no quarter
    // is picked when every quarter has zero revenue.
    const bestQuarter = computed(() => {
      let best = ''
      let bestRevenue = 0
      for (const q of quarterlyData.value) {
        if (q.total_revenue > bestRevenue) {
          bestRevenue = q.total_revenue
          best = q.quarter
        }
      }
      return best
    })

    const bestQuarterLabel = computed(() => formatQuarter(bestQuarter.value))

    // Quarterly table rows, pre-formatted so the template only prints strings
    const quarterRows = computed(() => {
      return quarterlyData.value.map(q => ({
        quarter: q.quarter,
        label: formatQuarter(q.quarter),
        totalOrders: formatCount(q.total_orders),
        revenue: formatMoney(q.total_revenue),
        avgOrderValue: formatMoney(q.avg_order_value),
        fulfillmentRate: Number.isFinite(q.fulfillment_rate) ? `${q.fulfillment_rate}%` : EMPTY_VALUE,
        fulfillmentClass: getFulfillmentClass(q.fulfillment_rate)
      }))
    })

    // Bars are scaled against the best month, so the tallest bar is always MAX_BAR_HEIGHT
    const chartBars = computed(() => {
      const maxRevenue = monthlyData.value.reduce((max, m) => Math.max(max, toNumber(m.revenue)), 0)
      return monthlyData.value.map(m => ({
        month: m.month,
        label: formatMonth(m.month),
        // maxRevenue is 0 when no month has revenue: avoid dividing by it
        height: maxRevenue > 0 ? (toNumber(m.revenue) / maxRevenue) * MAX_BAR_HEIGHT : 0,
        revenue: formatMoney(m.revenue)
      }))
    })

    // Month-over-month rows: each month is compared with the row before it (data is sorted by month)
    const monthRows = computed(() => {
      return monthlyData.value.map((m, index) => {
        const row = {
          month: m.month,
          label: formatMonth(m.month),
          orders: formatCount(m.order_count),
          revenue: formatMoney(m.revenue),
          change: EMPTY_VALUE,
          changeClass: '',
          growth: EMPTY_VALUE,
          growthClass: ''
        }

        // The first month has nothing to compare with
        if (index === 0) return row
        const previous = monthlyData.value[index - 1].revenue

        const change = m.revenue - previous
        if (Number.isFinite(change)) {
          row.changeClass = getChangeClass(change)
          if (change > 0) row.change = `+${formatMoney(change)}`
          else if (change < 0) row.change = `-${formatMoney(Math.abs(change))}`
          else row.change = formatMoney(0)
        }

        // Growth is relative to the previous month, so a zero (or missing) previous month has no
        // defined rate: show "-" rather than Infinity / NaN
        if (Number.isFinite(change) && Number.isFinite(previous) && previous !== 0) {
          const rate = (change / previous) * 100
          row.growth = `${rate > 0 ? '+' : ''}${rate.toFixed(1)}%`
          row.growthClass = getChangeClass(change)
        }

        return row
      })
    })

    const loadData = async () => {
      try {
        loading.value = true
        error.value = null

        // The two reports are independent, so fetch them in parallel
        const [quarterly, monthly] = await Promise.all([
          api.getQuarterlyReports(),
          api.getMonthlyTrends()
        ])
        quarterlyData.value = Array.isArray(quarterly) ? quarterly : []
        monthlyData.value = Array.isArray(monthly) ? monthly : []
      } catch (err) {
        // Only the raw detail is stored; the "Failed to load" wording is translated in the template
        error.value = err.message || t('common.error')
        console.error('Failed to load reports:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(loadData)

    return {
      t,
      loading,
      error,
      formatMoney,
      totalRevenue,
      avgMonthlyRevenue,
      totalOrders,
      bestQuarterLabel,
      quarterRows,
      chartBars,
      monthRows
    }
  }
}
</script>

<style scoped>
.reports {
  padding: 0;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  margin-bottom: 1.5rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
}

.reports-table {
  width: 100%;
  border-collapse: collapse;
}

.reports-table th {
  background: #f8fafc;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #64748b;
  border-bottom: 2px solid #e2e8f0;
}

.reports-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #e2e8f0;
}

.reports-table tr:hover {
  background: #f8fafc;
}

.chart-container {
  padding: 2rem 1rem;
  min-height: 300px;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 250px;
  gap: 0.5rem;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.bar-container {
  height: 200px;
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.bar {
  width: 100%;
  background: linear-gradient(to top, #3b82f6, #60a5fa);
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
  cursor: pointer;
}

.bar:hover {
  background: linear-gradient(to top, #2563eb, #3b82f6);
}

.bar-label {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
  text-align: center;
  transform: rotate(-45deg);
  white-space: nowrap;
  margin-top: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3b82f6;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: #0f172a;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.badge.success {
  background: #dcfce7;
  color: #166534;
}

.badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.positive-change {
  color: #16a34a;
  font-weight: 600;
}

.negative-change {
  color: #dc2626;
  font-weight: 600;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

.error {
  background: #fee2e2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 8px;
  margin: 1rem 0;
}

/* Shown in place of a table or chart when the API returns no rows */
.empty {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}
</style>
