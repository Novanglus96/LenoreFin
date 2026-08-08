<template>
  <v-dialog v-model="dialog" max-width="420" scrollable>
    <v-card>
      <v-card-title class="d-flex align-center ga-2 pt-4 px-4">
        <v-icon icon="mdi-view-dashboard-edit" color="primary" />
        Customize Dashboard
      </v-card-title>
      <v-card-subtitle class="px-4 pb-2">
        Toggle visibility and drag to reorder widgets
      </v-card-subtitle>
      <v-divider />
      <v-card-text class="px-2 py-2">
        <v-list density="compact">
          <v-list-item
            v-for="(widget, index) in localLayout"
            :key="widget.id"
            :class="['rounded', 'mb-1', widget.visible ? '' : 'text-disabled']"
            :base-color="widget.visible ? 'primary' : undefined"
          >
            <template v-slot:prepend>
              <v-icon :icon="widgetMeta[widget.id].icon" class="mr-2" />
            </template>
            <v-list-item-title>{{ widgetMeta[widget.id].label }}</v-list-item-title>
            <template v-slot:append>
              <div class="d-flex align-center ga-1">
                <v-btn
                  icon="mdi-chevron-up"
                  size="x-small"
                  variant="text"
                  :disabled="index === 0"
                  @click="moveUp(index)"
                />
                <v-btn
                  icon="mdi-chevron-down"
                  size="x-small"
                  variant="text"
                  :disabled="index === localLayout.length - 1"
                  @click="moveDown(index)"
                />
                <v-switch
                  v-model="widget.visible"
                  color="primary"
                  density="compact"
                  hide-details
                  class="ml-2"
                />
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-divider />
      <v-card-actions class="pa-3 ga-2">
        <v-btn variant="text" @click="reset">Reset to default</v-btn>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Cancel</v-btn>
        <v-btn color="primary" variant="tonal" @click="save">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
  import { ref, watch } from "vue";
  import { useDashboardConfig } from "@/composables/dashboardComposable";

  const props = defineProps({
    modelValue: Boolean,
  });
  const emit = defineEmits(["update:modelValue"]);

  const { dashboardConfig, saveLayout, DEFAULT_LAYOUT } = useDashboardConfig();

  const dialog = ref(props.modelValue);
  watch(
    () => props.modelValue,
    v => (dialog.value = v),
  );
  watch(dialog, v => emit("update:modelValue", v));

  const widgetMeta = {
    graphs: { label: "Graphs", icon: "mdi-chart-pie" },
    budgets: { label: "Budgets", icon: "mdi-wallet" },
    account_balances: { label: "Account Balances", icon: "mdi-star" },
    reminders: { label: "Reminders", icon: "mdi-bell" },
    transactions: { label: "Transactions", icon: "mdi-bank-transfer" },
  };

  const localLayout = ref([]);

  watch(
    dialog,
    open => {
      if (open) {
        localLayout.value = JSON.parse(
          JSON.stringify(dashboardConfig.value?.layout ?? DEFAULT_LAYOUT),
        );
      }
    },
    { immediate: true },
  );

  function moveUp(index) {
    if (index === 0) return;
    const arr = [...localLayout.value];
    [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]];
    localLayout.value = arr;
  }

  function moveDown(index) {
    if (index === localLayout.value.length - 1) return;
    const arr = [...localLayout.value];
    [arr[index], arr[index + 1]] = [arr[index + 1], arr[index]];
    localLayout.value = arr;
  }

  function reset() {
    localLayout.value = JSON.parse(JSON.stringify(DEFAULT_LAYOUT));
  }

  function save() {
    saveLayout(localLayout.value);
    dialog.value = false;
  }
</script>
