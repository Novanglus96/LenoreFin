<template>
  <svg
    :viewBox="`0 0 ${width} ${height}`"
    :width="width"
    :height="height"
    class="plan-spark"
    role="img"
    :aria-label="label"
  >
    <line x1="0" :x2="width" :y1="zeroY" :y2="zeroY" class="plan-spark-zero" />
    <polyline
      v-if="current.length"
      :points="currentPoints"
      class="plan-spark-current"
    />
    <polyline :points="plannedPoints" :class="lineClass" />
  </svg>
</template>

<script setup>
  import { computed } from "vue";

  // `path` and `current` are [[isoDate, balance], ...] from the plan.
  const props = defineProps({
    path: { type: Array, default: () => [] },
    current: { type: Array, default: () => [] },
    width: { type: Number, default: 160 },
    height: { type: Number, default: 36 },
    label: { type: String, default: "Balance over the plan" },
  });

  const parse = rows =>
    rows.map(([d, b]) => [new Date(d + "T00:00:00").getTime(), Number(b)]);

  const planned = computed(() => parse(props.path));
  const currentRows = computed(() => parse(props.current));

  const bounds = computed(() => {
    const all = [...planned.value, ...currentRows.value];
    if (!all.length) return { x0: 0, x1: 1, lo: 0, hi: 1 };
    const xs = all.map(p => p[0]);
    const ys = all.map(p => p[1]);
    const lo = Math.min(0, ...ys);
    const hi = Math.max(0, ...ys);
    return {
      x0: Math.min(...xs),
      x1: Math.max(...xs),
      lo,
      hi: hi === lo ? lo + 1 : hi,
    };
  });

  const PAD = 2;
  const x = t => {
    const { x0, x1 } = bounds.value;
    return ((t - x0) / (x1 - x0 || 1)) * props.width;
  };
  const y = v => {
    const { lo, hi } = bounds.value;
    return PAD + (1 - (v - lo) / (hi - lo)) * (props.height - 2 * PAD);
  };
  // Balances change on a day and hold until the next: draw steps.
  const stepped = rows => {
    const out = [];
    rows.forEach(([t, v], i) => {
      if (i > 0) out.push(`${x(t).toFixed(1)},${y(rows[i - 1][1]).toFixed(1)}`);
      out.push(`${x(t).toFixed(1)},${y(v).toFixed(1)}`);
    });
    return out.join(" ");
  };

  const zeroY = computed(() => y(0));
  const plannedPoints = computed(() => stepped(planned.value));
  const currentPoints = computed(() => stepped(currentRows.value));
  const lineClass = computed(() =>
    planned.value.some(p => p[1] < 0)
      ? "plan-spark-line plan-spark-bad"
      : "plan-spark-line plan-spark-ok",
  );
</script>

<style scoped>
  .plan-spark {
    display: block;
    overflow: visible;
  }
  .plan-spark-zero {
    stroke: rgb(var(--v-theme-on-surface));
    stroke-opacity: 0.35;
    stroke-width: 1;
    stroke-dasharray: 2 2;
  }
  .plan-spark-line {
    fill: none;
    stroke-width: 1.75;
  }
  .plan-spark-ok {
    stroke: rgb(var(--v-theme-success));
  }
  .plan-spark-bad {
    stroke: rgb(var(--v-theme-error));
  }
  .plan-spark-current {
    fill: none;
    stroke: rgb(var(--v-theme-on-surface));
    stroke-opacity: 0.3;
    stroke-width: 1;
    stroke-dasharray: 3 2;
  }
</style>
