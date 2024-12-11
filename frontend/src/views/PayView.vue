<template>
  <v-container>
    <div v-if="!isLoading">
      <v-row class="pa-1 ga-1" no-gutters>
        <v-col class="rounded text-center">
          <v-tabs v-model="tab" color="accent">
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
                :isLoading="isLoading"
                v-if="!isMobile" />
              <ReportGraphWidgetMobile
                :data="item"
                :graphName="item.pretty_name"
                :key="index"
                :isLoading="isLoading"
                v-if="isMobile" /></v-window-item></v-window></v-col></v-row
      ><v-row class="pa-1 ga-1" no-gutters>
        <v-col class="rounded text-center"
          ><ReportTableWidget
            :isLoading="isLoading"
            :data="pay_graph[0].data" /></v-col
      ></v-row>
    </div>
    <div v-else>
      <v-row
        ><v-col cols="3"></v-col
        ><v-col
          class="text-accent text-subtitle-2 text-uppercase text-center font-italic"
        >
          Loading Data...</v-col
        ><v-col cols="3"></v-col
      ></v-row>
      <v-row
        ><v-col cols="3"></v-col
        ><v-col>
          <v-progress-linear
            color="accent"
            height="6"
            indeterminate
            rounded
          ></v-progress-linear> </v-col
        ><v-col cols="3"></v-col
      ></v-row>
    </div>
  </v-container>
</template>
<script setup>
import { ref } from "vue";
import ReportGraphWidget from "@/components/ReportGraphWidget.vue";
import ReportGraphWidgetMobile from "@/components/ReportGraphWidgetMobile.vue";
import ReportTableWidget from "@/components/ReportTableWidget.vue";
import { usePayGraph } from "@/composables/planningGraphComposable";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;

const { pay_graph, isLoading } = usePayGraph();

const tab = ref(0); // Tab model
</script>
