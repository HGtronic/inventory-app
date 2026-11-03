<script>
import { fetchOrders } from "../data/catalog";
import { formatCurrency } from "../utils/format";

export default {
  name: "LegacyReportsView",
  data() {
    return {
      orders: [],
    };
  },
  computed: {
    totalsByStatus() {
      const totals = {};
      for (const o of this.orders) {
        totals[o.status] = (totals[o.status] || 0) + o.total;
      }
      return Object.entries(totals).map(([status, total]) => ({
        status,
        total,
      }));
    },
  },
  created() {
    fetchOrders().then((orders) => {
      this.orders = orders;
    });
  },
  methods: {
    formatCurrency,
  },
};
</script>

<template>
  <div class="legacy-reports">
    <h1>Reports</h1>
    <table>
      <thead>
        <tr>
          <th>Status</th>
          <th class="num">Total</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in totalsByStatus" :key="row.status">
          <td>{{ row.status }}</td>
          <td class="num">{{ formatCurrency(row.total) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.legacy-reports {
  max-width: 480px;
}
</style>
