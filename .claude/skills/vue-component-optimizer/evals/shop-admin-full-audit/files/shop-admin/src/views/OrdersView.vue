<script setup>
import {
  ref,
  shallowRef,
  reactive,
  computed,
  watch,
  nextTick,
  onMounted,
} from "vue";
import OrderFilters from "../components/OrderFilters.vue";
import { fetchOrders } from "../data/catalog";
import { formatDate } from "../utils/format";

const NARROW_WIDTH = 900;

const orders = shallowRef([]);
const loading = ref(true);
const error = ref(null);

const filters = reactive({ status: "all", search: "", page: 1 });
const pageSize = 25;

const selectedOrder = shallowRef(null);
const drawerRef = ref(null);
const isNarrow = ref(window.innerWidth < NARROW_WIDTH);

const filteredOrders = computed(() => {
  const q = filters.search.trim().toLowerCase();
  return orders.value.filter((o) => {
    if (filters.status !== "all" && o.status !== filters.status) return false;
    if (
      q &&
      !o.id.toLowerCase().includes(q) &&
      !o.customerName.toLowerCase().includes(q)
    )
      return false;
    return true;
  });
});

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredOrders.value.length / pageSize)),
);

const pagedOrders = computed(() => {
  const start = (filters.page - 1) * pageSize;
  return filteredOrders.value.slice(start, start + pageSize);
});

const filteredRevenue = computed(() =>
  filteredOrders.value
    .filter((o) => o.status === "paid" || o.status === "shipped")
    .reduce((sum, o) => sum + o.total, 0),
);

const flaggedCount = computed(
  () => filteredOrders.value.filter((o) => o.flagged).length,
);

watch(
  () => filters.status,
  () => {
    filters.page = 1;
  },
);

async function load() {
  try {
    const data = await fetchOrders();
    orders.value = data.sort((a, b) => b.date.localeCompare(a.date));
  } catch (e) {
    error.value = "Failed to load orders";
  } finally {
    loading.value = false;
  }
}

function onResize() {
  isNarrow.value = window.innerWidth < NARROW_WIDTH;
}

onMounted(() => {
  load();
  window.addEventListener("resize", onResize);
});

async function openOrder(order) {
  selectedOrder.value = order;
  await nextTick();
  if (drawerRef.value) drawerRef.value.focus();
}

function closeDrawer() {
  selectedOrder.value = null;
}

function statusLabel(status) {
  const labels = {
    pending: "Pending",
    paid: "Paid",
    shipped: "Shipped",
    cancelled: "Cancelled",
    refunded: "Refunded",
  };
  return labels[status] || status;
}

function formatMoney(v) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(v);
}
</script>

