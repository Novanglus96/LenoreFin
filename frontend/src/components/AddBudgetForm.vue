<template>
  <v-dialog persistent width="900"
    ><BudgetForm
      :budget="newBudget"
      :edit="false"
      :key="-1"
      @update-dialog="closeDialog"
  /></v-dialog>
</template>
<script setup>
import { defineEmits, ref } from "vue";
import BudgetForm from "@/components/BudgetForm.vue";

const emit = defineEmits(["updateDialog"]);

const newBudget = ref({
  id: null,
  tag_ids: "[null]",
  name: null,
  amount: 0.0,
  roll_over: true,
  repeat: null,
  start_day: null,
  roll_over_amt: 0.0,
  active: true,
  widget: true,
  next_start: null,
});

const closeDialog = () => {
  emit("updateDialog", false);
};
</script>
