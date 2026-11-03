<template>
  <div class="backlog">
    <div class="page-header">
      <h2>{{ t('backlog.title') }}</h2>
      <p>{{ t('backlog.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('backlog.loading') }}</div>
    <div v-else-if="error" class="error">{{ t('backlog.loadFailed', { message: error }) }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card danger">
          <div class="stat-label">{{ t('backlog.priorityStat', { priority: t('priority.high') }) }}</div>
          <div class="stat-value">{{ priorityCounts.high }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('backlog.priorityStat', { priority: t('priority.medium') }) }}</div>
          <div class="stat-value">{{ priorityCounts.medium }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('backlog.priorityStat', { priority: t('priority.low') }) }}</div>
          <div class="stat-value">{{ priorityCounts.low }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('backlog.totalItems') }}</div>
          <div class="stat-value">{{ backlogItems.length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('backlog.itemsTitle') }}</h3>
        </div>
        <div v-if="backlogItems.length === 0" class="empty-state">
          <p class="empty-message">
            ✓ {{ t('backlog.noBacklog') }}
          </p>
        </div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('backlog.table.orderId') }}</th>
                <th>{{ t('backlog.table.sku') }}</th>
                <th>{{ t('backlog.table.itemName') }}</th>
                <th>{{ t('backlog.table.quantityNeeded') }}</th>
                <th>{{ t('backlog.table.quantityAvailable') }}</th>
                <th>{{ t('backlog.table.shortage') }}</th>
                <th>{{ t('backlog.table.daysDelayed') }}</th>
                <th>{{ t('backlog.table.priority') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in backlogItems" :key="item.id">
                <td><strong>{{ item.order_id }}</strong></td>
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>
                  {{ translateProductName(item.item_name) }}
                  <!-- has_purchase_order is set by the API once a PO exists for this backlog item -->
                  <span v-if="item.has_purchase_order" class="badge info po-badge">
                    {{ t('backlog.poPlaced') }}
                  </span>
                </td>
                <td>{{ item.quantity_needed }}</td>
                <td>{{ item.quantity_available }}</td>
                <td>
                  <span class="badge danger">
                    {{ t('backlog.unitsShort', { count: item.quantity_needed - item.quantity_available }) }}
                  </span>
                </td>
                <td>
                  <!-- Amber up to a week late, red beyond that -->
                  <span :style="{ color: item.days_delayed > 7 ? '#ef4444' : '#f59e0b' }">
                    {{ t('backlog.days', { count: item.days_delayed }) }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', item.priority]">
                    {{ translatePriority(item.priority) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'

export default {
  name: 'Backlog',
  setup() {
    const { t, translateProductName } = useI18n()
    const loading = ref(true)
    const error = ref(null)
    const allBacklogItems = ref([])
    const inventoryItems = ref([])

    // Use shared filters
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    // Filter backlog based on inventory filters
    const backlogItems = computed(() => {
      if (selectedLocation.value === 'all' && selectedCategory.value === 'all') {
        return allBacklogItems.value
      }

      // The backlog endpoint has no warehouse/category filters, so keep only the items
      // whose SKU appears in the (already filtered) inventory list
      const validSkus = new Set(inventoryItems.value.map(item => item.sku))
      return allBacklogItems.value.filter(b => validSkus.has(b.item_sku))
    })

    // Counts for the stat cards, computed once per data change instead of once per render call
    const priorityCounts = computed(() => {
      const counts = { high: 0, medium: 0, low: 0 }
      for (const item of backlogItems.value) {
        if (Object.hasOwn(counts, item.priority)) counts[item.priority]++
      }
      return counts
    })

    // Backend priorities are lowercase ("high"); fall back to the raw value if it is unknown
    const translatePriority = (priority) => {
      return ['high', 'medium', 'low'].includes(priority) ? t(`priority.${priority}`) : priority
    }

    const loadBacklog = async () => {
      try {
        loading.value = true
        error.value = null
        const filters = getCurrentFilters()

        const [backlogData, inventoryData] = await Promise.all([
          api.getBacklog(),
          api.getInventory({
            warehouse: filters.warehouse,
            category: filters.category
          })
        ])

        allBacklogItems.value = backlogData
        inventoryItems.value = inventoryData
      } catch (err) {
        // Only the raw detail is stored; the "Failed to load" wording is translated in the template
        error.value = err.message || t('common.error')
        console.error('Failed to load backlog:', err)
      } finally {
        loading.value = false
      }
    }

    // Watch for filter changes and reload data
    watch([selectedLocation, selectedCategory], () => {
      loadBacklog()
    })

    onMounted(loadBacklog)

    return {
      t,
      translateProductName,
      translatePriority,
      loading,
      error,
      backlogItems,
      priorityCounts
    }
  }
}
</script>

<style scoped>
.empty-state {
  padding: 3rem;
  text-align: center;
}

.empty-message {
  font-size: 1.125rem;
  color: #10b981;
  font-weight: 600;
}

/* Sits next to the item name without pushing the table wider */
.po-badge {
  margin-left: 0.5rem;
  white-space: nowrap;
}
</style>
