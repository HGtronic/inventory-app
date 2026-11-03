<script>
import { fetchCustomers } from "../data/catalog";

const SETTINGS_KEY = "customerSettings";
const DEFAULT_SETTINGS = { pageSize: 25, showInactive: true, compact: false };

function loadSettings() {
  try {
    const stored = JSON.parse(localStorage.getItem(SETTINGS_KEY));
    return { ...DEFAULT_SETTINGS, ...stored };
  } catch (e) {
    return { ...DEFAULT_SETTINGS };
  }
}

export default {
  name: "CustomersView",
  data() {
    return {
      customers: [],
      loading: true,
      error: null,
      page: 1,
      search: "",
      settings: loadSettings(),
    };
  },
  computed: {
    pageSize() {
      return this.settings.pageSize;
    },
    visibleCustomers() {
      const q = this.search.trim().toLowerCase();
      return this.customers.filter((c) => {
        if (!this.settings.showInactive && c.status === "inactive")
          return false;
        if (
          q &&
          !c.name.toLowerCase().includes(q) &&
          !c.email.toLowerCase().includes(q)
        )
          return false;
        return true;
      });
    },
    totalPages() {
      return Math.max(
        1,
        Math.ceil(this.visibleCustomers.length / this.pageSize),
      );
    },
    pagedCustomers() {
      const start = (this.page - 1) * this.pageSize;
      return this.visibleCustomers.slice(start, start + this.pageSize);
    },
  },
  watch: {
    settings: {
      handler(v) {
        localStorage.setItem(SETTINGS_KEY, JSON.stringify(v));
      },
      deep: true,
    },
  },
  async mounted() {
    try {
      this.customers = await fetchCustomers();
    } catch (e) {
      this.error = "Failed to load customers";
    } finally {
      this.loading = false;
    }
  },
  methods: {
    prevPage() {
      if (this.page > 1) this.page--;
    },
    nextPage() {
      if (this.page < this.totalPages) this.page++;
    },
    statusLabel(status) {
      const labels = { active: "Active", inactive: "Inactive", vip: "VIP" };
      return labels[status] || status;
    },
    formatCurrency(v) {
      return "$" + Math.round(v).toLocaleString();
    },
  },
};
</script>

<template>
  <div class="customers-view">
    <div class="page-header">
      <div>
        <h1>Customers</h1>
        <p class="muted">{{ visibleCustomers.length }} customers</p>
      </div>
    </div>

    <div class="card settings-bar">
      <input
        v-model="search"
        type="search"
        placeholder="Search name or email"
        class="search-input"
        @input="page = 1"
      />
      <label class="setting">
        <span>Rows per page</span>
        <select v-model.number="settings.pageSize" @change="page = 1">
          <option :value="10">10</option>
          <option :value="25">25</option>
          <option :value="50">50</option>
        </select>
      </label>
      <label class="setting">
        <input
          v-model="settings.showInactive"
          type="checkbox"
          @change="page = 1"
        />
        <span>Show inactive</span>
      </label>
      <label class="setting">
        <input v-model="settings.compact" type="checkbox" />
        <span>Compact rows</span>
      </label>
    </div>

    <p v-if="loading" class="muted">Loading customers...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else class="card">
      <table :class="{ compact: settings.compact }">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>City</th>
            <th>Status</th>
            <th class="num">Lifetime value</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in pagedCustomers" :key="customer.id">
            <td>{{ customer.name }}</td>
            <td class="muted">{{ customer.email }}</td>
            <td>{{ customer.city }}</td>
            <td>
              <span class="status-pill" :class="'status-' + customer.status">{{
                statusLabel(customer.status)
              }}</span>
            </td>
            <td class="num">{{ formatCurrency(customer.lifetimeValue) }}</td>
          </tr>
          <tr v-if="pagedCustomers.length === 0">
            <td colspan="5" class="empty muted">
              No customers match the current filters.
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pager">
        <button type="button" :disabled="page <= 1" @click="prevPage">
          Previous
        </button>
        <span class="muted">Page {{ page }} of {{ totalPages }}</span>
        <button type="button" :disabled="page >= totalPages" @click="nextPage">
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-bar {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
}

.search-input {
  width: 260px;
}

.setting {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
}

table.compact th,
table.compact td {
  padding-top: 3px;
  padding-bottom: 3px;
}

.empty {
  padding: 24px;
  text-align: center;
}

.status-pill {
  display: inline-block;
  padding: 2px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 999px;
}

.status-active {
  color: #166534;
  background: #dcfce7;
}

.status-inactive {
  color: #475569;
  background: #e2e8f0;
}

.status-vip {
  color: #6b21a8;
  background: #f3e8ff;
}
</style>
