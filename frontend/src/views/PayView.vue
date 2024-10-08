<template>
  <v-container>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center">
        <v-tabs v-model="tab" color="accent" v-if="!isLoading">
          <v-tab
            v-for="(item, index) in pay_graph[0].data"
            :key="index"
            :value="item.key_name"
            >{{ item.pretty_name }}</v-tab
          >
        </v-tabs>
        <v-window v-model="tab" v-if="!isLoading">
          <v-window-item
            v-for="(item, index) in pay_graph[0].data"
            :key="index"
            :value="item.key_name"
          >
            <ReportGraphWidget
              :data="item"
              :graphName="item.pretty_name"
              :key="index"
              :isLoading="
                isLoading
              " /></v-window-item></v-window></v-col></v-row
    ><v-row class="pa-1 ga-1" no-gutters v-if="!isLoading">
      <v-col class="rounded text-center"
        ><ReportTableWidget
          :isLoading="isLoading"
          :data="pay_graph[0].data" /></v-col
    ></v-row>
  </v-container>
</template>
<script setup>
import { ref } from "vue";
import ReportGraphWidget from "@/components/ReportGraphWidget.vue";
import ReportTableWidget from "@/components/ReportTableWidget.vue";
import { usePayGraph } from "@/composables/planningGraphComposable";

const { pay_graph, isLoading } = usePayGraph();

const tab = ref(0); // Tab model
</script>
