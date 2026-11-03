<script setup>
import { ref } from "vue";

defineProps({
  product: { type: Object, required: true },
  categoryName: String,
  options: { type: Object, default: () => ({}) },
});

const selected = ref(false);
const qty = ref(1);
const added = ref(false);

function addToRestock() {
  added.value = true;
}
</script>

<template>
  <tr :class="{ selected }">
    <td class="check-col">
      <input
        v-model="selected"
        type="checkbox"
        :aria-label="'Select ' + product.name"
      />
    </td>
    <td>{{ product.name }}</td>
    <td class="mono">
      <template v-if="options.showSku">{{ product.sku }}</template>
    </td>
    <td>{{ categoryName }}</td>
    <td class="num">
      {{ options.currency === "USD" ? "$" : "" }}{{ product.price.toFixed(2) }}
    </td>
    <td class="num">{{ product.stock }}</td>
    <td>
      <div class="restock-col">
        <input
          v-model.number="qty"
          type="number"
          min="1"
          class="qty-input"
          aria-label="Restock quantity"
        />
        <button type="button" :disabled="added" @click="addToRestock">
          {{ added ? "Added" : "Add to restock" }}
        </button>
      </div>
    </td>
  </tr>
</template>

<style scoped>
tr.selected {
  background: #f1f5f9;
}

.check-col {
  width: 36px;
}

.restock-col {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.qty-input {
  width: 64px;
}
</style>
