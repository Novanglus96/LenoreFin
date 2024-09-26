import { defineStore } from "pinia";

export const usePlanningStore = defineStore("planning", {
  state: () => ({
    calculator: {
      selected_rule: null,
      timeframe: 0,
      selected_transactions: []
    },
  }),
  getters: {},
  actions: {},
});
