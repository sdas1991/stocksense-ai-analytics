import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import StockDetail from '../views/StockDetail.vue'
import Watchlist from '../views/Watchlist.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/stock/:symbol',
    name: 'StockDetail',
    component: StockDetail,
    props: true
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: Watchlist
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
