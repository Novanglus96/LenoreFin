<template>
  <v-speed-dial
    v-model="open"
    location="left center"
    transition="slide-y-reverse-transition"
    activator="parent"
  >
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        :icon="!open ? 'mdi-dots-vertical' : 'mdi-close'"
        v-bind="activatorProps"
        :variant="!open ? 'plain' : 'outlined'"
        size="small"
      ></v-btn>
    </template>
    <v-btn
      icon="mdi-invoice-remove"
      :key="1"
      variant="outlined"
      class="bg-error"
    ></v-btn>
    <v-btn
      icon="mdi-invoice-text-edit"
      :key="2"
      variant="outlined"
      class="bg-surface"
    ></v-btn>
    <v-btn
      icon="mdi-invoice-text-clock"
      :key="3"
      variant="outlined"
      class="bg-surface"
    ></v-btn>
  </v-speed-dial>
</template>
<script setup>
  import { ref } from "vue";

  const open = ref(false);
</script>
