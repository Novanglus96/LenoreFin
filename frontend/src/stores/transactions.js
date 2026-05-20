import { defineStore } from "pinia";

export const useTransactionsStore = defineStore("transactions", {
  state: () => ({
    pageinfo: {
      account_id: null,
      maxdays: 14,
      forecast: true,
      page: 1,
      page_size: 60,
      view_type: 2,
      rule_id: null,
      search: null,
      status_id: null,
      transaction_type_id: null,
      tag_id: null,
    },
  }),
  getters: {},
  actions: {
    resetFilters() {
      this.pageinfo.search = null;
      this.pageinfo.status_id = null;
      this.pageinfo.transaction_type_id = null;
      this.pageinfo.tag_id = null;
      this.pageinfo.page = 1;
    },
  },
});
