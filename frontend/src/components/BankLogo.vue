<template>
  <v-avatar :size="size" rounded="sm">
    <v-img v-if="logoUrl" :src="logoUrl" :alt="alt" />
    <v-icon v-else :icon="defaultIcon" :size="iconSize" />
  </v-avatar>
</template>
<script setup>
  import { defineProps, computed } from "vue";

  const props = defineProps({
    logoUrl: { type: String, default: null },
    size: { type: [Number, String], default: 24 },
    alt: { type: String, default: "Bank logo" },
    defaultIcon: { type: String, default: "mdi-bank" },
  });

  const iconSize = computed(() => {
    const n = parseInt(props.size);
    return isNaN(n) ? "small" : Math.round(n * 0.7);
  });
</script>
