<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left d-flex align-center ga-2">
      <span class="text-subtitle-2 text-primary">Savings Plan</span>
      <v-chip v-if="plan && !isLoading" :color="statusColor" size="x-small" label>
        {{ statusLabel }}
      </v-chip>
      <v-tooltip text="Add bucket" location="top" v-if="authStore.isFullAccess">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-pail-plus"
            flat
            variant="plain"
            size="small"
            v-bind="props"
            :disabled="!isOnline"
            @click="addDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
      <BucketForm
        v-model="addDialog"
        key="0"
        :isEdit="false"
        :passedFormData="blankBucket"
        @update-dialog="value => (addDialog = value)"
        @add-bucket="addBucket"
      />
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
            <div
              v-if="Number(plan.other_funding_total) > 0"
              class="text-caption text-medium-emphasis"
            >
              plus {{ money(plan.other_funding_total) }} the plan does not set
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
        :items="rows"
        :items-length="rows.length"
        item-value="bucket_id"
        density="compact"
        disable-sort
        hide-default-footer
        :items-per-page="-1"
        striped="odd"
        :hide-default-header="!mdAndUp"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        class="bg-background"
      >
        <template v-slot:[`item.bucket_name`]="{ item }">
          <div
            :class="
              item.active
                ? 'font-weight-bold'
                : 'font-italic text-warning text-decoration-line-through'
            "
          >
            {{ item.bucket_name }}
          </div>
          <div class="text-caption text-medium-emphasis">
            {{ item.account_name ?? "no account" }}
          </div>
        </template>
        <template v-slot:[`item.current_per_paycheck`]="{ item }">
          <div class="text-center">
            {{ money(item.current_per_paycheck ?? item.bucket.contribution_per_paycheck) }}
          </div>
          <!-- Money the plan does not set. Without it a bucket receiving
               362.77 reads as receiving 85. -->
          <div
            v-if="Number(item.other_funding_per_paycheck) > 0"
            class="text-caption text-center text-medium-emphasis"
          >
            +{{ money(item.other_funding_per_paycheck) }} elsewhere
          </div>
        </template>
        <template v-slot:[`item.minimum_per_paycheck`]="{ item }">
          <div class="text-center" v-if="!item.in_plan">—</div>
          <div class="text-center" v-else>
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
          <div class="text-center" v-if="!item.in_plan">—</div>
          <template v-else>
            <div class="text-center font-weight-bold">
              {{ money(item.planned_per_paycheck) }}
            </div>
            <div class="text-caption text-center" :class="lineDeltaClass(item)">
              {{ lineDelta(item) }}
            </div>
          </template>
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
          <div
            v-if="Number(item.rewards_expected) > 0"
            class="text-caption text-success"
          >
            <v-icon icon="mdi-gift-outline" size="x-small"></v-icon>
            {{ money(item.rewards_expected) }} of card rewards expected
            {{ item.rewards_on }}
          </div>
          <div
            v-if="Number(item.measured_per_year) > 0"
            class="text-caption text-medium-emphasis"
          >
            <v-icon icon="mdi-tag-outline" size="x-small"></v-icon>
            {{ money(item.measured_per_year) }} a year measured on
            {{ item.measured_tag_names.join(", ") }}
          </div>
          <div v-if="item.warning" class="text-caption text-warning">
            {{ item.warning }}
          </div>
          <div v-if="!item.in_plan" class="text-caption text-medium-emphasis">
            Inactive, so the plan does not fund it.
          </div>
          <!-- Whether this bucket has been set up at all. Silence used to mean
               both "configured" and "never looked at". -->
          <div
            v-else-if="item.coverage"
            class="text-caption"
            :class="
              Number(item.unbudgeted_per_year) > 0
                ? 'text-warning'
                : 'text-medium-emphasis'
            "
          >
            <v-icon
              :icon="
                item.claimed_tag_count
                  ? 'mdi-tag-multiple-outline'
                  : 'mdi-tag-off-outline'
              "
              size="x-small"
            ></v-icon>
            {{ item.coverage }}
          </div>
        </template>

        <!-- A bucket is edited where its plan is read, rather than from a
             second table of the same rows further down the page. -->
        <template v-slot:[`item.actions`]="{ item }">
          <div class="d-flex justify-end">
            <v-btn
              variant="plain"
              icon="mdi-pencil"
              size="small"
              density="comfortable"
              :disabled="!isOnline"
              @click="openEdit(item)"
            ></v-btn>
            <v-btn
              variant="plain"
              icon="mdi-delete"
              size="small"
              density="comfortable"
              color="error"
              :disabled="!isOnline"
              @click="openDelete(item)"
            ></v-btn>
          </div>
        </template>
        <!-- Mobile view -->
        <template v-slot:[`item.mobile`]="{ item }">
          <div class="py-1">
            <div
              class="text-primary"
              :class="
                item.active
                  ? 'font-weight-bold'
                  : 'font-italic text-decoration-line-through'
              "
            >
              {{ item.bucket_name }}
              <span class="text-caption text-medium-emphasis">
                {{ item.account_name }}
              </span>
            </div>
            <div class="d-flex justify-space-between text-caption">
              <span>
                now
                {{ money(item.current_per_paycheck ?? item.bucket.contribution_per_paycheck) }}
                <template v-if="Number(item.other_funding_per_paycheck) > 0">
                  +{{ money(item.other_funding_per_paycheck) }}
                </template>
              </span>
              <template v-if="item.in_plan">
                <span>min {{ money(item.minimum_per_paycheck) }}</span>
                <span class="font-weight-bold">
                  plan {{ money(item.planned_per_paycheck) }}
                </span>
              </template>
              <span v-else class="text-medium-emphasis">not in the plan</span>
            </div>
            <div class="text-caption text-medium-emphasis">
              {{ item.reason }}
            </div>
            <div v-if="authStore.isFullAccess" class="d-flex justify-end">
              <v-btn
                variant="plain"
                icon="mdi-pencil"
                size="small"
                density="comfortable"
                :disabled="!isOnline"
                @click="openEdit(item)"
              ></v-btn>
              <v-btn
                variant="plain"
                icon="mdi-delete"
                size="small"
                density="comfortable"
                color="error"
                :disabled="!isOnline"
                @click="openDelete(item)"
              ></v-btn>
            </div>
          </div>
        </template>
      </v-data-table>

      <!-- The emergency plan, derived rather than stored: what every bucket
           may not go below, and what cutting back to that would free. -->
      <div
        v-if="buckets"
        class="text-caption text-medium-emphasis text-right px-4 py-2"
      >
        Contributed now {{ money(buckets.per_paycheck_total) }} · in an
        emergency {{ money(buckets.emergency_paycheck_total) }} ·
        freeing {{ money(buckets.total_emergency) }}
      </div>

      <BucketForm
        v-if="editing"
        v-model="editDialog"
        :key="editing.id"
        :isEdit="true"
        :passedFormData="editing"
        @update-dialog="value => (editDialog = value)"
        @edit-bucket="editBucket"
      />

      <v-dialog v-model="deleteDialog" width="400">
        <v-card>
          <v-card-title>Delete bucket?</v-card-title>
          <v-card-text>
            <span>{{ editing?.name }}</span>
          </v-card-text>
          <v-card-actions>
            <v-btn @click="deleteDialog = false">Close</v-btn>
            <v-btn
              color="error"
              :disabled="!isOnline"
              @click="confirmDelete"
            >
              Delete
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Budgets are the only thing the plan acts on, so this is how twelve
           months of measured spending gets a say: accepting one changes a
           budget, and that changes the plan. -->
      <v-container v-if="plan.budget_suggestions.length">
        <div class="text-subtitle-2 font-weight-bold mb-1">
          Budgets worth revisiting
        </div>
        <div class="text-caption text-medium-emphasis mb-2">
          What the last twelve months say, against what the budgets say. The
          plan does not act on any of it until a budget changes.
        </div>
        <v-list density="compact" class="bg-background rounded">
          <v-list-item
            v-for="(suggestion, i) in plan.budget_suggestions"
            :key="i"
            :prepend-icon="suggestionIcon(suggestion.kind)"
          >
            <v-list-item-title class="text-body-2">
              <v-chip size="x-small" label class="mr-1">
                {{ suggestion.kind }}
              </v-chip>
              {{ suggestion.budget_name }}
              <span
                v-if="Number(suggestion.per_paycheck_effect) !== 0"
                class="text-medium-emphasis"
              >
                — about {{ money(suggestion.per_paycheck_effect) }} a paycheck
              </span>
            </v-list-item-title>
            <v-list-item-subtitle class="text-caption">
              {{ suggestion.why }}
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-container>

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
  import { computed, ref } from "vue";
  import { useDisplay } from "vuetify";
  import NumberFlow from "@number-flow/vue";
  import BucketForm from "@/components/BucketForm.vue";
  import { useSavingsPlan } from "@/composables/savingsPlanComposable";
  import { useBuckets } from "@/composables/bucketsComposable";
  import { useAuthStore } from "@/stores/auth";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";

  const { mdAndUp } = useDisplay();
  const authStore = useAuthStore();
  const { isOnline } = useOnlineStatus();
  const { plan, isLoading } = useSavingsPlan();
  const { buckets, addBucket, editBucket, removeBucket } = useBuckets();

  const addDialog = ref(false);
  const editDialog = ref(false);
  const deleteDialog = ref(false);
  const editing = ref(null);

  const blankBucket = {
    id: 0,
    name: null,
    contribution_per_paycheck: "0",
    // Null, not zero: blank means "work the minimum out from the budgets and
    // the dated bills", which is what most buckets want.
    minimum_per_paycheck: null,
    buffer: "0",
    target_balance: null,
    target_date: null,
    sweep: false,
    sweep_share: 1,
    priority: 100,
    lendable: true,
    receives_rewards: false,
    budget_ids: [],
    scope_tag_ids: [],
    scope_main_tag_ids: [],
    active: true,
    account_id: null,
    reminder_id: null,
  };

  // The rows are the *buckets*, annotated with what the plan says about each,
  // rather than the plan's lines. The plan only solves active buckets, so
  // driving the table from it would hide every inactive one — and with the
  // separate buckets table gone, hidden means unreachable: no way to open
  // Charity again once it is switched off.
  const rows = computed(() => {
    const lines = new Map(
      (plan.value?.lines ?? []).map(line => [line.bucket_id, line]),
    );
    return (buckets.value?.buckets ?? []).map(bucket => {
      const line = lines.get(bucket.id);
      return {
        ...(line ?? {}),
        bucket_id: bucket.id,
        bucket_name: bucket.name,
        active: bucket.active,
        in_plan: Boolean(line),
        reason: line?.reason ?? "",
        bucket,
      };
    });
  });

  const openEdit = row => {
    editing.value = row.bucket;
    editDialog.value = true;
  };

  const openDelete = row => {
    editing.value = row.bucket;
    deleteDialog.value = true;
  };

  const confirmDelete = () => {
    removeBucket(editing.value);
    deleteDialog.value = false;
  };

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

  const headers = computed(() => {
    const columns = [
      { title: "Bucket", key: "bucket_name" },
      { title: "Now", key: "current_per_paycheck", width: "110px" },
      { title: "Minimum", key: "minimum_per_paycheck", width: "120px" },
      { title: "Plan", key: "planned_per_paycheck", width: "120px" },
      { title: "Why", key: "reason" },
    ];
    if (authStore.isFullAccess) {
      columns.push({ title: "", key: "actions", width: "96px" });
    }
    return columns;
  });

  const suggestionIcon = kind =>
    ({
      raise: "mdi-arrow-up-bold-outline",
      lower: "mdi-arrow-down-bold-outline",
      create: "mdi-plus-box-outline",
      overlap: "mdi-vector-intersection",
    })[kind] ?? "mdi-information-outline";

  const overfundedCount = computed(
    () =>
      (plan.value?.lines ?? []).filter(
        line => Number(line.freed_per_paycheck) > 0,
      ).length,
  );

  const displayHeaders = computed(() =>
    mdAndUp.value ? headers.value : [{ title: "", key: "mobile" }],
  );
</script>
