import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import ContactsView from '../views/ContactsView.vue'
import DealsView from '../views/DealsView.vue'
import ReportsView from '../views/ReportsView.vue'
import SettingsView from '../views/SettingsView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView, meta: { title: 'Dashboard' } },
    { path: '/contacts', name: 'contacts', component: ContactsView, meta: { title: 'Contacts' } },
    { path: '/deals', name: 'deals', component: DealsView, meta: { title: 'Deals' } },
    { path: '/reports', name: 'reports', component: ReportsView, meta: { title: 'Reports' } },
    { path: '/settings', name: 'settings', component: SettingsView, meta: { title: 'Settings' } }
  ]
})
