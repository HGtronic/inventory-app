import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "../views/DashboardView.vue";
import ProductsView from "../views/ProductsView.vue";
import OrdersView from "../views/OrdersView.vue";
import CustomersView from "../views/CustomersView.vue";

const routes = [
  { path: "/", name: "dashboard", component: DashboardView },
  { path: "/products", name: "products", component: ProductsView },
  { path: "/orders", name: "orders", component: OrdersView },
  { path: "/customers", name: "customers", component: CustomersView },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
