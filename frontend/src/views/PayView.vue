<template>
  <div v-if="!isLoading">
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded text-center">
        <v-tabs v-model="tab" color="accent" center-active show-arrows>
          <v-tab
            v-for="(item, index) in pay_graph[0].data"
            :key="index"
            :value="item.key_name"
            color="accent"
            class="text-secondary"
          >
            {{ item.pretty_name }}
          </v-tab>
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
              :isLoading="isLoading"
            />
          </v-window-item>
          <ReportTableWidget :isLoading="isLoading" :data="pay_graph[0].data" />
        </v-window>
      </v-col>
    </v-row>
  </div>
  <div v-else>
    <v-row>
      <v-col cols="3"></v-col>
      <v-col
        class="text-accent text-subtitle-2 text-uppercase text-center font-italic"
      >
        Loading Data...
      </v-col>
      <v-col cols="3"></v-col>
    </v-row>
    <v-row>
      <v-col cols="3"></v-col>
      <v-col>
        <v-progress-linear
          color="accent"
          height="6"
          indeterminate
          rounded
        ></v-progress-linear>
      </v-col>
      <v-col cols="3"></v-col>
    </v-row>
  </div>
</template>
<script setup>
  import { ref } from "vue";
  import ReportGraphWidget from "@/components/ReportGraphWidget.vue";
  import ReportTableWidget from "@/components/ReportTableWidget.vue";
  import { usePayGraph } from "@/composables/planningGraphComposable";

  const { pay_graph, isLoading } = usePayGraph();

  const tab = ref(0); // Tab model
</script>
