<template>
  <v-speed-dial
    v-model="open"
    location="left center"
    transition="slide-y-reverse-transition"
    activator="parent"
  >
    <template v-slot:activator="{ props: activatorProps }">
      <v-btn
        icon
        v-bind="activatorProps"
        :variant="!open ? 'plain' : 'outlined'"
        size="small"
      >
        <!-- A genuine change of shape rather than a fill state, so this scales
             instead of cross-fading. -->
        <AnimatedIcon
          transition="scale"
          :icon="!open ? 'mdi-dots-vertical' : 'mdi-close'"
        />
      </v-btn>
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
  import AnimatedIcon from "@/components/AnimatedIcon.vue";

  const open = ref(false);
</script>
