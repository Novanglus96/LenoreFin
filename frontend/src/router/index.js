import { createRouter, createWebHistory } from 'vue-router'
import DashBoard from '@/views/DashBoard.vue'
import FourView from '../views/FourView.vue'
import AccountsView from '@/views/AccountsView.vue'
import PlanningView from '@/views/PlanningView.vue'
import AccountDetailView from '@/views/AccountDetailView.vue'
import AddAccount from '@/views/AddAccount.vue'
import ForecastView from '@/views/ForecastView.vue'
import RemindersView from '@/views/RemindersView.vue'
import TagsView from '@/views/TagsView.vue'
import SettingsView from '@/views/SettingsView.vue'

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
    path: '/accounts/add',
    name: 'addaccount',
    component: AddAccount
  },
  {
    path: '/accounts/:accountID',
    name: 'account_detail',
    component: AccountDetailView,
  },
  {
    path: '/forecast',
    name: 'forecast',
    component: ForecastView,
  },
  {
    path: '/planning',
    name: 'planning',
    component: PlanningView
  },
  {
    path: '/reminders',
    name: 'reminders',
    component: RemindersView
  },
  {
    path: '/tags',
    name: 'tags',
    component: TagsView
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView
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
