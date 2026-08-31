<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left d-flex align-center ga-2">
      <span class="text-subtitle-2 text-primary">Savings Plan</span>
      <v-chip v-if="plan && !isLoading" :color="statusColor" size="x-small" label>
        {{ statusLabel }}
      </v-chip>
      <v-spacer></v-spacer>
      <span
        v-if="plan && !isLoading"
        class="text-caption text-medium-emphasis"
      >
        {{ plan.paychecks_in_horizon }} paychecks to
        {{ plan.horizon_months }} months out
      </span>
    </v-card-title>

    <v-card-text v-if="isLoading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
      <div class="text-caption text-medium-emphasis mt-3">
        Projecting a year across every account…
      </div>
    </v-card-text>

    <v-card-text v-else-if="!plan" class="text-center py-8">
      <div class="text-body-2 text-medium-emphasis">No plan available.</div>
    </v-card-text>

    <v-card-text v-else class="ma-0 pa-0 ga-0">
      <!-- The headline: what the plan puts away, and the two figures that say
           whether that is comfortable or merely affordable. -->
      <v-container>
        <v-row dense>
          <v-col cols="12" sm="6" md="3">
            <div class="text-caption text-medium-emphasis">
              Allocates per paycheck
            </div>
            <div class="text-h6">
              <NumberFlow
                :value="Number(plan.planned_total)"
                :format="{ style: 'currency', currency: 'USD' }"
              />
            </div>
            <div class="text-caption" :class="deltaClass">
              {{ deltaLabel }}
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <template v-if="Number(plan.freed_per_paycheck) > 0">
              <div class="text-caption text-medium-emphasis">
                Going in that need not
              </div>
              <div class="text-h6 text-warning">
                {{ money(plan.freed_per_paycheck) }}
              </div>
              <div class="text-caption text-medium-emphasis">
                across {{ overfundedCount }}
                {{ overfundedCount === 1 ? "account" : "accounts" }}
              </div>
            </template>
            <template v-else>
              <div class="text-caption text-medium-emphasis">
                Minimums require
              </div>
              <div class="text-h6">{{ money(plan.minimums_total) }}</div>
              <div class="text-caption text-medium-emphasis">
                what every account must have
              </div>
            </template>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-caption text-medium-emphasis">
              No transfers needed up to
            </div>
            <div class="text-h6">
              {{ money(plan.path_capacity_per_paycheck) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              above this, money has to be moved across
            </div>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <div class="text-caption text-medium-emphasis">
              The year affords
            </div>
            <div class="text-h6">
              {{ money(plan.horizon_capacity_per_paycheck) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              past this it is unaffordable, not badly timed
            </div>
          </v-col>
        </v-row>
      </v-container>

      <!-- A structural breach means the plan does not work. Timing dips are
           not failures, so they are reported as the schedule below instead. -->
      <v-alert
        v-if="!plan.feasible"
        type="error"
        variant="tonal"
        density="compact"
        class="mx-4 mb-3"
      >
        There is no valid plan: the minimums exceed what the year affords.
      </v-alert>
      <v-alert
        v-else-if="!plan.verified"
        type="warning"
        variant="tonal"
        density="compact"
        class="mx-4 mb-3"
      >
        This plan leaves an account short in a way no transfer covers.
      </v-alert>

      <v-alert
        v-for="(note, i) in plan.notes"
        :key="i"
        type="info"
        variant="tonal"
        density="compact"
        class="mx-4 mb-2 text-body-2"
      >
        {{ note }}
      </v-alert>

      <!-- The allocation -->
      <v-data-table
        :headers="displayHeaders"
        :items="plan.lines"
        :items-length="plan.lines.length"
        item-value="contribution_id"
        density="compact"
        disable-sort
        hide-default-footer
        :items-per-page="-1"
        striped="odd"
        :hide-default-header="!mdAndUp"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        class="bg-background"
      >
        <template v-slot:[`item.contribution`]="{ item }">
          <div class="font-weight-bold">{{ item.contribution }}</div>
          <div class="text-caption text-medium-emphasis">
            {{ item.account_name ?? "no account" }}
          </div>
        </template>
        <template v-slot:[`item.current_per_paycheck`]="{ item }">
          <div class="text-center">{{ money(item.current_per_paycheck) }}</div>
        </template>
        <template v-slot:[`item.minimum_per_paycheck`]="{ item }">
          <div class="text-center">
            {{ money(item.minimum_per_paycheck) }}
            <v-tooltip
              v-if="!item.minimum_is_stated"
              text="Worked out from this account's budgets and dated bills"
              location="top"
            >
              <template v-slot:activator="{ props }">
                <v-icon
                  v-bind="props"
                  icon="mdi-function-variant"
                  size="x-small"
                  class="ml-1 text-medium-emphasis"
                ></v-icon>
              </template>
            </v-tooltip>
          </div>
        </template>
        <template v-slot:[`item.planned_per_paycheck`]="{ item }">
          <div class="text-center font-weight-bold">
            {{ money(item.planned_per_paycheck) }}
          </div>
          <div class="text-caption text-center" :class="lineDeltaClass(item)">
            {{ lineDelta(item) }}
          </div>
        </template>
        <template v-slot:[`item.reason`]="{ item }">
          <v-chip
            v-if="Number(item.freed_per_paycheck) > 0"
            color="warning"
            size="x-small"
            label
            class="mb-1"
          >
            can drop {{ money(item.freed_per_paycheck) }}
          </v-chip>
          <div class="text-caption">{{ item.reason }}</div>
          <div v-if="item.warning" class="text-caption text-warning">
            {{ item.warning }}
          </div>
        </template>
        <!-- Mobile view -->
        <template v-slot:[`item.mobile`]="{ item }">
          <div class="py-1">
            <div class="font-weight-bold text-primary">
              {{ item.contribution }}
              <span class="text-caption text-medium-emphasis">
                {{ item.account_name }}
              </span>
            </div>
            <div class="d-flex justify-space-between text-caption">
              <span>now {{ money(item.current_per_paycheck) }}</span>
              <span>min {{ money(item.minimum_per_paycheck) }}</span>
              <span class="font-weight-bold">
                plan {{ money(item.planned_per_paycheck) }}
              </span>
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ item.reason }}
            </div>
          </div>
        </template>
      </v-data-table>

      <!-- The bridging schedule. Half the plan: an allocation without the
           movements that make it survivable is only half an answer. -->
      <v-container v-if="plan.bridges.length">
        <div class="text-subtitle-2 font-weight-bold mb-1">
          Money to move across
        </div>
        <div class="text-caption text-medium-emphasis mb-2">
          Short gaps where the money exists but has not arrived yet. Each one
          goes back on the day checking recovers.
        </div>
        <v-list density="compact" class="bg-background rounded">
          <v-list-item
            v-for="(bridge, i) in plan.bridges"
            :key="i"
            :prepend-icon="
              bridge.shortfall > 0 ? 'mdi-alert-circle' : 'mdi-swap-horizontal'
            "
            :class="bridge.shortfall > 0 ? 'text-error' : ''"
          >
            <v-list-item-title class="text-body-2">
              {{ money(bridge.amount) }} by {{ bridge.when }}
              <span v-if="bridge.return_on" class="text-medium-emphasis">
                — back on {{ bridge.return_on }}
              </span>
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              {{ bridge.why }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-container>

      <!-- What would have to change when no plan works at all. -->
      <v-container v-if="plan.levers.length">
        <div class="text-subtitle-2 font-weight-bold mb-1">
          What would have to change
        </div>
        <v-list density="compact" class="bg-background rounded">
          <v-list-item v-for="(lever, i) in plan.levers" :key="i">
            <v-list-item-title class="text-body-2">
              {{ lever.what }} — {{ money(lever.amount_per_paycheck) }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              {{ lever.detail }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-container>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { computed } from "vue";
  import { useDisplay } from "vuetify";
  import NumberFlow from "@number-flow/vue";
  import { useSavingsPlan } from "@/composables/savingsPlanComposable";

  const { mdAndUp } = useDisplay();
  const { plan, isLoading } = useSavingsPlan();

  const money = value =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(Number(value ?? 0));

  const statusLabel = computed(() => {
    if (!plan.value) return "";
    if (!plan.value.feasible) return "no valid plan";
    if (!plan.value.verified) return "does not hold";
    if (plan.value.bridges.length)
      return `${plan.value.bridges.length} transfer${
        plan.value.bridges.length === 1 ? "" : "s"
      } needed`;
    return "verified";
  });

  const statusColor = computed(() => {
    if (!plan.value) return "surface";
    if (!plan.value.feasible || !plan.value.verified) return "error";
    if (plan.value.bridges.length) return "warning";
    return "success";
  });

  // Against what is actually being contributed today, which is the only
  // comparison that tells you whether to change anything.
  const deltaLabel = computed(() => {
    if (!plan.value) return "";
    const delta = Number(plan.value.planned_total - plan.value.current_total);
    if (Math.abs(delta) < 0.01) return "same as now";
    return `${delta > 0 ? "+" : ""}${money(delta)} vs now`;
  });

  const deltaClass = computed(() => {
    if (!plan.value) return "";
    const delta = Number(plan.value.planned_total - plan.value.current_total);
    if (Math.abs(delta) < 0.01) return "text-medium-emphasis";
    return delta > 0 ? "text-success" : "text-warning";
  });

  const lineDelta = item => {
    const delta = Number(item.planned_per_paycheck - item.current_per_paycheck);
    if (Math.abs(delta) < 0.01) return "unchanged";
    return `${delta > 0 ? "+" : ""}${money(delta)}`;
  };

  const lineDeltaClass = item => {
    const delta = Number(item.planned_per_paycheck - item.current_per_paycheck);
    if (Math.abs(delta) < 0.01) return "text-medium-emphasis";
    return delta > 0 ? "text-success" : "text-warning";
  };

  const headers = [
    { title: "Contribution", key: "contribution" },
    { title: "Now", key: "current_per_paycheck", width: "110px" },
    { title: "Minimum", key: "minimum_per_paycheck", width: "120px" },
    { title: "Plan", key: "planned_per_paycheck", width: "120px" },
    { title: "Why", key: "reason" },
  ];

  const overfundedCount = computed(
    () =>
      (plan.value?.lines ?? []).filter(
        line => Number(line.freed_per_paycheck) > 0,
      ).length,
  );

  const displayHeaders = computed(() =>
    mdAndUp.value ? headers : [{ title: "", key: "mobile" }],
  );
</script>
