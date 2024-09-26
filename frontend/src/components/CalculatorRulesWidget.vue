<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Rule" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-table-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="calcAddRuleFormDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
    </template>
    <CalculatorRuleForm
      v-model="calcAddRuleFormDialog"
      @update-dialog="updateAddDialog"
      :key="0"
      :isEdit="false"
    />
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Rules</span>
    </template>
    <template v-slot:text>
      <v-list :selected="rule_selected" nav>
        <v-list-item
          v-for="(item, i) in props.rules"
          :key="i"
          @click="selectRule(item.id)"
          color="accent"
          :value="item.id"
        >
          <v-list-item-title>{{ item.name }}</v-list-item-title>
          <template #append>
            <v-btn variant="plain" icon @click.stop="clickEditRule(item)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn variant="plain" icon @click.stop="clickDeleteRule(item.id)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
            <v-dialog v-model="showDeleteDialog" width="400">
              <v-card>
                <v-card-title>Delete this rule?</v-card-title>
                <v-card-actions
                  ><v-btn @click="showDeleteDialog = false">Close</v-btn
                  ><v-btn @click="confirmDeleteRule"
                    >Delete</v-btn
                  ></v-card-actions
                >
              </v-card>
            </v-dialog>
          </template>
        </v-list-item>
      </v-list>
      <CalculatorRuleForm
        v-model="calcEditRuleFormDialog"
        @update-dialog="updateEditDialog"
        :key="1"
        :isEdit="true"
        :passedFormData="passedFormData"
      />
    </template>
  </v-card>
</template>
<script setup>
import { ref, defineProps, defineEmits } from "vue";
import CalculatorRuleForm from "./CalculatorRuleForm.vue";
import { useCalculationRule } from "@/composables/calculatorComposable";

const emit = defineEmits(["ruleSelected"]);
const { removeCalculationRule } = useCalculationRule();
const rule_selected = ref(null);
const calcAddRuleFormDialog = ref(false);
const calcEditRuleFormDialog = ref(false);
const passedFormData = ref(null);
const showDeleteDialog = ref(false);
const ruleToDelete = ref(null);

const props = defineProps({
  rules: Object,
  isLoading: Boolean,
});

const selectRule = value => {
  emit("ruleSelected", value);
};
const clickEditRule = item => {
  passedFormData.value = item;
  calcEditRuleFormDialog.value = true;
};
const clickDeleteRule = id => {
  ruleToDelete.value = id;
  showDeleteDialog.value = true;
};
const confirmDeleteRule = () => {
  removeCalculationRule(ruleToDelete.value);
  showDeleteDialog.value = false;
};
const updateAddDialog = value => {
  calcAddRuleFormDialog.value = value;
};
const updateEditDialog = value => {
  calcEditRuleFormDialog.value = value;
};
</script>
<style>
.icon-with-text {
  position: relative;
  display: inline-block;
}

.icon-text {
  position: absolute;
  top: 0;
  right: 1;
  color: black;
  padding: 4px 1px;
  font-size: 0.7rem;
}
</style>
