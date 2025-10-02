<template>
  <div>
    <v-pie
      :items="props.graph_items"
      :legend="{
        position: $vuetify.display.mdAndUp ? 'right' : 'bottom',
      }"
      :tooltip="{
        subtitleFormat: s =>
          `$${formatNumber(s.value)}(${((100 * s.value) / total).toFixed(1)}%)`,
      }"
      animation
      gap="0"
      density="compact"
      reveal
      size="310"
      style="max-width: 100%; height: auto"
      v-if="!isLoading && props.graph_items[0].value != 0"
    ></v-pie>
    <v-progress-circular
      color="secondary"
      indeterminate
      :size="300"
      :width="12"
      v-if="isLoading"
    >
      Loading...
    </v-progress-circular>
    <v-progress-circular
      color="accent"
      :size="300"
      :width="36"
      v-if="!isLoading && props.graph_items[0].value == 0"
    >
      None
    </v-progress-circular>
  </div>
</template>

<script setup>
  import { ref, defineProps, watch, computed } from "vue";
  import { useGraphsNew } from "@/composables/tagsComposable";
  import { useOptions } from "@/composables/optionsComposable";
  import { VPie } from "vuetify/labs/VPie";
  //import { useDisplay } from "vuetify";

  //const { width } = useDisplay();

  const numberFormatter = new Intl.NumberFormat("en", { useGrouping: true });
  function formatNumber(v) {
    return numberFormatter.format(v);
  }
  const { options: appOptions } = useOptions();
  const formData = ref(null);

  const props = defineProps({
    widget: {
      type: Number,
      default: 1,
    },
    position: {
      default: "right",
    },
    graph_items: {},
  });
  if (props.widget == 1) {
    formData.value = {
      graph_name: appOptions.widget1_graph_name,
      month: appOptions.widget1_month,
      tag_id: appOptions.widget1_tag_id,
      graph_type: appOptions.widget1_type ? appOptions.widget1_type.id : 1,
      exclude: appOptions.widget1_exclude
        ? JSON.parse(appOptions.widget1_exclude)
        : [],
    };
  }
  if (props.widget == 2) {
    formData.value = {
      graph_name: appOptions.widget2_graph_name,
      month: appOptions.widget2_month,
      tag_id: appOptions.widget2_tag_id,
      graph_type: appOptions.widget2_type ? appOptions.widget2_type.id : 1,
      exclude: appOptions.widget2_exclude
        ? JSON.parse(appOptions.widget2_exclude)
        : [],
    };
  }
  if (props.widget == 3) {
    formData.value = {
      graph_name: appOptions.widget3_graph_name,
      month: appOptions.widget3_month,
      tag_id: appOptions.widget3_tag_id,
      graph_type: appOptions.widget3_type ? appOptions.widget2_type.id : 1,
      exclude: appOptions.widget3_exclude
        ? JSON.parse(appOptions.widget3_exclude)
        : [],
    };
  }

  const { tag_graph_items, isLoading } = useGraphsNew(props.widget);
  const total = computed(() =>
    tag_graph_items.value.reduce((sum, n) => sum + parseFloat(n.value), 0),
  );

  // Populate formData once appOptions are loaded
  watch(
    appOptions,
    newOptions => {
      if (newOptions) {
        if (props.widget == 1) {
          formData.value = {
            graph_name: newOptions.widget1_graph_name,
            month: newOptions.widget1_month,
            tag_id: newOptions.widget1_tag_id,
            graph_type: newOptions.widget1_type
              ? newOptions.widget1_type.id
              : 1,
            exclude: newOptions.widget1_exclude
              ? JSON.parse(newOptions.widget1_exclude)
              : [],
          };
        }
        if (props.widget == 2) {
          formData.value = {
            graph_name: newOptions.widget2_graph_name,
            month: newOptions.widget2_month,
            tag_id: newOptions.widget2_tag_id,
            graph_type: newOptions.widget2_type
              ? newOptions.widget2_type.id
              : 1,
            exclude: newOptions.widget2_exclude
              ? JSON.parse(newOptions.widget2_exclude)
              : [],
          };
        }
        if (props.widget == 3) {
          formData.value = {
            graph_name: newOptions.widget3_graph_name,
            month: newOptions.widget3_month,
            tag_id: newOptions.widget3_tag_id,
            graph_type: newOptions.widget3_type
              ? newOptions.widget3_type.id
              : 1,
            exclude: newOptions.widget3_exclude
              ? JSON.parse(newOptions.widget3_exclude)
              : [],
          };
        }
      }
    },
    { immediate: true },
  );
</script>
