<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="recommendations">
      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.budget') }}</div>
          <div class="stat-value">{{ formatCurrency(recommendations.budget, currentCurrency) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.allocated') }}</div>
          <div class="stat-value">{{ formatCurrencyWithDecimals(recommendations.allocated, currentCurrency, 2) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.remaining') }}</div>
          <div class="stat-value">{{ formatCurrencyWithDecimals(recommendations.remaining, currentCurrency, 2) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.itemsRecommended') }}</div>
          <div class="stat-value">{{ recommendations.items.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
          <span class="budget-value">{{ formatCurrency(budget, currentCurrency) }}</span>
        </div>
        <input
          v-model.number="budget"
          type="range"
          class="budget-slider"
          min="0"
          :max="maxBudget"
          :step="BUDGET_STEP"
          :disabled="maxBudget === 0"
          :aria-label="t('restocking.budget')"
        />
        <div class="slider-scale">
          <span>{{ formatCurrency(0, currentCurrency) }}</span>
          <span class="full-cost">
            {{ t('restocking.fullRestockCost', { amount: formatCurrencyWithDecimals(recommendations.full_restock_cost, currentCurrency, 2) }) }}
          </span>
          <span>{{ formatCurrency(maxBudget, currentCurrency) }}</span>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ recommendations.items.length }})</h3>
          <button
            type="button"
            class="place-order-btn"
            :disabled="!canPlaceOrder"
            @click="placeOrder"
          >
            {{ placing ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="placedOrder" class="order-confirmation" role="status">
          <span>
            {{ t('restocking.orderPlaced', { orderNumber: placedOrder.order_number, days: placedOrder.lead_time_days }) }}
          </span>
          <router-link to="/orders">{{ t('restocking.viewInOrders') }}</router-link>
        </div>
        <div v-if="orderError" class="error" role="alert">{{ orderError }}</div>
        <div v-if="refreshError" class="error" role="alert">{{ refreshError }}</div>

        <div v-if="recommendations.items.length > 0" class="table-container">
          <table class="restock-table">
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.item') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.forecast') }}</th>
                <th class="num">{{ t('restocking.table.onHand') }}</th>
                <th class="num">{{ t('restocking.table.onOrder') }}</th>
                <th class="num">{{ t('restocking.table.shortfall') }}</th>
                <th class="num">{{ t('restocking.table.orderQty') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recommendations.items" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ item.item_name }}</td>
                <td>
                  <span :class="['badge', item.trend]">{{ t(`trends.${item.trend}`) }}</span>
                </td>
                <td class="num">{{ item.forecasted_demand.toLocaleString() }}</td>
                <td class="num">{{ item.quantity_on_hand.toLocaleString() }}</td>
                <td class="num">{{ item.quantity_on_order.toLocaleString() }}</td>
                <td class="num">{{ item.shortfall.toLocaleString() }}</td>
                <td class="num qty-cell">
                  <span v-if="item.partial" class="badge warning">{{ t('restocking.partial') }}</span>
                  <strong>{{ item.recommended_quantity.toLocaleString() }}</strong>
                </td>
                <td class="num">{{ formatCurrencyWithDecimals(item.unit_cost, currentCurrency, 2) }}</td>
                <td class="num"><strong>{{ formatCurrencyWithDecimals(item.line_total, currentCurrency, 2) }}</strong></td>
                <td class="num">{{ t('orders.leadTimeDays', { days: item.lead_time_days }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-state">
          {{ noCandidates ? t('restocking.allStocked') : t('restocking.budgetTooLow') }}
        </div>

        <p v-if="recommendations.uncovered_count > 0" class="uncovered-note">
          {{ t('restocking.notCovered', { count: recommendations.uncovered_count }) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

// Slider granularity in USD. The slider max and initial budget are snapped to it.
const BUDGET_STEP = 500
// How long the slider must rest before recommendations are refetched.
const DEBOUNCE_MS = 250

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency } = useI18n()

    const loading = ref(true)
    const error = ref(null)
    const recommendations = ref(null)
    const refreshError = ref(null)

    // Budget and slider max are USD; formatCurrency converts at display time only.
    const budget = ref(0)
    const maxBudget = ref(0)

    // True from the moment the slider moves until the matching response lands.
    const refreshing = ref(false)

    const placing = ref(false)
    const placedOrder = ref(null)
    const orderError = ref(null)

    let debounceTimer = null
    // Incremented per request so a slow, older response can't overwrite a newer one.
    let requestCounter = 0
    // Budget of the most recent request; lets the watcher skip the fetch we already started.
    let lastRequestedBudget = null

    const fetchRecommendations = async () => {
      clearTimeout(debounceTimer)
      const requestId = ++requestCounter
      lastRequestedBudget = budget.value
      refreshing.value = true
      try {
        const data = await api.getRestockRecommendations(budget.value)
        // A newer request has been issued since; its response owns the state.
        if (requestId !== requestCounter) return
        recommendations.value = data
        refreshError.value = null
      } catch (err) {
        if (requestId !== requestCounter) return
        refreshError.value = t('restocking.loadFailed')
        console.error('Failed to load restock recommendations:', err)
      } finally {
        if (requestId === requestCounter) refreshing.value = false
      }
    }

    const initialize = async () => {
      try {
        loading.value = true
        error.value = null

        // Without a budget the server sizes the plan to a full restock, which
        // tells us how far the slider needs to go.
        const full = await api.getRestockRecommendations(null)

        // Max: full restock cost rounded up to the next $500 step, so the top of
        // the slider always covers everything. Initial budget: half of that,
        // rounded down to a step (e.g. $36,500 -> $18,000).
        maxBudget.value = Math.ceil(full.full_restock_cost / BUDGET_STEP) * BUDGET_STEP
        budget.value = Math.floor(maxBudget.value / 2 / BUDGET_STEP) * BUDGET_STEP

        // Show the page only once the first budgeted response is in.
        await fetchRecommendations()
        if (!recommendations.value) {
          error.value = refreshError.value || t('restocking.loadFailed')
        }
      } catch (err) {
        error.value = t('restocking.loadFailed')
        console.error('Failed to initialize restocking:', err)
      } finally {
        loading.value = false
      }
    }

    // Debounce slider moves so dragging doesn't fire a request per step.
    watch(budget, (newBudget) => {
      if (newBudget === lastRequestedBudget) return
      orderError.value = null
      refreshing.value = true
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(fetchRecommendations, DEBOUNCE_MS)
    })

    const noCandidates = computed(() => {
      const rec = recommendations.value
      return !!rec && rec.items.length === 0 && rec.uncovered_count === 0
    })

    // Only order a plan that matches the slider. Comparing budgets catches cases the
    // `refreshing` flag misses: an older response landing while a newer debounce is
    // still pending, or a failed refetch leaving the previous plan on screen.
    // Slider values are whole dollars, so the server's echoed budget compares exactly.
    const planMatchesSlider = computed(() => {
      return !!recommendations.value && recommendations.value.budget === budget.value
    })

    const canPlaceOrder = computed(() => {
      return planMatchesSlider.value
        && recommendations.value.items.length > 0
        && !refreshError.value
        && !placing.value
        && !refreshing.value
    })

    const placeOrder = async () => {
      if (!canPlaceOrder.value) return

      placing.value = true
      placedOrder.value = null
      orderError.value = null

      // Submit the budget and lines of the displayed recommendation, not the live slider value.
      const { budget: orderBudget, items } = recommendations.value
      try {
        placedOrder.value = await api.createRestockOrder({
          budget: orderBudget,
          items: items.map(item => ({
            item_sku: item.item_sku,
            quantity: item.recommended_quantity
          }))
        })
      } catch (err) {
        // 400s carry a readable reason in `detail`; 422s carry an array, so fall back.
        const detail = err.response?.data?.detail
        orderError.value = typeof detail === 'string' ? detail : t('restocking.orderFailed')
        console.error('Failed to place restock order:', err)
      } finally {
        placing.value = false
      }

      // On success the new on-order stock shrinks the list; on failure the
      // server state may have changed (e.g. a double submit), so refresh either way.
      await fetchRecommendations()
    }

    onMounted(initialize)

    onBeforeUnmount(() => {
      clearTimeout(debounceTimer)
      // Invalidate any in-flight request so it can't touch state after unmount.
      requestCounter++
    })

    return {
      t,
      currentCurrency,
      formatCurrency,
      formatCurrencyWithDecimals,
      BUDGET_STEP,
      loading,
      error,
      refreshError,
      recommendations,
      budget,
      maxBudget,
      placing,
      placedOrder,
      orderError,
      noCandidates,
      canPlaceOrder,
      placeOrder
    }
  }
}
</script>

<style scoped>
.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.budget-slider {
  width: 100%;
  accent-color: #0f172a;
  cursor: pointer;
}

.budget-slider:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.slider-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.813rem;
  color: #64748b;
}

.full-cost {
  font-weight: 600;
  color: #0f172a;
}

.place-order-btn {
  padding: 0.5rem 1.25rem;
  background: #0f172a;
  color: white;
  border: 1px solid #0f172a;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.place-order-btn:hover:not(:disabled) {
  background: #1e293b;
}

.place-order-btn:disabled {
  background: #94a3b8;
  border-color: #94a3b8;
  cursor: not-allowed;
}

.order-confirmation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  color: #065f46;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.938rem;
}

.order-confirmation a {
  color: #065f46;
  font-weight: 600;
  white-space: nowrap;
}

.restock-table th,
.restock-table td {
  white-space: nowrap;
}

.restock-table .num {
  text-align: right;
}

.qty-cell .badge {
  margin-right: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
  color: #64748b;
  font-size: 0.938rem;
}

.uncovered-note {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: #64748b;
}
</style>
