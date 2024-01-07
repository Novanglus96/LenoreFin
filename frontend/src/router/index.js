import { createRouter, createWebHistory } from 'vue-router'
import DashBoard from '@/views/DashBoard.vue'
import FourView from '../views/FourView.vue'
import AccountsView from '@/views/AccountsView.vue'
import PlanningView from '@/views/PlanningView.vue'
import AccountDetailView from '@/views/AccountDetailView.vue'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DashBoard
  },
  {
    path: '/accounts',
    name: 'accounts',
    component: AccountsView
  },
  {
    path: '/accounts/:accountID',
    name: 'account_detail',
    component: AccountDetailView,
  },
  {
    path: '/planning',
    name: 'planning',
    component: PlanningView
  },
  { 
    path: '/:catchAll(.*)', 
    component: FourView,
    name: 'NotFound'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