<template>
  <div class="orders-view">
    <div class="page-header">
      <div>
        <h1>Orders</h1>
        <p class="muted">
          {{ filteredOrders.length }} orders match the current filters
        </p>
      </div>
      <div class="summary">
        <div class="card summary-card">
          <span class="summary-label">Collected revenue</span>
          <span class="summary-value">{{ formatMoney(filteredRevenue) }}</span>
        </div>
        <div class="card summary-card">
          <span class="summary-label">Flagged</span>
          <span class="summary-value">{{ flaggedCount }}</span>
        </div>
      </div>
    </div>

    <OrderFilters :filters="filters" />

    <p v-if="loading" class="muted">Loading orders...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else class="card">
      <table class="orders-table">
        <thead>
          <tr>
            <th>Order</th>
            <th>Customer</th>
            <th v-if="!isNarrow">Date</th>
            <th class="num">Items</th>
            <th class="num">Total</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="o in pagedOrders"
            :key="o.id"
            :class="{ active: selectedOrder && selectedOrder.id === o.id }"
            tabindex="0"
            @click="openOrder(o)"
            @keydown.enter="openOrder(o)"
          >
            <td class="mono">
              {{ o.id }}
              <span v-if="o.flagged" class="flag">Flagged</span>
            </td>
            <td>{{ o.customerName }}</td>
            <td v-if="!isNarrow">{{ formatDate(o.date) }}</td>
            <td class="num">{{ o.items.length }}</td>
            <td class="num">{{ formatMoney(o.total) }}</td>
            <td>
              <span class="status-pill" :class="'status-' + o.status">{{
                statusLabel(o.status)
              }}</span>
            </td>
          </tr>
          <tr v-if="pagedOrders.length === 0">
            <td :colspan="isNarrow ? 5 : 6" class="empty muted">
              No orders match the current filters.
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pager">
        <button
          type="button"
          :disabled="filters.page <= 1"
          @click="filters.page--"
        >
          Previous
        </button>
        <span class="muted">Page {{ filters.page }} of {{ totalPages }}</span>
        <button
          type="button"
          :disabled="filters.page >= totalPages"
          @click="filters.page++"
        >
          Next
        </button>
      </div>
    </div>

    <div v-if="selectedOrder" class="drawer-backdrop" @click.self="closeDrawer">
      <aside
        ref="drawerRef"
        class="drawer"
        role="dialog"
        aria-label="Order detail"
        tabindex="-1"
        @keydown.esc="closeDrawer"
      >
        <header class="drawer-header">
          <div>
            <h2>Order {{ selectedOrder.id }}</h2>
            <p class="muted">{{ formatDate(selectedOrder.date) }}</p>
          </div>
          <button
            type="button"
            aria-label="Close order detail"
            @click="closeDrawer"
          >
            Close
          </button>
        </header>

        <dl class="drawer-meta">
          <div>
            <dt>Customer</dt>
            <dd>{{ selectedOrder.customerName }}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{{ statusLabel(selectedOrder.status) }}</dd>
          </div>
          <div>
            <dt>Flagged for review</dt>
            <dd>{{ selectedOrder.flagged ? "Yes" : "No" }}</dd>
          </div>
        </dl>

        <table class="items-table">
          <thead>
            <tr>
              <th>SKU</th>
              <th class="num">Qty</th>
              <th class="num">Price</th>
              <th class="num">Line total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in selectedOrder.items" :key="item.sku">
              <td class="mono">{{ item.sku }}</td>
              <td class="num">{{ item.qty }}</td>
              <td class="num">{{ formatMoney(item.price) }}</td>
              <td class="num">{{ formatMoney(item.qty * item.price) }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="3" class="num drawer-total-label">Order total</td>
              <td class="num drawer-total">
                {{ formatMoney(selectedOrder.total) }}
              </td>
            </tr>
          </tfoot>
        </table>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.summary {
  display: flex;
  gap: 12px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  min-width: 160px;
  padding: 12px 16px;
}

.summary-label {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
}

.orders-table tbody tr {
  cursor: pointer;
}

.orders-table tbody tr:hover,
.orders-table tbody tr.active {
  background: #f8fafc;
}

.orders-table tbody tr:focus-visible {
  outline: 2px solid #94a3b8;
  outline-offset: -2px;
}

.empty {
  padding: 24px;
  text-align: center;
}

.flag {
  margin-left: 8px;
  padding: 1px 6px;
  font-family: inherit;
  font-size: 11px;
  font-weight: 600;
  color: #92400e;
  background: #fef3c7;
  border-radius: 4px;
}

.status-pill {
  display: inline-block;
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 999px;
}

.status-pending {
  color: #92400e;
  background: #fef3c7;
}

.status-paid {
  color: #166534;
  background: #dcfce7;
}

.status-shipped {
  color: #1e40af;
  background: #dbeafe;
}

.status-cancelled {
  color: #991b1b;
  background: #fee2e2;
}

.status-refunded {
  color: #475569;
  background: #e2e8f0;
}

.drawer-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: flex;
  justify-content: flex-end;
  background: rgba(15, 23, 42, 0.35);
}

.drawer {
  width: 440px;
  max-width: 100%;
  height: 100%;
  padding: 24px;
  overflow-y: auto;
  background: #fff;
  box-shadow: -4px 0 16px rgba(15, 23, 42, 0.15);
}

.drawer:focus {
  outline: none;
}

.drawer-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.drawer-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 0 0 20px;
}

.drawer-meta dt {
  font-size: 12px;
  color: #64748b;
}

.drawer-meta dd {
  margin: 0;
  font-weight: 500;
}

.drawer-total-label {
  font-weight: 600;
}

.drawer-total {
  font-weight: 600;
}
</style>
