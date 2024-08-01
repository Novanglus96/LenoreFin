<template>
  <div>
    <!--
      Simple way of switching selected component,
      or use your own sidebar component
    -->
    <DoxenSidebar v-model="selectedDemo" :demos="demos" />
    <VueDoxen v-model="selectedDemo" :demos="demos" />
    <!--
      Optional CSS file for syntax highlighting
    -->
    <link
      href="https://unpkg.com/highlightjs/styles/ir-black.css"
      rel="stylesheet"
      type="text/css"
    />
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { DoxenSidebar, VueDoxen } from "vue-doxen";

// OPTIONAL: CSS file for minor layout/affordance improvements
import "vue-doxen/vue-doxen.css";

// Components you want to document/demo
import AccountForecastWidget from "../components/AccountForecastWidget.vue";
import AccountTransactionsWidget from "../components/AccountTransactionsWidget.vue";

defineOptions({
  name: "DocumentationPage",
});

const selectedDemo = ref("AccountForecastWidget");

const demos = computed(() => {
  return {
    // Pass the component in directly
    AccountForecastWidget,
    // or wrap it in a "demo" object to add
    // documentation specific properties
    ComponentB: {
      component: AccountTransactionsWidget,
      description: "Details about your component",
    },
  };
});
</script>
