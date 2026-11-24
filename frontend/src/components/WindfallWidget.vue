<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-subtitle-1 text-primary">Windfall</v-card-title>
    <v-card-subtitle class="text-wrap">
      Money outside the paychecks — a bonus, a refund. Type the amount; any
      bucket that is not solvent is topped up first, then the rules suggest the
      rest of the split; change it if you like, then apply. Each share is
      written as a pending transfer.
    </v-card-subtitle>
    <v-card-text>
      <v-row dense>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model="amount"
            label="Amount"
            prefix="$"
            type="number"
            min="0"
            density="compact"
            data-testid="windfall-amount"
            @keyup.enter="runSuggest"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model="arrival"
            label="Lands on"
            type="date"
            density="compact"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-autocomplete
            v-model="sourceId"
            :items="accountItems"
            item-title="account_name"
            item-value="id"
            label="Lands in"
            density="compact"
          />
        </v-col>
      </v-row>
      <v-btn
        size="small"
        variant="tonal"
        color="primary"
        :disabled="!(Number(amount) > 0)"
        data-testid="windfall-suggest"
        @click="runSuggest"
      >
        Suggest a split
      </v-btn>

      <template v-if="split">
        <v-table density="compact" class="mt-3">
          <thead>
            <tr>
              <th>Bucket</th>
              <th>Why</th>
              <th class="text-right">Suggested</th>
              <th class="text-right">Amount</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in split"
              :key="row.bucket_id"
              :data-testid="`windfall-row-${row.name}`"
            >
              <td>{{ row.name }}</td>
              <td class="text-caption text-medium-emphasis">{{ row.why }}</td>
              <td class="text-right">{{ money(row.suggested) }}</td>
              <td class="text-right" style="width: 140px">
                <v-text-field
                  v-model="row.amount"
                  type="number"
                  min="0"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </td>
            </tr>
          </tbody>
        </v-table>
        <div v-if="!split.length" class="text-caption mt-2">
          No windfall rules name a bucket yet — set the order in the plan above
          and accept it.
        </div>
        <div class="d-flex align-center mt-2 ga-3">
          <span class="text-body-2">
            Allocated {{ money(allocated) }} of {{ money(amount) }}
            <span v-if="leftover > 0" class="text-medium-emphasis">
              — {{ money(leftover) }} stays in the account it lands in
            </span>
            <span v-if="leftover < 0" class="text-error">
              — {{ money(-leftover) }} more than arrived
            </span>
          </span>
          <v-spacer />
          <v-btn
            v-if="authStore.isFullAccess"
            color="primary"
            variant="flat"
            size="small"
            :disabled="leftover < 0 || allocated <= 0 || !sourceId"
            :loading="applying"
            data-testid="windfall-apply"
            @click="runApply"
          >
            Apply
          </v-btn>
        </div>
        <div v-if="notes.length" class="text-caption text-medium-emphasis mt-2">
          Also in your rules: {{ notes.map(n => n.rule).join("; ") }}
        </div>
      </template>

      <div v-if="history.length" class="mt-4">
        <div class="text-caption text-medium-emphasis">Recent windfalls</div>
        <div
          v-for="w in history"
          :key="w.id"
          class="text-body-2 d-flex align-center ga-2"
        >
          <span :class="{ 'text-decoration-line-through': w.reverted_on }">
            {{ niceDate(w.arrival_date) }} · {{ money(w.amount) }} →
            {{
              w.allocations
                .map(a => `${a.bucket_name} ${money(a.amount)}`)
                .join(", ")
            }}
          </span>
          <v-btn
            v-if="!w.reverted_on && authStore.isFullAccess"
            size="x-small"
            variant="text"
            color="warning"
            @click="revertWindfall(w.id)"
          >
            Undo
          </v-btn>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
  import { computed, ref, watch } from "vue";
  import { useAccounts } from "@/composables/accountsComposable";
  import {
    usePlanHistory,
    useWindfall,
  } from "@/composables/savingsPlanComposable";
  import { useAuthStore } from "@/stores/auth";

  const props = defineProps({
    fundingAccountId: { type: Number, default: null },
  });
  const authStore = useAuthStore();

  const today = new Date();
  const iso = d =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

  const amount = ref(null);
  const arrival = ref(iso(today));
  const sourceId = ref(props.fundingAccountId);
  watch(
    () => props.fundingAccountId,
    id => {
      if (!sourceId.value) sourceId.value = id;
    },
  );

  const split = ref(null);
  const notes = ref([]);
  const { accounts } = useAccounts(false);
  const accountItems = computed(() =>
    (accounts.value ?? []).filter(a => !a.is_parent_account),
  );
  const { suggest, apply, applying } = useWindfall();
  const { windfalls, revertWindfall } = usePlanHistory();
  const history = computed(() => (windfalls.value ?? []).slice(0, 5));

  const fmt = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  });
  const money = v => fmt.format(Number(v || 0));
  const niceDate = d =>
    new Date(d + "T00:00:00").toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });

  const allocated = computed(() =>
    (split.value ?? []).reduce((s, r) => s + Number(r.amount || 0), 0),
  );
  const leftover = computed(
    () => Math.round((Number(amount.value || 0) - allocated.value) * 100) / 100,
  );

  const runSuggest = async () => {
    if (!(Number(amount.value) > 0)) return;
    const result = await suggest(amount.value);
    split.value = result.allocations.map(r => ({
      ...r,
      amount: Number(r.suggested),
    }));
    notes.value = result.notes;
  };

  const runApply = async () => {
    await apply({
      amount: amount.value,
      arrival_date: arrival.value,
      source_account_id: sourceId.value,
      allocations: split.value.map(r => ({
        bucket_id: r.bucket_id,
        amount: r.amount || 0,
        suggested: r.suggested,
      })),
    });
    split.value = null;
    amount.value = null;
  };
</script>
