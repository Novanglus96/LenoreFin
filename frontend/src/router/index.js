import { createRouter, createWebHistory } from "vue-router";
import DashBoard from "@/views/DashBoard.vue";
import FourView from "../views/FourView.vue";
import AccountsView from "@/views/AccountsView.vue";
import PlanningView from "@/views/PlanningView.vue";
import AccountDetailView from "@/views/AccountDetailView.vue";
import AddAccount from "@/views/AddAccount.vue";
import ForecastView from "@/views/ForecastView.vue";
import RemindersView from "@/views/RemindersView.vue";
import TagsView from "@/views/TagsView.vue";
import DocumentView from "@/views/DocumentView.vue";
import CalculatorView from "@/views/CalculatorView.vue";
import PayView from "@/views/PayView.vue";
import ContributionsView from "@/views/ContributionsView.vue";
import ExpensesView from "@/views/ExpensesView.vue";
import NotesView from "@/views/NotesView.vue";
import RetirementView from "@/views/RetirementView.vue";
import BudgetsView from "@/views/BudgetsView.vue";

const routes = [
  {
    path: "/",
    name: "dashboard",
    component: DashBoard,
  },
  {
    path: "/docs",
    name: "docs",
    component: DocumentView,
  },
  {
    path: "/accounts",
    name: "accounts",
    component: AccountsView,
  },
  {
    path: "/accounts/add",
    name: "addaccount",
    component: AddAccount,
  },
  {
    path: "/accounts/:accountID",
    name: "account_detail",
    component: AccountDetailView,
  },
  {
    path: "/forecast",
    name: "forecast",
    component: ForecastView,
  },
  {
    path: "/planning",
    name: "planning",
    component: PlanningView,
  },
  {
    path: "/reminders",
    name: "reminders",
    component: RemindersView,
  },
  {
    path: "/tags",
    name: "tags",
    component: TagsView,
  },
  {
    path: "/planning/calculator",
    name: "calculator",
    component: CalculatorView,
  },
  {
    path: "/planning/contributions",
    name: "contributions",
    component: ContributionsView,
  },
  {
    path: "/planning/budgets",
    name: "budgets",
    component: BudgetsView,
  },
  {
    path: "/planning/expenses",
    name: "expenses",
    component: ExpensesView,
  },
  {
    path: "/planning/notes",
    name: "notes",
    component: NotesView,
  },
  {
    path: "/planning/pay",
    name: "pay",
    component: PayView,
  },
  {
    path: "/planning/retirement",
    name: "retirement",
    component: RetirementView,
  },
  {
    path: "/:catchAll(.*)",
    component: FourView,
    name: "NotFound",
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// Add a global beforeEach guard
router.beforeEach((to, from, next) => {
  const isPageReload = sessionStorage.getItem("isPageReload");
  sessionStorage.removeItem("isPageReload");

  if (isPageReload && to.fullPath !== "/") {
    next("/");
  } else {
    next();
  }
});

// Set a flag to detect page reload
window.addEventListener("beforeunload", () => {
  sessionStorage.setItem("isPageReload", "true");
});

export default router;
