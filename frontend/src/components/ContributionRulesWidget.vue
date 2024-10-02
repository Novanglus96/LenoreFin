<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Overage Rule" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-water-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addContributionRuleDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
    </template>
    <ContributionRuleForm
      v-model="addContributionRuleDialog"
      key="0"
      :isEdit="false"
      @update-dialog="updateAddDialog"
      @add-contribution-rule="clickAddContributionRule"
      :passedFormData="newContributionRuleData"
    />
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary"
        >Per Paycheck Overage Rules</span
      >
    </template>
    <template v-slot:text>
      <vue3-datatable
        :rows="contributionRules ? contributionRules : []"
        :columns="columns"
        :loading="isLoading"
        :totalRows="contributionRules ? contributionRules.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="false"
        :stickyHeader="true"
        noDataContent="No rules"
        ref="contrib_rules_table"
        height="440px"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[10]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} rules"
        class="alt-pagination"
      >
        <template #order="row">
          <span class="font-weight-bold">#{{ row.value.order }}</span>
        </template>
        <template #edit="row">
          <v-btn variant="plain" icon @click="clickEditButton(row.value)"
            ><v-icon icon="mdi-pencil"></v-icon
          ></v-btn>
          <ContributionRuleForm
            v-model="editContributionRuleDialog"
            :key="row.value.id"
            :isEdit="true"
            @update-dialog="updateEditDialog"
            :passedFormData="selectedContributionRule"
            @edit-contribution-rule="clickEditContributionRule"
          />
        </template>
        <template #delete="row">
          <v-btn variant="plain" icon
            ><v-icon
              icon="mdi-delete"
              @click="clickDeleteButton(row.value)"
            ></v-icon
          ></v-btn>
          <v-dialog
            v-model="deleteContributionRuleDialog"
            :key="row.value.id"
            width="400"
            ><v-card
              ><v-card-title>Delete Rule?</v-card-title
              ><v-card-text
                ><span>{{ selectedContributionRule.rule }}</span></v-card-text
              >
              <v-card-actions
                ><v-btn @click="deleteContributionRuleDialog = false"
                  >Close</v-btn
                ><v-btn
                  @click="clickDeleteContributionRule(selectedContributionRule)"
                  >Delete</v-btn
                ></v-card-actions
              ></v-card
            ></v-dialog
          >
        </template>
      </vue3-datatable>
    </template>
  </v-card>
</template>
<script setup>
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { ref } from "vue";
import { useContributionRules } from "@/composables/contributionsComposable";
import ContributionRuleForm from "@/components/ContributionRuleForm.vue";

const contrib_rules_table = ref(null);
const editContributionRuleDialog = ref(false);
const addContributionRuleDialog = ref(false);
const deleteContributionRuleDialog = ref(false);
const selectedContributionRule = ref(null);
const newContributionRuleData = ref({});

const {
  contributionRules,
  isLoading,
  addContributionRule,
  editContributionRule,
  removeContributionRule,
} = useContributionRules();

const columns = ref([
  { field: "id", title: "id", isUnique: true, hide: true },
  { field: "order", title: "Order", width: "20px" },
  {
    field: "rule",
    title: "Rule",
    type: "string",
  },
  {
    field: "cap",
    title: "Cap",
    type: "string",
  },
  { field: "edit", title: "Edit", width: "40px", cellClass: "text-center" },
  { field: "delete", title: "Delete", width: "40px", cellClass: "text-center" },
]);

const updateAddDialog = () => {
  addContributionRuleDialog.value = false;
};

const updateEditDialog = () => {
  editContributionRuleDialog.value = false;
};

const clickEditButton = contributionRule => {
  selectedContributionRule.value = contributionRule;
  editContributionRuleDialog.value = true;
};

const clickDeleteButton = contributionRule => {
  selectedContributionRule.value = contributionRule;
  deleteContributionRuleDialog.value = true;
};

const clickEditContributionRule = contributionRule => {
  editContributionRule(contributionRule);
  editContributionRuleDialog.value = false;
};

const clickDeleteContributionRule = contributionRule => {
  removeContributionRule(contributionRule);
  deleteContributionRuleDialog.value = false;
};

const clickAddContributionRule = contributionRule => {
  addContributionRule(contributionRule);
  addContributionRuleDialog.value = false;
};
</script>
<style>
/* alt-pagination */
.alt-pagination .bh-pagination .bh-page-item {
  width: auto; /* equivalent to w-max */
  min-width: 32px;
  border-radius: 0.25rem; /* equivalent to rounded */
}
/* Customize the color of the selected page number */
.alt-pagination .bh-pagination .bh-page-item.bh-active {
  background-color: #06966a; /* Change this to your desired color */
  border-color: black;
  font-weight: bold; /* Optional: Make the text bold */
}
.alt-pagination .bh-pagination .bh-page-item:not(.bh-active):hover {
  background-color: #ff5900;
  border-color: black;
}

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
