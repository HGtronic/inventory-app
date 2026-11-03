<script setup>
import { watch } from "vue";

const props = defineProps({ filters: Object });

function reset() {
  props.filters.status = "all";
  props.filters.search = "";
  props.filters.page = 1;
}

watch(
  () => props.filters.search,
  () => {
    props.filters.page = 1;
  },
);
</script>

<template>
  <div class="card order-filters">
    <label class="field">
      <span class="field-label">Status</span>
      <select v-model="filters.status">
        <option value="all">All statuses</option>
        <option value="pending">Pending</option>
        <option value="paid">Paid</option>
        <option value="shipped">Shipped</option>
        <option value="cancelled">Cancelled</option>
        <option value="refunded">Refunded</option>
      </select>
    </label>
    <label class="field grow">
      <span class="field-label">Search</span>
      <input
        v-model="filters.search"
        type="search"
        placeholder="Order ID or customer"
      />
    </label>
    <button type="button" @click="reset">Reset</button>
  </div>
</template>

<style scoped>
.order-filters {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  margin-bottom: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field.grow {
  flex: 1;
}

.field-label {
  font-size: 12px;
  color: #64748b;
}
</style>
