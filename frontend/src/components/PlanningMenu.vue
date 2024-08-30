<template>
  <v-list density="compact" nav>
    <v-list-subheader color="secondary"
      ><v-icon icon="mdi-folder"></v-icon> PLANNING</v-list-subheader
    >
    <v-list-item
      v-for="(planning_item, i) in planning_menu"
      :key="i"
      :prepend-icon="planning_item.icon"
      :to="planning_item.link"
      @click="setAccount(null, false, planning_item.link)"
      color="accent"
    >
      <v-list-item-title>{{ planning_item.title }}</v-list-item-title>
    </v-list-item>
  </v-list>
</template>
<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useTransactionsStore } from "@/stores/transactions";

const transactions_store = useTransactionsStore();
const router = useRouter();

const planning_menu = ref([
  {
    title: "Pay",
    link: "/planning/pay",
    icon: "mdi-checkbook",
  },
  {
    title: "Expenses",
    link: "/planning/expenses",
    icon: "mdi-cash",
  },
  {
    title: "Contributions",
    link: "/planning/contributions",
    icon: "mdi-pail",
  },
  {
    title: "Retirement",
    link: "/planning/retirement",
    icon: "mdi-piggy-bank",
  },
  {
    title: "Christmas",
    link: "/planning/christmas",
    icon: "mdi-pine-tree",
  },
  {
    title: "Notes",
    link: "/planning/notes",
    icon: "mdi-note",
  },
  {
    title: "Calculator",
    link: "/planning/calculator",
    icon: "mdi-calculator",
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
</script>
