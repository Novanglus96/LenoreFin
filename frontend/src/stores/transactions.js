import { defineStore } from "pinia";

export const useTransactionsStore = defineStore("transactions", {
  state: () => ({
    pageinfo: {
      account_id: null,
      maxdays: 14,
      forecast: true,
      page: 1,
      page_size: 30,
      view_type: 2,
      rule_id: null,
    },
  }),
  getters: {},
  actions: {},
});
