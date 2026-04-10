import { createRouter, createWebHistory } from 'vue-router'
import store from './store'

const routes = [
  { path: '/login', name: 'Login', component: () => import('./views/Login.vue'), meta: { public: true } },
  { path: '/', name: 'Dashboard', component: () => import('./views/Dashboard.vue') },
  { path: '/flight/:id', name: 'FlightDetail', component: () => import('./views/FlightDetail.vue') },
  { path: '/analytics', name: 'Analytics', component: () => import('./views/Analytics.vue') },
  { path: '/battery', name: 'Battery', component: () => import('./views/BatteryHealth.vue') },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
