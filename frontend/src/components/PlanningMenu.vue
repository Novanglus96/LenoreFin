<template>
  <v-list density="compact" nav>
    <v-list-subheader color="secondary"
      ><v-icon icon="mdi-folder"></v-icon> PLANNING</v-list-subheader
    >
    <v-list-item
      v-for="(planning_item, i) in filteredPlanningMenu"
      :key="i"
      :to="planning_item.link"
      @click="setAccount(null, false, planning_item.link)"
      color="secondary"
      base-color="secondary"
      ><template v-slot:prepend
        ><v-icon
          :icon="planning_item.icon"
          :size="!isMobile ? 'large' : 'x-large'"
        ></v-icon
      ></template>
      <v-list-item-title
        ><span :class="isMobile ? 'text-h6' : ''">{{
          planning_item.title
        }}</span></v-list-item-title
      >
    </v-list-item>
  </v-list>
</template>
<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useTransactionsStore } from "@/stores/transactions";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;

const transactions_store = useTransactionsStore();
const router = useRouter();
const app_personal = computed(() => process.env.VUE_APP_PERSONAL === "true");

const planning_menu = ref([
  {
    title: "Pay",
    link: "/planning/pay",
    icon: "mdi-checkbook",
    personal: false,
  },
  {
    title: "Expenses",
    link: "/planning/expenses",
    icon: "mdi-cash",
    personal: false,
  },
  {
    title: "Budgets",
    link: "/planning/budgets",
    icon: "mdi-pail",
    personal: false,
  },
  {
    title: "Contributions",
    link: "/planning/contributions",
    icon: "mdi-pail",
    personal: true,
  },
  {
    title: "Retirement",
    link: "/planning/retirement",
    icon: "mdi-piggy-bank",
    personal: false,
  },
  {
    title: "Notes",
    link: "/planning/notes",
    icon: "mdi-note",
    personal: true,
  },
  {
    title: "Calculator",
    link: "/planning/calculator",
    icon: "mdi-calculator",
    personal: true,
  },
]);

const setAccount = (account, forecast, link) => {
  if (link == "/planning/calculator") {
    transactions_store.pageinfo.account_id = account;
    transactions_store.pageinfo.forecast = forecast;
    transactions_store.pageinfo.page = 1;
    transactions_store.pageinfo.maxdays = 0;
    transactions_store.pageinfo.view_type = 3;
  }

  router.push(link);
};

const filteredPlanningMenu = computed(() =>
  planning_menu.value.filter(item => {
    return (item.personal && app_personal) || !item.personal;
  }),
);
</script>
