<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <!-- ── Header: window, verdict, totals, accept ───────────────────── -->
    <v-card-title class="d-flex flex-wrap align-center ga-2">
      <span class="text-subtitle-1 text-primary">Savings plan</span>
      <v-chip
        v-if="plan && !plan.error"
        :color="verdictColor(plan.verdict)"
        size="small"
        variant="flat"
        data-testid="plan-verdict"
      >
        {{ verdictLabel(plan.verdict) }}
      </v-chip>
      <v-progress-circular
        v-if="isFetching"
        indeterminate
        size="16"
        width="2"
        color="primary"
      />
      <v-spacer />
      <v-select
        v-model="planWindow.start"
        :items="startOptions"
        label="First paycheck"
        density="compact"
        hide-details
        style="max-width: 190px"
        data-testid="window-start"
      />
      <v-select
        v-model="planWindow.end"
        :items="endOptions"
        label="Through"
        density="compact"
        hide-details
        style="max-width: 190px"
        data-testid="window-end"
      />
    </v-card-title>

    <v-card-text v-if="isLoading && !plan" class="text-center pa-8">
      <v-progress-circular indeterminate color="primary" />
      <div class="text-caption mt-2">Forecasting every bucket…</div>
    </v-card-text>

    <v-card-text v-else-if="plan?.error">
      <v-alert type="info" variant="tonal">{{ plan.error }}</v-alert>
    </v-card-text>

    <template v-else-if="plan">
      <v-card-text class="pb-0">
        <v-row dense>
          <v-col cols="12" md="4">
            <div class="text-caption text-medium-emphasis">Per paycheck</div>
            <div class="text-h6" data-testid="plan-total">
              {{ money(plan.total_planned_per_paycheck) }}
              <span
                v-if="totalDelta !== 0"
                class="text-body-2"
                :class="totalDelta > 0 ? 'text-warning' : 'text-success'"
              >
                ({{ totalDelta > 0 ? "+" : "" }}{{ money(totalDelta) }})
              </span>
            </div>
            <div class="text-caption text-medium-emphasis">
              now {{ money(plan.total_current_per_paycheck) }} ·
              {{ plan.window.paydays }} paychecks · changes start
              {{ niceDate(plan.window.first_transfer) }}
            </div>
            <div class="text-caption mt-2">{{ verdictExplain }}</div>
            <div class="d-flex flex-wrap ga-2 mt-3">
              <v-btn
                v-if="authStore.isFullAccess"
                color="primary"
                variant="flat"
                size="small"
                :disabled="!canAccept"
                :loading="accepting"
                data-testid="plan-accept"
                @click="confirmAccept = true"
              >
                Accept plan
              </v-btn>
              <v-btn
                variant="text"
                size="small"
                :disabled="!hasEdits"
                data-testid="plan-reset"
                @click="resetEdits"
              >
                Reset changes
              </v-btn>
            </div>
            <div
              v-if="lastAccepted"
              class="text-caption text-medium-emphasis mt-2"
              data-testid="plan-last-accepted"
            >
              Last accepted {{ niceDate(lastAccepted.accepted_on) }}
              <span
                v-if="lastAccepted.verdict === 'insolvent'"
                class="text-warning"
              >
                (overridden: not solvent)
              </span>
              <v-btn
                v-if="authStore.isFullAccess && !lastAccepted.imported"
                variant="text"
                size="x-small"
                color="warning"
                @click="confirmUndo = true"
              >
                Undo
              </v-btn>
            </div>
          </v-col>
          <v-col cols="12" md="8">
            <div class="text-caption text-medium-emphasis">
              {{ plan.funding?.account_name }} — lowest
              <span
                :class="
                  Number(plan.funding?.low_balance) < 0 ? 'text-error' : ''
                "
              >
                {{ money(plan.funding?.low_balance) }}
              </span>
              on {{ niceDate(plan.funding?.low_when) }}
            </div>
            <ApexChart
              type="line"
              height="200"
              :options="fundingChartOptions"
              :series="fundingSeries"
              aria-label="Funding account forecast"
            />
          </v-col>
        </v-row>
      </v-card-text>

      <!-- ── Buckets ──────────────────────────────────────────────────── -->
      <v-card-text>
        <div class="d-flex align-center mb-1">
          <span class="text-subtitle-2">Buckets</span>
          <v-spacer />
          <v-btn
            v-if="authStore.isFullAccess"
            size="small"
            variant="text"
            prepend-icon="mdi-plus"
            data-testid="plan-add-bucket"
            @click="openDraft()"
          >
            Add bucket
          </v-btn>
        </div>
        <v-table density="compact" class="plan-table">
          <thead>
            <tr>
              <th>Bucket</th>
              <th class="text-right">Now</th>
              <th class="text-right">Planned</th>
              <th v-if="mdAndUp">Goal</th>
              <th v-if="mdAndUp">By</th>
              <th v-if="mdAndUp">Year</th>
              <th v-if="mdAndUp">Outlook</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="row in plan.buckets" :key="row.key">
              <tr
                :class="{ 'plan-row-removed': row.removed }"
                :data-testid="`plan-row-${row.name}`"
              >
                <td>
                  <div class="font-weight-medium">
                    {{ row.name }}
                    <v-chip v-if="row.is_new" size="x-small" color="info">
                      new
                    </v-chip>
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ row.account_name || "No account linked" }}
                  </div>
                </td>
                <td class="text-right">
                  {{ money(row.current_per_paycheck) }}
                </td>
                <td class="text-right" style="width: 120px">
                  <v-text-field
                    v-if="!row.removed && authStore.isFullAccess"
                    :model-value="fieldOf(row, 'per_paycheck')"
                    type="number"
                    min="0"
                    step="5"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="plan-input"
                    :data-testid="`plan-amount-${row.name}`"
                    @update:model-value="v => setField(row, 'per_paycheck', v)"
                  />
                  <span v-else>{{ money(row.planned_per_paycheck) }}</span>
                </td>
                <td v-if="mdAndUp" style="width: 120px">
                  <v-text-field
                    v-if="!row.removed && authStore.isFullAccess"
                    :model-value="fieldOf(row, 'goal_amount')"
                    type="number"
                    min="0"
                    placeholder="none"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="plan-input"
                    @update:model-value="v => setField(row, 'goal_amount', v)"
                  />
                </td>
                <td v-if="mdAndUp" style="width: 150px">
                  <v-text-field
                    v-if="
                      !row.removed &&
                      authStore.isFullAccess &&
                      fieldOf(row, 'goal_amount')
                    "
                    :model-value="fieldOf(row, 'goal_date')"
                    type="date"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="plan-input plan-input-date"
                    @update:model-value="v => setField(row, 'goal_date', v)"
                  />
                </td>
                <td v-if="mdAndUp">
                  <PlanSparkline
                    v-if="row.path?.length"
                    :path="row.path"
                    :current="row.current_path"
                    :label="`${row.name}: lowest ${money(row.low_balance)}`"
                  />
                </td>
                <td v-if="mdAndUp" style="min-width: 200px">
                  <BucketOutlook
                    :row="row"
                    :first-transfer="plan.window.first_transfer"
                  />
                </td>
                <td class="text-no-wrap">
                  <template v-if="authStore.isFullAccess">
                    <v-btn
                      v-if="isEdited(row)"
                      icon="mdi-restore"
                      size="x-small"
                      variant="text"
                      color="warning"
                      :aria-label="`Revert ${row.name}`"
                      :data-testid="`plan-revert-${row.name}`"
                      @click="revertRow(row)"
                    />
                    <v-btn
                      v-if="!row.is_new"
                      icon="mdi-pencil"
                      size="x-small"
                      variant="text"
                      :aria-label="`Set up ${row.name}`"
                      @click="editBucket(row.bucket_id)"
                    />
                    <v-btn
                      :icon="row.removed ? 'mdi-undo' : 'mdi-close'"
                      size="x-small"
                      variant="text"
                      :aria-label="
                        row.removed ? `Keep ${row.name}` : `Remove ${row.name}`
                      "
                      @click="toggleRemove(row)"
                    />
                  </template>
                </td>
              </tr>
              <!-- On a phone the graph and outlook get a line of their own. -->
              <tr v-if="!mdAndUp" :class="{ 'plan-row-removed': row.removed }">
                <td colspan="4" class="pb-3">
                  <div class="d-flex ga-3 align-start">
                    <PlanSparkline
                      v-if="row.path?.length"
                      :path="row.path"
                      :current="row.current_path"
                      :width="120"
                      :label="`${row.name}: lowest ${money(row.low_balance)}`"
                    />
                    <BucketOutlook
                      :row="row"
                      :first-transfer="plan.window.first_transfer"
                    />
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </v-table>
      </v-card-text>

      <!-- ── Overage order ───────────────────────────────────────────── -->
      <v-card-text>
        <div class="text-subtitle-2">Where extra money goes</div>
        <div class="text-caption text-medium-emphasis mb-2">
          The order a windfall is split in, after any bucket that is not solvent
          has been topped up back to zero. A bucket takes what its goal still
          needs unless you set a cap; one with no goal and no cap takes the
          rest. Saved when you accept.
        </div>
        <v-list density="compact" class="bg-transparent py-0">
          <v-list-item
            v-for="(rule, i) in rules"
            :key="rule.key"
            class="px-0"
            :data-testid="`overage-${rule.name}`"
          >
            <template #prepend>
              <span class="text-caption mr-3">{{ i + 1 }}.</span>
            </template>
            <v-list-item-title>{{ rule.name }}</v-list-item-title>
            <v-list-item-subtitle>
              <template v-if="rule.shortfall === null">
                No goal — takes the remainder
              </template>
              <template v-else-if="Number(rule.shortfall) > 0">
                Needs {{ money(rule.shortfall) }}
              </template>
              <template v-else>Goal met under this plan</template>
            </v-list-item-subtitle>
            <template #append>
              <v-text-field
                v-if="authStore.isFullAccess"
                :model-value="rule.cap_amount"
                type="number"
                min="0"
                placeholder="calculated"
                label="Cap"
                density="compact"
                variant="outlined"
                hide-details
                style="width: 120px"
                class="mr-1"
                @update:model-value="v => setCap(rule.key, v)"
              />
              <v-btn
                icon="mdi-arrow-up"
                size="x-small"
                variant="text"
                :disabled="i === 0"
                @click="move(i, -1)"
              />
              <v-btn
                icon="mdi-arrow-down"
                size="x-small"
                variant="text"
                :disabled="i === rules.length - 1"
                @click="move(i, 1)"
              />
              <v-btn
                icon="mdi-close"
                size="x-small"
                variant="text"
                :aria-label="`Drop ${rule.name} from the order`"
                @click="dropRule(i)"
              />
            </template>
          </v-list-item>
        </v-list>
        <v-select
          v-if="authStore.isFullAccess && addableToOrder.length"
          :model-value="null"
          :items="addableToOrder"
          item-title="name"
          item-value="key"
          label="Add a bucket to the order"
          density="compact"
          hide-details
          style="max-width: 280px"
          class="mt-1"
          @update:model-value="addRule"
        />
        <div v-if="notes.length" class="mt-3">
          <div class="text-caption text-medium-emphasis">
            Notes (not computed):
          </div>
          <div v-for="note in notes" :key="note.id" class="text-caption">
            • {{ note.rule }}
            <span v-if="note.cap">— {{ note.cap }}</span>
          </div>
        </div>
      </v-card-text>
    </template>

    <!-- ── Dialogs ───────────────────────────────────────────────────── -->
    <v-dialog v-model="draftDialog" max-width="480">
      <v-card>
        <v-card-title>Add a bucket to the plan</v-card-title>
        <v-card-subtitle class="text-wrap">
          Created, with its funding transfer, when you accept the plan.
        </v-card-subtitle>
        <v-card-text>
          <v-text-field v-model="draft.name" label="Name" density="compact" />
          <v-autocomplete
            v-model="draft.account_id"
            :items="accountItems"
            item-title="account_name"
            item-value="id"
            label="Account it lives in"
            density="compact"
          />
          <v-text-field
            v-model="draft.per_paycheck"
            label="Per paycheck"
            prefix="$"
            type="number"
            density="compact"
          />
          <v-row dense>
            <v-col>
              <v-text-field
                v-model="draft.goal_amount"
                label="Goal (optional)"
                prefix="$"
                type="number"
                density="compact"
              />
            </v-col>
            <v-col>
              <v-text-field
                v-model="draft.goal_date"
                label="By (optional)"
                type="date"
                density="compact"
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="draftDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :disabled="!draft.name || !draft.account_id"
            @click="addDraft"
          >
            Add
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="bucketDialog" max-width="520">
      <BucketForm
        v-if="bucketDialog"
        :bucket="editingBucket"
        @close="bucketDialog = false"
        @save="saveBucketDefinition"
        @delete="removeBucketDefinition"
      />
    </v-dialog>

    <v-dialog v-model="confirmAccept" max-width="520">
      <v-card>
        <v-card-title>Accept this plan?</v-card-title>
        <v-card-text>
          From {{ niceDate(plan?.window.first_transfer) }}, the funding
          transfers change to match the plan:
          <ul class="mt-2">
            <li v-for="row in changedRows" :key="row.key">
              <strong>{{ row.name }}</strong>
              <template v-if="row.removed">— stops</template>
              <template v-else-if="row.is_new">
                — created, {{ schedule(row.segments) }}
              </template>
              <template v-else>— {{ schedule(row.segments) }}</template>
            </li>
          </ul>
          <div v-if="!changedRows.length" class="mt-2">
            No transfers change; goals and the overage order are saved.
          </div>
          <v-alert
            v-if="insolvent"
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            This plan is not solvent: {{ insolventWhat }}.
            <v-checkbox
              v-model="overrideInsolvent"
              label="Accept it anyway"
              density="compact"
              hide-details
              data-testid="plan-accept-override"
            />
          </v-alert>
          <div class="mt-2 text-caption">You can undo this afterwards.</div>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="confirmAccept = false">Cancel</v-btn>
          <v-btn
            :color="insolvent ? 'warning' : 'primary'"
            variant="flat"
            :disabled="insolvent && !overrideInsolvent"
            data-testid="plan-accept-confirm"
            @click="doAccept"
          >
            Accept
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmUndo" max-width="420">
      <v-card>
        <v-card-title>
          Undo the plan accepted {{ niceDate(lastAccepted?.accepted_on) }}?
        </v-card-title>
        <v-card-text>
          Every transfer it changed goes back to how it was, and buckets it
          created are deleted.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="confirmUndo = false">Cancel</v-btn>
          <v-btn color="warning" variant="flat" @click="doUndo">Undo</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
  import { computed, reactive, ref, watch } from "vue";
  import { useDisplay } from "vuetify";
  import ApexChart from "vue3-apexcharts";
  import PlanSparkline from "@/components/PlanSparkline.vue";
  import BucketOutlook from "@/components/BucketOutlook.vue";
  import BucketForm from "@/components/BucketForm.vue";
  import { useAccounts } from "@/composables/accountsComposable";
  import {
    useBuckets,
    usePlanHistory,
    useSavingsPlan,
    useWindfallRules,
  } from "@/composables/savingsPlanComposable";
  import { useAuthStore } from "@/stores/auth";

  const emit = defineEmits(["funding"]);
  const { mdAndUp } = useDisplay();
  const authStore = useAuthStore();

  // ── State ───────────────────────────────────────────────────────────
  const planWindow = ref({ start: null, end: null });
  const blankEdits = () => ({ buckets: {}, new: [], remove: [] });
  const edits = ref(blankEdits());

  const { plan, isLoading, isFetching, accept, accepting } = useSavingsPlan(
    planWindow,
    edits,
  );
  const { acceptances, revertPlan } = usePlanHistory();
  const { buckets, saveBucket, deleteBucket } = useBuckets();
  const { rules: storedRules } = useWindfallRules();
  const { accounts } = useAccounts(false);

  watch(
    () => plan.value?.funding?.account_id,
    id => id && emit("funding", id),
    { immediate: true },
  );

  // Adopt the server's default window once, so the selects show it.
  watch(
    () => plan.value?.window,
    w => {
      if (!w) return;
      if (!planWindow.value.start) planWindow.value.start = w.start;
      if (!planWindow.value.end) planWindow.value.end = w.end;
    },
    { immediate: true },
  );

  // ── Formatting ──────────────────────────────────────────────────────
  const fmt = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  });
  const money = v =>
    v === null || v === undefined ? "—" : fmt.format(Number(v));
  const niceDate = d =>
    d
      ? new Date(d + "T00:00:00").toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        })
      : "—";
  const shortDate = d =>
    new Date(d + "T00:00:00").toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });

  const verdictColor = v =>
    ({ ideal: "success", workable: "warning", insolvent: "error" })[v] ??
    "grey";
  const verdictLabel = v =>
    ({ ideal: "Ideal", workable: "Workable", insolvent: "Not solvent" })[v] ??
    "—";
  const verdictExplain = computed(() => {
    const v = plan.value?.verdict;
    if (v === "ideal") return "Nothing goes below zero.";
    if (v === "workable")
      return "A bucket dips below zero, but the next paycheck clears it.";
    if (plan.value?.funding?.verdict === "insolvent")
      return `${plan.value.funding.account_name} goes below zero — accepting it needs an override.`;
    return "A bucket stays below zero past the next paycheck — accepting it needs an override.";
  });

  const schedule = segments => {
    if (!segments?.length) return "";
    return segments
      .map((s, i) => {
        const amount = Number(s.amount);
        if (amount === 0)
          return i === 0 ? "not funded" : `stops ${shortDate(s.start)}`;
        const when = i === 0 ? "" : ` from ${shortDate(s.start)}`;
        return `${money(amount)} ×${s.count}${when}`;
      })
      .join(", then ");
  };

  // ── Window ──────────────────────────────────────────────────────────
  const startOptions = computed(() =>
    (plan.value?.window?.options ?? []).map(d => ({
      title: niceDate(d),
      value: d,
    })),
  );
  const endOptions = computed(() => {
    const w = plan.value?.window;
    if (!w) return [];
    const start = planWindow.value.start ?? w.start;
    const ends = new Set();
    // Year ends, then paydays, all within the forecast.
    for (
      let y = Number(start.slice(0, 4));
      y <= Number(w.horizon.slice(0, 4));
      y++
    ) {
      const d = `${y}-12-31`;
      if (d >= start && d <= w.horizon) ends.add(d);
    }
    w.options.filter(d => d >= start).forEach(d => ends.add(d));
    return [...ends].sort().map(d => ({ title: niceDate(d), value: d }));
  });

  // ── Editing buckets ─────────────────────────────────────────────────
  const draftByKey = key => edits.value.new.find(d => d.key === key);

  const fieldOf = (row, field) => {
    const draft = draftByKey(row.key);
    if (draft) return draft[field];
    const change = edits.value.buckets[row.key];
    if (change && field in change) return change[field];
    if (field === "per_paycheck") return Number(row.planned_per_paycheck);
    if (field === "goal_amount")
      return row.goal_amount === null ? null : Number(row.goal_amount);
    return row[field];
  };

  const setField = (row, field, value) => {
    const draft = draftByKey(row.key);
    const clean = value === "" ? null : value;
    if (draft) {
      draft[field] = clean;
      return;
    }
    edits.value.buckets[row.key] = {
      ...(edits.value.buckets[row.key] ?? {}),
      [field]: clean,
    };
  };

  const toggleRemove = row => {
    if (row.is_new) {
      edits.value.new = edits.value.new.filter(d => d.key !== row.key);
      return;
    }
    const list = edits.value.remove;
    edits.value.remove = list.includes(row.key)
      ? list.filter(k => k !== row.key)
      : [...list, row.key];
  };

  // A bucket is edited if any of its fields or its removal is pending.
  const isEdited = row =>
    !row.is_new &&
    (row.key in edits.value.buckets || edits.value.remove.includes(row.key));
  // Back to what is saved: drop this bucket's edits and any pending removal.
  const revertRow = row => {
    const { [row.key]: _dropped, ...rest } = edits.value.buckets; // eslint-disable-line no-unused-vars
    edits.value.buckets = rest;
    edits.value.remove = edits.value.remove.filter(k => k !== row.key);
  };

  const hasEdits = computed(
    () =>
      Object.keys(edits.value.buckets).length > 0 ||
      edits.value.new.length > 0 ||
      edits.value.remove.length > 0 ||
      edits.value.overage_order !== undefined ||
      edits.value.rules !== undefined,
  );
  const resetEdits = () => {
    edits.value = blankEdits();
  };

  const changedRows = computed(() =>
    (plan.value?.buckets ?? []).filter(r => r.changed || r.is_new || r.removed),
  );
  // An insolvent plan can still be accepted — the dialog asks for an override.
  const canAccept = computed(() => plan.value && !isFetching.value);
  const insolvent = computed(() => plan.value?.verdict === "insolvent");
  const insolventWhat = computed(() => {
    const parts = [];
    if (plan.value?.funding?.verdict === "insolvent")
      parts.push(`${plan.value.funding.account_name} goes below zero`);
    const bad = (plan.value?.buckets ?? []).filter(
      b => b.verdict === "insolvent",
    );
    if (bad.length)
      parts.push(
        `${bad.map(b => b.name).join(", ")} stay${bad.length === 1 ? "s" : ""} below zero past the next paycheck`,
      );
    return parts.join("; ");
  });
  const overrideInsolvent = ref(false);

  const totalDelta = computed(() =>
    plan.value
      ? Number(plan.value.total_planned_per_paycheck) -
        Number(plan.value.total_current_per_paycheck)
      : 0,
  );

  // ── New buckets ─────────────────────────────────────────────────────
  const accountItems = computed(() =>
    (accounts.value ?? []).filter(a => !a.is_parent_account),
  );
  const draftDialog = ref(false);
  const draft = reactive({});
  let draftCounter = 0;
  const openDraft = () => {
    Object.assign(draft, {
      name: "",
      account_id: null,
      per_paycheck: 0,
      goal_amount: null,
      goal_date: null,
    });
    draftDialog.value = true;
  };
  const addDraft = () => {
    edits.value.new.push({ ...draft, key: `new${draftCounter++}` });
    draftDialog.value = false;
  };

  // ── Bucket definitions (linking accounts and transfers) ─────────────
  const bucketDialog = ref(false);
  const editingBucket = ref(null);
  const editBucket = id => {
    editingBucket.value = (buckets.value ?? []).find(b => b.id === id) ?? null;
    bucketDialog.value = true;
  };
  const saveBucketDefinition = async bucket => {
    await saveBucket(bucket);
    bucketDialog.value = false;
  };
  const removeBucketDefinition = async id => {
    await deleteBucket(id);
    bucketDialog.value = false;
  };

  // ── Overage order ───────────────────────────────────────────────────
  const rules = computed(() => {
    const suggested = plan.value?.suggested_rules ?? [];
    const caps = Object.fromEntries(
      (edits.value.rules ?? []).map(r => [r.key, r.cap_amount]),
    );
    return suggested.map(r => ({
      ...r,
      cap_amount: r.key in caps ? caps[r.key] : r.cap_amount,
    }));
  });
  const notes = computed(() =>
    (storedRules.value ?? []).filter(r => !r.bucket_id),
  );

  // Any change to the order or a cap pins the whole list as the page shows it.
  const pin = (order, capOverride = {}) => {
    const caps = Object.fromEntries(
      rules.value.map(r => [r.key, r.cap_amount]),
    );
    Object.assign(caps, capOverride);
    edits.value.overage_order = order;
    edits.value.rules = order.map(key => ({
      key,
      cap_amount: caps[key] ?? null,
    }));
  };
  const keys = () => rules.value.map(r => r.key);
  const move = (i, delta) => {
    const order = keys();
    [order[i], order[i + delta]] = [order[i + delta], order[i]];
    pin(order);
  };
  const dropRule = i => {
    const order = keys();
    order.splice(i, 1);
    pin(order);
  };
  const addRule = key => {
    if (key) pin([...keys(), key]);
  };
  const setCap = (key, value) =>
    pin(keys(), { [key]: value === "" || value === null ? null : value });
  const addableToOrder = computed(() =>
    (plan.value?.buckets ?? []).filter(
      b => !b.removed && b.linked && !keys().includes(b.key),
    ),
  );

  // ── Accept / undo ───────────────────────────────────────────────────
  const confirmAccept = ref(false);
  const confirmUndo = ref(false);
  const lastAccepted = computed(() =>
    (acceptances.value ?? []).find(a => !a.reverted_on),
  );
  watch(confirmAccept, open => {
    if (open) overrideInsolvent.value = false;
  });
  const doAccept = async () => {
    confirmAccept.value = false;
    await accept(insolvent.value && overrideInsolvent.value);
    resetEdits();
  };
  const doUndo = async () => {
    confirmUndo.value = false;
    await revertPlan(lastAccepted.value.id);
  };

  // ── Funding chart ───────────────────────────────────────────────────
  const toSeries = rows =>
    (rows ?? []).map(([d, b]) => [
      new Date(d + "T00:00:00").getTime(),
      Number(b),
    ]);
  const fundingSeries = computed(() => [
    { name: "Planned", data: toSeries(plan.value?.funding?.path) },
    { name: "Now", data: toSeries(plan.value?.funding?.current_path) },
  ]);
  const fundingChartOptions = computed(() => ({
    chart: {
      toolbar: { show: false },
      zoom: { enabled: false },
      animations: { enabled: false },
    },
    colors: [
      plan.value?.funding?.verdict === "insolvent" ? "#E53935" : "#43A047",
      "#9E9E9E",
    ],
    stroke: { curve: "stepline", width: [2, 1], dashArray: [0, 4] },
    dataLabels: { enabled: false },
    legend: { show: true, position: "top", horizontalAlign: "right" },
    xaxis: { type: "datetime" },
    yaxis: { labels: { formatter: v => money(v) } },
    tooltip: { x: { format: "MMM dd yyyy" }, y: { formatter: v => money(v) } },
    annotations: {
      yaxis: [{ y: 0, borderColor: "#E53935", strokeDashArray: 3 }],
      xaxis: plan.value
        ? [
            {
              x: new Date(plan.value.window.start + "T00:00:00").getTime(),
              borderColor: "#1E88E5",
              label: { text: "Plan starts", style: { fontSize: "10px" } },
            },
          ]
        : [],
    },
  }));
</script>

<style scoped>
  .plan-input {
    min-width: 110px;
  }
  .plan-input-date {
    min-width: 150px;
  }
  .plan-input :deep(input) {
    text-align: right;
    padding-top: 4px;
    padding-bottom: 4px;
    min-height: 32px;
  }
  .plan-row-removed td {
    opacity: 0.55;
  }
  .plan-table td {
    vertical-align: middle;
    padding-top: 4px !important;
    padding-bottom: 4px !important;
  }
</style>
