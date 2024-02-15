<template>
  <v-app>
    <AppNavigationVue />
    <v-main>
      <v-container class="bg-primary h-100" fluid>
        <router-view />
      </v-container>
      <v-snackbar
        v-model="mainstore.snackbar"
        :color="mainstore.snackbarColor"
        :timeout="mainstore.snackbarTimeout"
        content-class="centered-text"
      >
        {{ mainstore.snackbarText }}
      </v-snackbar>
    </v-main>
  </v-app>
</template>
<script setup>
import AppNavigationVue from "@/views/AppNavigationVue";
import { useMainStore } from "@/stores/main";
import { onMounted } from "vue";
import { useOptions } from "@/composables/optionsComposable";

const mainstore = useMainStore();
const { prefetchOptions } = useOptions();
onMounted(() => {
  prefetchOptions();
});
</script>
