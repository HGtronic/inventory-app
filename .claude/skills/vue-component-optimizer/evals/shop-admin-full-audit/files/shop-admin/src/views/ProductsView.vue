<script setup>
import { ref, watch, onMounted } from "vue";
import ProductRow from "../components/ProductRow.vue";
import { fetchProducts, fetchCategories } from "../data/catalog";

const products = ref([]);
const categories = ref([]);
const loading = ref(true);
const error = ref(null);

const search = ref("");
const categoryFilter = ref("all");
const sortKey = ref("name");
const sortDir = ref("asc");
const totalStockValue = ref(0);

onMounted(async () => {
  try {
    const [productList, categoryList] = await Promise.all([
      fetchProducts(),
      fetchCategories(),
    ]);
    products.value = productList;
    categories.value = categoryList;
  } catch (e) {
    error.value = "Failed to load products";
  } finally {
    loading.value = false;
  }
});

watch(
  products,
  (list) => {
    totalStockValue.value = list.reduce((s, p) => s + p.price * p.stock, 0);
  },
  { deep: true },
);

function setSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === "asc" ? "desc" : "asc";
  } else {
    sortKey.value = key;
    sortDir.value = "asc";
  }
}

function filteredProducts() {
  const q = search.value.trim().toLowerCase();
  const list = products.value.filter((p) => {
    if (categoryFilter.value !== "all" && p.categoryId !== categoryFilter.value)
      return false;
    if (
      q &&
      !p.name.toLowerCase().includes(q) &&
      !p.sku.toLowerCase().includes(q)
    )
      return false;
    return true;
  });
  const dir = sortDir.value === "asc" ? 1 : -1;
  const key = sortKey.value;
  return list.sort((a, b) => {
    if (key === "name") return a.name.localeCompare(b.name) * dir;
    return (a[key] - b[key]) * dir;
  });
}

function getCategoryName(id) {
  const c = categories.value.find((c) => c.id === id);
  return c ? c.name : "Uncategorized";
}

function formatPrice(n) {
  return "$" + n.toFixed(2);
}
</script>

<template>
  <div class="products-view">
    <div class="page-header">
      <div>
        <h1>Products</h1>
        <p class="muted">Catalog and restocking</p>
      </div>
      <div class="card summary-card">
        <span class="summary-label">Total stock value</span>
        <span class="summary-value">{{ formatPrice(totalStockValue) }}</span>
      </div>
    </div>

    <p v-if="loading" class="muted">Loading products...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <div v-else class="card">
      <div class="toolbar">
        <input
          v-model="search"
          type="search"
          placeholder="Search name or SKU"
          class="search-input"
        />
        <select v-model="categoryFilter" aria-label="Category">
          <option value="all">All categories</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">
            {{ c.name }}
          </option>
        </select>
        <span class="muted result-count"
          >{{ filteredProducts().length }} products</span
        >
      </div>

      <table>
        <thead>
          <tr>
            <th></th>
            <th class="sortable" @click="setSort('name')">
              Name
              <span
                v-if="sortKey === 'name'"
                class="sort-indicator"
                :class="sortDir"
              ></span>
            </th>
            <th>SKU</th>
            <th>Category</th>
            <th class="sortable num" @click="setSort('price')">
              Price
              <span
                v-if="sortKey === 'price'"
                class="sort-indicator"
                :class="sortDir"
              ></span>
            </th>
            <th class="sortable num" @click="setSort('stock')">
              Stock
              <span
                v-if="sortKey === 'stock'"
                class="sort-indicator"
                :class="sortDir"
              ></span>
            </th>
            <th>Restock</th>
          </tr>
        </thead>
        <tbody>
          <ProductRow
            v-for="(p, index) in filteredProducts()"
            :key="index"
            :product="p"
            :category-name="getCategoryName(p.categoryId)"
            :options="{ currency: 'USD', showSku: true }"
          />
        </tbody>
      </table>
      <p v-if="filteredProducts().length === 0" class="empty muted">
        No products match the current filters.
      </p>
    </div>
  </div>
</template>

<style scoped>
.summary-card {
  display: flex;
  flex-direction: column;
  min-width: 200px;
}

.summary-label {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.summary-value {
  font-size: 22px;
  font-weight: 600;
}

.search-input {
  width: 260px;
}

.result-count {
  margin-left: auto;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sort-indicator {
  display: inline-block;
  margin-left: 4px;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  vertical-align: middle;
}

.sort-indicator.asc {
  border-bottom: 5px solid #64748b;
}

.sort-indicator.desc {
  border-top: 5px solid #64748b;
}

.empty {
  padding: 24px;
  text-align: center;
}
</style>
