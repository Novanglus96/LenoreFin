<template>
  <div class="text-caption text-wrap" style="white-space: normal">
    <template v-if="row.removed">
      Removed — funding stops {{ niceDate(firstTransfer) }}
    </template>
    <template v-else-if="!row.linked">
      Link an account to plan this bucket
    </template>
    <template v-else>
      <v-chip :color="color" size="x-small" variant="tonal" class="mr-1">
        {{ label }}
      </v-chip>
      low {{ money(row.low_balance) }}
      <div v-if="row.goal_reached_on" class="text-info">
        Reaches its goal {{ niceDate(row.goal_reached_on) }} — consider stopping
        at your next review
        <template v-if="Number(row.paid_after_goal) > 0">
          ({{ money(row.paid_after_goal) }} more goes in after that)
        </template>
      </div>
      <div v-else-if="Number(row.shortfall) > 0" class="text-warning">
        {{ money(row.shortfall) }} short of goal — flagged for windfalls
      </div>
      <div class="text-medium-emphasis">{{ schedule }}</div>
    </template>
  </div>
</template>

<script setup>
  import { computed } from "vue";

  const props = defineProps({
    row: { type: Object, required: true },
    firstTransfer: { type: String, default: null },
  });

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

  const color = computed(
    () =>
      ({ ideal: "success", workable: "warning", insolvent: "error" })[
        props.row.verdict
      ] ?? "grey",
  );
  const label = computed(
    () =>
      ({ ideal: "Ideal", workable: "Workable", insolvent: "Not solvent" })[
        props.row.verdict
      ] ?? "—",
  );

  // "175 ×3, then 325 ×5 from Feb 13, then stops Apr 24"
  const schedule = computed(() =>
    (props.row.segments ?? [])
      .map((s, i) => {
        const amount = Number(s.amount);
        if (amount === 0)
          return i === 0 ? "not funded" : `stops ${shortDate(s.start)}`;
        const when = i === 0 ? "" : ` from ${shortDate(s.start)}`;
        return `${money(amount)} ×${s.count}${when}`;
      })
      .join(", then "),
  );
</script>
