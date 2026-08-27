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
        style="max-width: 165px"
      ></v-select>
      <v-select
        v-model="horizonMonths"
        :items="horizonOptions"
        item-title="title"
        item-value="value"
        density="compact"
        variant="outlined"
        hide-details
        label="Plan ahead"
        style="max-width: 150px"
      ></v-select>
      <v-text-field
        v-model.number="incomeAdjustment"
        density="compact"
        variant="outlined"
        hide-details
        label="Pay change"
        type="number"
        step="5"
        prefix="$"
        suffix="/pc"
        style="max-width: 145px"
      ></v-text-field>
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
      <!-- Summary strip: what is really being put aside now, what the plan
           allocates, and the difference. The baseline is the *effective*
           figure — scheduled transfers plus the top-ups being made by hand —
           because comparing against the scheduled amount alone counts money
           already going in as money still to be found. -->
      <v-container>
        <v-row dense align="center">
          <v-col cols="12" sm="4" class="text-center">
            <div class="text-caption text-medium-emphasis">
              Putting aside now
            </div>
            <div class="text-body-1 font-weight-bold">
              {{ formatCurrency(planner?.effective_per_paycheck_total ?? 0) }}
            </div>
            <div
              v-if="topupTotal !== 0"
              class="text-caption text-medium-emphasis"
            >
              {{ formatCurrency(planner?.current_per_paycheck_total ?? 0) }}
              scheduled + {{ formatCurrency(topupTotal) }} by hand
            </div>
          </v-col>
          <v-col cols="12" sm="4" class="text-center">
            <div class="text-caption text-medium-emphasis">Plan allocates</div>
            <div class="text-body-1 font-weight-bold">
              {{ formatCurrency(allocation?.allocated_total ?? 0) }}
            </div>
            <div v-if="allocation" class="text-caption text-medium-emphasis">
              {{ formatCurrency(allocation.obligations_total) }} of it is fixed
            </div>
          </v-col>
          <v-col cols="12" sm="4" class="text-center">
            <div class="text-caption text-medium-emphasis">Net change</div>
            <div
              class="text-body-1 font-weight-bold"
              :class="deltaClass(allocation?.net_change_total)"
            >
              {{ formatDelta(allocation?.net_change_total ?? 0) }}
            </div>
            <div class="text-caption text-medium-emphasis">
              mostly a reshuffle
            </div>
          </v-col>
        </v-row>
      </v-container>

      <!-- Headroom: whether the plan actually fits in a pay period. A raise is
           an input rather than something inferred — with more than one earner
           the per-cheque noise dwarfs a typical raise, so there is nothing in
           history to detect it from. -->
      <v-alert
        v-if="headroom && headroom.allocatable_per_paycheck !== null"
        :type="headroom.affordable ? 'success' : 'warning'"
        variant="tonal"
        density="compact"
        class="mx-4 mb-3"
      >
        <div class="d-flex flex-wrap ga-4 align-center text-body-2">
          <span>
            <!-- Capacity, not take-home. The funding account is a hub, so most
                 of what passes through it is money going out to buckets and
                 coming back to pay the bills those buckets exist for. -->
            To allocate
            <strong>
              {{ formatCurrency(headroom.allocatable_per_paycheck) }}
            </strong>
            <v-tooltip
              location="top"
              :text="
                `Putting aside today ${formatCurrency(
                  planner?.effective_per_paycheck_total,
                )} ${Number(headroom.funding_account_drift) < 0 ? 'less' : 'plus'} ${formatCurrency(
                  Math.abs(Number(headroom.funding_account_drift)),
                )} of funding-account drift` +
                (Number(headroom.forward_reminder_change) !== 0
                  ? `, ${Number(headroom.forward_reminder_change) < 0 ? 'less' : 'plus'} ${formatCurrency(
                      Math.abs(Number(headroom.forward_reminder_change)),
                    )} as commitments start and end`
                  : '') +
                (Number(headroom.income_adjustment) !== 0
                  ? `, plus ${formatCurrency(headroom.income_adjustment)} stated pay change`
                  : '') +
                (headroom.net_per_paycheck
                  ? `. Take-home is ${formatCurrency(headroom.net_per_paycheck)}, but bills paid straight from checking never reach a bucket.`
                  : '')
              "
            >
              <template v-slot:activator="{ props }">
                <v-icon
                  v-bind="props"
                  size="x-small"
                  class="ms-1"
                  icon="mdi-information-outline"
                ></v-icon>
              </template>
            </v-tooltip>
          </span>
          <span>
            Unallocated now
            <strong>{{ formatCurrency(headroom.headroom_now) }}</strong>
          </span>
          <span>
            Left if applied
            <strong :class="headroom.affordable ? '' : 'text-error'">
              {{ formatCurrency(headroom.headroom_if_applied) }}
            </strong>
          </span>
          <span
            v-if="allocation && allocation.feasible === false"
            class="font-weight-medium"
          >
            Fixed obligations alone are
            {{ formatCurrency(allocation.shortfall) }} over capacity — moving
            money between buckets cannot fix this one.
          </span>
        </div>
      </v-alert>
      <v-alert
        v-else-if="headroom && headroom.note"
        type="info"
        variant="tonal"
        density="compact"
        class="mx-4 mb-3"
        :text="headroom.note"
      ></v-alert>

      <!-- The actionable answer. "Move 122 from Reno to Ellie" is a sentence
           someone can act on; a column of deltas is a table they have to solve
           themselves. -->
      <v-alert
        v-if="allocation?.moves?.length"
        type="info"
        variant="tonal"
        density="compact"
        class="mx-4 mb-3"
      >
        <div class="text-body-2 font-weight-medium mb-1">
          Rebalance {{ allocation.moves.length }}
          {{ allocation.moves.length === 1 ? "transfer" : "transfers" }}
        </div>
        <div class="d-flex flex-column ga-1">
          <div
            v-for="(move, i) in allocation.moves"
            :key="i"
            class="text-body-2 d-flex align-center ga-1 flex-wrap"
          >
            <strong>{{ formatCurrency(move.amount_per_paycheck) }}</strong>
            <span class="text-medium-emphasis">a paycheck from</span>
            <span class="font-weight-medium">{{ move.from_contribution }}</span>
            <v-icon size="x-small" icon="mdi-arrow-right"></v-icon>
            <span class="font-weight-medium">{{ move.to_contribution }}</span>
          </div>
        </div>
        <!-- Moves only ever pair a giver with a taker, so an across-the-board
             change leaves a remainder they cannot show. -->
        <div
          v-if="Number(allocation.net_change_total) !== 0"
          class="text-caption text-medium-emphasis mt-2"
        >
          Overall the plan
          {{ Number(allocation.net_change_total) < 0 ? "shrinks" : "grows" }} by
          {{ formatCurrency(Math.abs(Number(allocation.net_change_total))) }}
          a paycheck on top of these moves.
        </div>
      </v-alert>
      <v-alert
        v-else-if="allocation?.note && allocation.feasible !== false"
        type="info"
        variant="tonal"
        density="compact"
        class="mx-4 mb-3"
        :text="allocation.note"
      ></v-alert>

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
          <v-chip
            size="x-small"
            :color="goalColor(item.goal_type)"
            variant="tonal"
          >
            {{ goalLabel(item.goal_type) }}
          </v-chip>
        </template>

        <template v-slot:[`item.trend`]="{ item }">
          <div v-if="item.trend" class="text-center">
            <!-- Per paycheck, not per month: every other figure in this table
                 is per paycheck, and that is the cadence the money moves in. -->
            <span :class="deltaClass(item.trend.projected_flow_per_paycheck)">
              {{ formatDelta(item.trend.projected_flow_per_paycheck) }}
            </span>
            <!-- The breakdown matters: "scheduled" comes from the forecast, so
                 annual and quarterly obligations are weighted by their real
                 dates rather than by whether they happened to fall inside the
                 history window. r² speaks only to the ad-hoc half. -->
            <v-tooltip
              :text="
                `Per paycheck: scheduled ${item.trend.scheduled_flow_per_paycheck} + ad-hoc ${item.trend.adhoc_flow_per_paycheck}` +
                ` (${item.trend.projected_flow_per_month}/mo over ${item.trend.paychecks_in_horizon} paychecks)` +
                ` · low point ${item.trend.projected_low_balance} in ${item.trend.paychecks_to_low} paychecks` +
                ` · suggested floor ${item.trend.suggested_floor}` +
                (Number(item.trend.one_off_total) !== 0
                  ? ` · ${item.trend.one_off_total} of one-offs excluded`
                  : '') +
                ` · fit r² ${item.trend.r_squared} over ${item.trend.data_points} transactions`
              "
              location="top"
            >
              <template v-slot:activator="{ props }">
                <v-icon
                  v-bind="props"
                  size="x-small"
                  class="ms-1"
                  :color="
                    item.trend.r_squared < 0.5 ? 'warning' : 'medium-emphasis'
                  "
                  icon="mdi-information-outline"
                ></v-icon>
              </template>
            </v-tooltip>
          </div>
          <span v-else class="text-caption text-medium-emphasis">—</span>
        </template>

        <template v-slot:[`item.current`]="{ item }">
          <div class="text-center">
            <!-- The effective figure: scheduled plus what is being topped up by
                 hand. A contribution with no goal has no suggestion but is
                 still costing money, so this comes off the row, not the
                 suggestion. -->
            {{ formatCurrency(item.effective_per_paycheck) }}
            <div
              v-if="Number(item.topup_per_paycheck) !== 0"
              class="text-caption text-medium-emphasis"
            >
              {{ formatCurrency(item.current_per_paycheck) }} +
              {{ formatCurrency(item.topup_per_paycheck) }} by hand
            </div>
            <!-- Drift: the plan and the reminder disagree. null means no
                 reminder is linked, which is not the same as zero drift. -->
            <v-tooltip
              v-if="item.drift !== null && Number(item.drift) !== 0"
              :text="`The linked reminder moves ${formatCurrency(
                Number(item.current_per_paycheck) - Number(item.drift),
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
              {{ formatCurrency(item.allocated_per_paycheck) }}
            </span>
            <!-- What it asked for, when the pot could not stretch that far. The
                 gap is the point: it says this bucket was rationed, not that
                 the goal was wrong. -->
            <v-tooltip
              v-if="
                Number(item.suggestion.required_per_paycheck) !==
                Number(item.allocated_per_paycheck)
              "
              location="top"
              :text="`Asked for ${formatCurrency(
                item.suggestion.required_per_paycheck,
              )}; ${formatCurrency(item.minimum_per_paycheck)} of this bucket is fixed obligations`"
            >
              <template v-slot:activator="{ props }">
                <v-icon
                  v-bind="props"
                  size="x-small"
                  class="ms-1"
                  color="medium-emphasis"
                  icon="mdi-scale-balance"
                ></v-icon>
              </template>
            </v-tooltip>
          </div>
          <span v-else class="text-caption text-medium-emphasis">
            {{ item.goal_type === "none" ? "no goal" : "—" }}
          </span>
        </template>

        <template v-slot:[`item.delta`]="{ item }">
          <div class="text-center" v-if="item.suggestion">
            <!-- Against effective funding, so an over-topped bucket reads as a
                 source of money rather than as already correct. -->
            <span :class="deltaClass(item.move_per_paycheck, true)">
              {{ formatDelta(item.move_per_paycheck) }}
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
            {{ selected.length }} contribution{{
              selected.length === 1 ? "" : "s"
            }}
            and the recurring transfer{{
              selected.length === 1 ? "" : "s"
            }}
            behind {{ selected.length === 1 ? "it" : "them" }}.
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
  const horizonMonths = ref(12);
  const incomeAdjustment = ref(0);
  const selected = ref([]);
  const confirmDialog = ref(false);

  const windowOptions = [
    { title: "Last 3 months", value: 3 },
    { title: "Last 6 months", value: 6 },
    { title: "Last 12 months", value: 12 },
  ];
  const horizonOptions = [
    { title: "6 mo (~13 pc)", value: 6 },
    { title: "1 yr (~26 pc)", value: 12 },
    { title: "2 yr (~52 pc)", value: 24 },
  ];

  const { planner, isLoading, isFetching, isApplying, applySuggestions } =
    usePlanner(months, horizonMonths, incomeAdjustment);

  const rows = computed(() => planner.value?.rows ?? []);
  const headroom = computed(() => planner.value?.headroom ?? null);
  const allocation = computed(() => planner.value?.allocation ?? null);

  // Top-ups across every bucket: the funding that was happening but never
  // appeared in a plan.
  const topupTotal = computed(() =>
    rows.value.reduce((sum, r) => sum + Number(r.topup_per_paycheck ?? 0), 0),
  );

  const headers = [
    { title: "Contribution", key: "contribution" },
    { title: "Goal", key: "goal_type", align: "center" },
    { title: "Projected/pc", key: "trend", align: "center" },
    { title: "Putting in", key: "current", align: "center" },
    { title: "Allocated", key: "suggested", align: "center" },
    { title: "Move", key: "delta", align: "center" },
    { title: "Why", key: "why" },
  ];

  // Only rows the user actually ticked, so the confirm dialog quotes the real
  // figure rather than the whole-table total.
  const selectedDelta = computed(() =>
    rows.value
      .filter(r => selected.value.includes(r.contribution_id))
      // The scheduled transfer is what "apply" rewrites, so the dialog quotes
      // the change to that — not the change against effective funding, which
      // includes top-ups that applying does not touch.
      .reduce(
        (sum, r) => sum + Number(r.suggestion?.delta_per_paycheck ?? 0),
        0,
      ),
  );

  const goalLabels = {
    none: "None",
    hold: "Obligations",
    target: "Target",
    floor: "Floor",
    grow: "Grow",
    budget: "Budget",
    maximise: "Leftover",
  };

  const goalColors = {
    none: "medium-emphasis",
    hold: "primary",
    target: "info",
    floor: "warning",
    grow: "success",
    budget: "info",
    maximise: "secondary",
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
