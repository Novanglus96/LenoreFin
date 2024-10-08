<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center">
        <v-tabs v-model="main_tab" color="accent">
          <v-tab
            v-for="(main, index) in expenses"
            :key="index"
            :value="main.title"
            >{{ main.title }}</v-tab
          >
        </v-tabs>
        <v-window v-model="main_tab">
          <v-window-item
            v-for="(main_window, main_index) in expenses"
            :key="main_index"
            :value="main_window.title"
          >
            <v-tabs v-model="tab[main_index]" color="accent">
              <v-tab
                v-for="(sub_window, sub_index) in main_window.data"
                :key="sub_index"
                :value="sub_window.key_name"
                >{{ sub_window.pretty_name }}</v-tab
              >
            </v-tabs>
            <v-window v-model="tab[main_index]">
              <v-window-item
                v-for="(sub_window, sub_index) in main_window.data"
                :key="sub_index"
                :value="sub_window.key_name"
              >
                <ReportGraphWidget
                  :data="sub_window"
                  :graphName="sub_window.pretty_name"
                  :key="sub_index"
                  :isLoading="isLoading"
              /></v-window-item>
              <ReportTableWidget
                :isLoading="isLoading"
                :data="main_window.data"
            /></v-window>
          </v-window-item>
        </v-window> </v-col
    ></v-row>
  </v-container>
</template>
<script setup>
import { ref } from "vue";
import ReportGraphWidget from "@/components/ReportGraphWidget.vue";
import ReportTableWidget from "@/components/ReportTableWidget.vue";
import { useExpenseGraph } from "@/composables/planningGraphComposable";

const { expense_graph: expenses, isLoading } = useExpenseGraph();

const main_tab = ref(0);

const tab = ref(Array(expenses.length).fill(0));
</script>
