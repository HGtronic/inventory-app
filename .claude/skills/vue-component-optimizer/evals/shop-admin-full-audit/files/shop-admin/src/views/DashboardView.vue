<script setup>
import { ref, shallowRef, computed, onMounted, onUnmounted } from "vue";
import { fetchProducts, fetchOrders, fetchCustomers } from "../data/catalog";
import { formatCurrency, formatDate } from "../utils/format";

const DAY_MS = 24 * 60 * 60 * 1000;

const products = shallowRef([]);
const orders = shallowRef([]);
const customers = shallowRef([]);
const loading = ref(true);
const error = ref(null);
const showHelp = ref(false);

const now = ref(new Date());
let timer;

const formatPercent = (v) => (v > 0 ? "+" : "") + v.toFixed(1) + "%";

function summarize(list) {
  const billable = list.filter(
    (o) => o.status !== "cancelled" && o.status !== "refunded",
  );
  const revenue = billable.reduce((sum, o) => sum + o.total, 0);
  return {
    revenue,
    orders: list.length,
    avgOrder: billable.length ? revenue / billable.length : 0,
    buyers: new Set(list.map((o) => o.customerId)).size,
  };
}

function pctChange(current, previous) {
  return previous ? ((current - previous) / previous) * 100 : 0;
}

// Compares the latest 30 days of orders against the 30 days before that.
const kpis = computed(() => {
  const dated = orders.value
    .map((o) => ({ order: o, time: new Date(o.date).getTime() }))
    .filter((e) => !isNaN(e.time));
  if (!dated.length) return [];
  const end = Math.max(...dated.map((e) => e.time));
  const current = summarize(
    dated.filter((e) => end - e.time <= 30 * DAY_MS).map((e) => e.order),
  );
  const previous = summarize(
    dated
      .filter((e) => end - e.time > 30 * DAY_MS && end - e.time <= 60 * DAY_MS)
      .map((e) => e.order),
  );
  const activeCustomers = customers.value.filter(
    (c) => c.status !== "inactive",
  ).length;
  return [
    {
      label: "Revenue (30d)",
      value: formatCurrency(current.revenue),
      change: pctChange(current.revenue, previous.revenue),
    },
    {
      label: "Orders (30d)",
      value: current.orders.toLocaleString(),
      change: pctChange(current.orders, previous.orders),
    },
    {
      label: "Avg order value",
      value: formatCurrency(current.avgOrder),
      change: pctChange(current.avgOrder, previous.avgOrder),
    },
    {
      label: "Active customers",
      value: activeCustomers.toLocaleString(),
      change: pctChange(current.buyers, previous.buyers),
    },
  ];
});

const recentOrders = computed(() =>
  [...orders.value].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 50),
);

const latestOrders = computed(() => recentOrders.value.slice(0, 8));

function topProducts() {
  return [...products.value]
    .sort((a, b) => b.price * b.stock - a.price * a.stock)
    .slice(0, 5);
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

async function load() {
  try {
    const [productList, orderList, customerList] = await Promise.all([
      fetchProducts(),
      fetchOrders(),
      fetchCustomers(),
    ]);
    products.value = productList;
    orders.value = orderList;
    customers.value = customerList;
  } catch (e) {
    error.value = "Failed to load dashboard data";
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  load();
  timer = setInterval(() => {
    now.value = new Date();
  }, 1000);
});

onUnmounted(() => {
  clearInterval(timer);
});
</script>

<template>
  <div class="dashboard-view">
    <div class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p class="muted">
          {{ now.toLocaleDateString() }} {{ now.toLocaleTimeString() }}
        </p>
      </div>
      <button type="button" @click="showHelp = !showHelp">Help</button>
    </div>

    <div v-show="showHelp" class="card tips">
      <h2>Dashboard tips</h2>
      <ul>
        <li>
          KPI cards compare the latest 30 days of orders with the 30 days
          before.
        </li>
        <li>
          Top products are ranked by stock value (price multiplied by units in
          stock).
        </li>
        <li>
          Open the Orders page to filter by status or inspect a single order.
        </li>
      </ul>
    </div>

    <section v-if="loading" class="kpi-row">
      <div v-for="n in 4" :key="n" class="skeleton-card" />
    </section>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else>
      <section class="kpi-row">
        <div v-for="k in kpis" :key="k.label" class="card kpi">
          <span class="kpi-label">{{ k.label }}</span>
          <span class="kpi-value">{{ k.value }}</span>
          <span class="kpi-change" :class="k.change >= 0 ? 'up' : 'down'">{{
            formatPercent(k.change)
          }}</span>
        </div>
      </section>

      <div class="panel-row">
        <section class="card panel">
          <h2>Top products</h2>
          <ol class="product-list">
            <li v-for="p in topProducts()" :key="p.id">
              <span>{{ p.name }}</span>
              <span class="muted">{{ formatCurrency(p.price * p.stock) }}</span>
            </li>
          </ol>
        </section>

        <section class="card panel">
          <h2>Flagged orders</h2>
          <ul class="flag-list">
            <li v-for="o in recentOrders" :key="o.id" v-if="o?.flagged">
              {{ o.id }} - {{ o.customerName }} - {{ formatCurrency(o.total) }}
            </li>
          </ul>
          <p class="muted hint">Orders flagged for review appear here.</p>
        </section>
      </div>

      <section class="card panel">
        <h2>Recent orders</h2>
        <table>
          <thead>
            <tr>
              <th>Order</th>
              <th>Customer</th>
              <th>Date</th>
              <th class="num">Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in latestOrders" :key="o.id">
              <td class="mono">{{ o.id }}</td>
              <td>{{ o.customerName }}</td>
              <td>{{ formatDate(o.date) }}</td>
              <td class="num">{{ formatCurrency(o.total) }}</td>
              <td>
                <span class="status-pill" :class="'status-' + o.status">{{
                  statusLabel(o.status)
                }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<style scoped>
.tips {
  margin-bottom: 16px;
}

.tips ul {
  margin: 8px 0 0;
  padding-left: 20px;
  color: #475569;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.kpi {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.kpi-label {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.kpi-value {
  font-size: 24px;
  font-weight: 600;
}

.kpi-change {
  font-size: 13px;
  font-weight: 500;
}

.kpi-change.up {
  color: #166534;
}

.kpi-change.down {
  color: #991b1b;
}

.skeleton-card {
  height: 96px;
  background: #e2e8f0;
  border-radius: 8px;
}

.panel-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.panel h2 {
  margin-bottom: 12px;
}

.product-list {
  margin: 0;
  padding-left: 20px;
}

.product-list li {
  padding: 4px 0;
}

.product-list li span:last-child {
  float: right;
}

.flag-list {
  margin: 0;
  padding-left: 20px;
}

.hint {
  margin-top: 12px;
  font-size: 13px;
}

.status-pill {
  display: inline-block;
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 999px;
}

.status-pending {
  color: #854d0e;
  background: #fef9c3;
}

.status-paid {
  color: #15803d;
  background: #dcfce7;
}

.status-shipped {
  color: #1d4ed8;
  background: #dbeafe;
}

.status-cancelled {
  color: #b91c1c;
  background: #fee2e2;
}

.status-refunded {
  color: #475569;
  background: #f1f5f9;
}
</style>
