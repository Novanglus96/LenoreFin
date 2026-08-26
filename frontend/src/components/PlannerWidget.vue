<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left d-flex align-center flex-wrap ga-2">
      <span class="text-subtitle-2 text-primary">Savings Planner</span>
      <v-spacer></v-spacer>
      <v-select
        v-model="months"
        :items="windowOptions"
        item-title="title"
        item-value="value"
        density="compact"
        variant="outlined"
        hide-details
        label="History window"
        style="max-width: 180px"
      ></v-select>
      <v-tooltip
        text="Apply the suggested amount to the selected contributions"
        location="top"
        v-if="authStore.isFullAccess"
      >
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            color="primary"
            variant="tonal"
            size="small"
            prepend-icon="mdi-check-all"
            :disabled="selected.length === 0 || !isOnline || isApplying"
            :loading="isApplying"
            @click="confirmDialog = true"
          >
            Apply {{ selected.length ? `(${selected.length})` : "" }}
          </v-btn>
        </template>
      </v-tooltip>
    </v-card-title>

    <v-card-text class="ma-0 pa-0">
      <!-- Summary strip: what the plan costs now vs what it would cost. -->
      <v-container>
        <v-row dense align="center">
          <v-col cols="12" sm="4" class="text-center">
            <div class="text-caption text-medium-emphasis">
              Current per paycheck
            </div>
            <div class="text-body-1 font-weight-bold">
              {{ formatCurrency(planner?.current_per_paycheck_total ?? 0) }}
            </div>
          </v-col>
          <v-col cols="12" sm="4" class="text-center">
            <div class="text-caption text-medium-emphasis">
              Suggested per paycheck
            </div>
            <div class="text-body-1 font-weight-bold">
              {{ formatCurrency(planner?.suggested_per_paycheck_total ?? 0) }}
            </div>
          </v-col>
          <v-col cols="12" sm="4" class="text-center">
            <div class="text-caption text-medium-emphasis">Change</div>
            <div
              class="text-body-1 font-weight-bold"
              :class="deltaClass(planner?.delta_per_paycheck_total)"
            >
              {{ formatDelta(planner?.delta_per_paycheck_total ?? 0) }}
            </div>
          </v-col>
        </v-row>
      </v-container>

      <v-data-table
        :headers="headers"
        :items="rows"
        :loading="isLoading || isFetching"
        item-value="contribution_id"
        v-model="selected"
        :show-select="authStore.isFullAccess"
        :item-selectable="row => Boolean(row.suggestion?.achievable)"
        no-data-text="No contributions to plan yet."
        loading-text="Analysing accounts..."
        disable-sort
        density="compact"
        striped="odd"
        class="bg-background"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
      >
        <template v-slot:[`item.contribution`]="{ item }">
          <div class="d-flex flex-column py-1">
            <span class="font-weight-medium">{{ item.contribution }}</span>
            <span class="text-caption text-medium-emphasis">
              {{ item.account_name ?? "No account linked" }}
            </span>
          </div>
        </template>

        <template v-slot:[`item.goal_type`]="{ item }">
          <v-chip size="x-small" :color="goalColor(item.goal_type)" variant="tonal">
            {{ goalLabel(item.goal_type) }}
          </v-chip>
        </template>

        <template v-slot:[`item.trend`]="{ item }">
          <div v-if="item.trend" class="text-center">
            <span :class="deltaClass(item.trend.natural_flow_per_month)">
              {{ formatDelta(item.trend.natural_flow_per_month) }}/mo
            </span>
            <!-- r² is the honesty column: a low fit means lumpy history, and
                 the suggestion built on it deserves less trust. -->
            <v-tooltip
              :text="`Fit r² ${item.trend.r_squared} over ${item.trend.data_points} transactions`"
              location="top"
            >
              <template v-slot:activator="{ props }">
                <v-icon
                  v-bind="props"
                  size="x-small"
                  class="ms-1"
                  :color="item.trend.r_squared < 0.5 ? 'warning' : 'medium-emphasis'"
                  icon="mdi-information-outline"
                ></v-icon>
              </template>
            </v-tooltip>
          </div>
          <span v-else class="text-caption text-medium-emphasis">—</span>
        </template>

        <template v-slot:[`item.current`]="{ item }">
          <div class="text-center">
            {{ formatCurrency(item.suggestion?.current_per_paycheck ?? 0) }}
            <!-- Drift: the plan and the reminder disagree. null means no
                 reminder is linked, which is not the same as zero drift. -->
            <v-tooltip
              v-if="item.drift !== null && Number(item.drift) !== 0"
              :text="`The linked reminder moves ${formatCurrency(
                Number(item.suggestion?.current_per_paycheck ?? 0) - Number(item.drift),
              )}, not this`"
              location="top"
            >
              <template v-slot:activator="{ props }">
                <v-icon
                  v-bind="props"
                  size="x-small"
                  class="ms-1"
                  color="warning"
                  icon="mdi-alert-circle-outline"
                ></v-icon>
              </template>
            </v-tooltip>
          </div>
        </template>

        <template v-slot:[`item.suggested`]="{ item }">
          <div class="text-center" v-if="item.suggestion">
            <span class="font-weight-bold">
              {{ formatCurrency(item.suggestion.required_per_paycheck) }}
            </span>
          </div>
          <span v-else class="text-caption text-medium-emphasis">—</span>
        </template>

        <template v-slot:[`item.delta`]="{ item }">
          <div class="text-center" v-if="item.suggestion">
            <span :class="deltaClass(item.suggestion.delta_per_paycheck, true)">
              {{ formatDelta(item.suggestion.delta_per_paycheck) }}
            </span>
          </div>
          <span v-else class="text-caption text-medium-emphasis">—</span>
        </template>

        <template v-slot:[`item.why`]="{ item }">
          <div class="text-caption text-medium-emphasis py-1">
            {{ item.suggestion?.reason ?? item.note ?? "—" }}
            <div v-if="item.suggestion?.warning" class="text-warning">
              {{ item.suggestion.warning }}
            </div>
          </div>
        </template>
      </v-data-table>
    </v-card-text>

    <v-dialog v-model="confirmDialog" width="480">
      <v-card>
        <v-card-title>Apply suggestions?</v-card-title>
        <v-card-text>
          <p class="mb-2">
            This updates
            {{ selected.length }} contribution{{ selected.length === 1 ? "" : "s" }}
            and the recurring transfer{{ selected.length === 1 ? "" : "s" }} behind
            {{ selected.length === 1 ? "it" : "them" }}.
          </p>
          <p class="text-caption text-medium-emphasis">
            Your per-paycheck total changes by
            {{ formatDelta(selectedDelta) }}.
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="confirmDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="tonal"
            :loading="isApplying"
            :disabled="!isOnline"
            @click="doApply"
          >
            Apply
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
  import { ref, computed } from "vue";
  import { usePlanner } from "@/composables/plannerComposable";
  import { useAuthStore } from "@/stores/auth";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";

  const { isOnline } = useOnlineStatus();
  const authStore = useAuthStore();

  const months = ref(6);
  const selected = ref([]);
  const confirmDialog = ref(false);

  const windowOptions = [
    { title: "Last 3 months", value: 3 },
    { title: "Last 6 months", value: 6 },
    { title: "Last 12 months", value: 12 },
  ];

  const { planner, isLoading, isFetching, isApplying, applySuggestions } =
    usePlanner(months);

  const rows = computed(() => planner.value?.rows ?? []);

  const headers = [
    { title: "Contribution", key: "contribution" },
    { title: "Goal", key: "goal_type", align: "center" },
    { title: "Trend", key: "trend", align: "center" },
    { title: "Now", key: "current", align: "center" },
    { title: "Suggested", key: "suggested", align: "center" },
    { title: "Change", key: "delta", align: "center" },
    { title: "Why", key: "why" },
  ];

  // Only rows the user actually ticked, so the confirm dialog quotes the real
  // figure rather than the whole-table total.
  const selectedDelta = computed(() =>
    rows.value
      .filter(r => selected.value.includes(r.contribution_id))
      .reduce((sum, r) => sum + Number(r.suggestion?.delta_per_paycheck ?? 0), 0),
  );

  const goalLabels = {
    none: "None",
    hold: "Hold steady",
    target: "Target",
    floor: "Floor",
    grow: "Grow",
  };

  const goalColors = {
    none: "medium-emphasis",
    hold: "primary",
    target: "info",
    floor: "warning",
    grow: "success",
  };

  const goalLabel = key => goalLabels[key] ?? key;
  const goalColor = key => goalColors[key] ?? "primary";

  const formatCurrency = value =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(Number(value ?? 0));

  const formatDelta = value => {
    const n = Number(value ?? 0);
    return `${n > 0 ? "+" : ""}${formatCurrency(n)}`;
  };

  // For a trend, negative is bad. For a suggested change, a rise is simply
  // what the goal costs — not an error — so it reads neutral-positive.
  const deltaClass = (value, isChange = false) => {
    const n = Number(value ?? 0);
    if (n === 0) return "";
    if (isChange) return n > 0 ? "text-info" : "text-success";
    return n > 0 ? "text-success" : "text-error";
  };

  async function doApply() {
    await applySuggestions([...selected.value]);
    selected.value = [];
    confirmDialog.value = false;
  }
</script>
