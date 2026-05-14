<template>
  <div>
    <v-row class="pa-1 ga-1 align-stretch" no-gutters v-if="lgAndUp">
      <v-col class="rounded" colspan="12" lg="*" v-for="i in 3" :key="i">
        <v-card
          variant="outlined"
          :elevation="4"
          class="bg-surface d-flex flex-column h-100"
        >
          <v-card-title class="d-flex align-center">
            <span class="text-subtitle-2 text-primary">
              {{ getGraphTitle(i) }}
            </span>

            <WidgetForm v-if="authStore.isFullAccess" :widget="i" />
          </v-card-title>
          <v-card-text
            class="d-flex justify-center align-center pa-0 ga-0 ma-0 w-100"
          >
            <PieGraphWidget
              :key="1"
              :graph_items="getGraphData(i)"
              :isLoading="getGraphisLoading(i)"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row class="pa-1 ga-1" no-gutters v-else>
      <v-col class="rounded text-center" colspan="12">
        <v-card
          variant="outlined"
          :elevation="4"
          class="bg-surface d-flex flex-column h-100"
        >
          <v-card-title class="d-flex align-center">
            <span class="text-subtitle-2 text-primary">
              {{ getGraphTitle(page) }}
            </span>
            <WidgetForm v-if="authStore.isFullAccess" :widget="page" />
          </v-card-title>
          <v-card-text
            class="d-flex justify-center align-center pa-0 ga-0 ma-0 w-100"
          >
            <PieGraphWidget
              :graph_items="getGraphData(page)"
              :isLoading="getGraphisLoading(page)"
              :key="page"
            />
          </v-card-text>
          <v-pagination v-model="page" length="3" class="mt-4" />
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  import PieGraphWidget from "@/components/PieGraphWidget.vue";
  import WidgetForm from "@/components/WidgetForm.vue";
  import { useDisplay } from "vuetify";
  import { useGraphsNew } from "@/composables/tagsComposable";
  import { useOptions } from "@/composables/optionsComposable";
  import { ref } from "vue";
  import { useAuthStore } from "@/stores/auth";

  const authStore = useAuthStore();
  const { options: appOptions } = useOptions();
  const { lgAndUp } = useDisplay();
  const page = ref(1);

  const { tag_graph_items: graph_items_1, isLoading: isLoading_1 } =
    useGraphsNew(1);
  const { tag_graph_items: graph_items_2, isLoading: isLoading_2 } =
    useGraphsNew(2);
  const { tag_graph_items: graph_items_3, isLoading: isLoading_3 } =
    useGraphsNew(3);

  function getGraphTitle(widget) {
    return appOptions.value
      ? appOptions.value[`widget${widget}_graph_name`]
      : `Graph ${widget}`;
  }

  const graph_items_map = {
    1: graph_items_1,
    2: graph_items_2,
    3: graph_items_3,
  };

  const graph_isLoading_map = {
    1: isLoading_1,
    2: isLoading_2,
    3: isLoading_3,
  };

  function getGraphData(widget) {
    return graph_items_map[widget] ? graph_items_map[widget]?.value : null;
  }

  function getGraphisLoading(widget) {
    return graph_isLoading_map[widget]
      ? graph_isLoading_map[widget]?.value
      : null;
  }
</script>
