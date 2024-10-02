<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Contribution" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-pail-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addContributionDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
    </template>
    <ContributionForm
      v-model="addContributionDialog"
      key="0"
      :isEdit="false"
      @update-dialog="updateAddDialog"
      @add-contribution="clickAddContribution"
      :passedFormData="newContributionData"
    />
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary"
        >Per Paycheck Contribution Rules</span
      >
    </template>
    <template v-slot:text>
      <v-container
        ><v-row dense
          ><v-col class="text-right text-subtitle-2 font-weight-bold" cols="3"
            >Paycheck Total(non Emergency)</v-col
          ><v-col class="text-left text-body-2" cols="1"
            >${{
              contributions ? contributions.per_paycheck_total : "0"
            }}</v-col
          ><v-col cols="3" class="text-right text-subtitle-2 font-weight-bold"
            >Paycheck Total(Emergency)</v-col
          ><v-col class="text-left text-body-2" cols="1"
            >${{
              contributions ? contributions.emergency_paycheck_total : "0"
            }}</v-col
          ><v-col class="text-right text-subtitle-2 font-weight-bold" cols="3"
            >Emergency Total</v-col
          ><v-col class="text-left text-body-2" cols="1"
            >${{ contributions ? contributions.total_emergency : "0" }}</v-col
          ></v-row
        >
      </v-container>
      <vue3-datatable
        :rows="contributions ? contributions.contributions : []"
        :columns="columns"
        :loading="isLoading"
        :totalRows="contributions ? contributions.contributions.length : 0"
        :isServerMode="false"
        pageSize="10"
        :hasCheckbox="false"
        :stickyHeader="true"
        noDataContent="No contributions"
        ref="contrib_table"
        height="340px"
        skin="bh-table-striped bh-table-compact"
        :pageSizeOptions="[10]"
        :showPageSize="false"
        paginationInfo="Showing {0} to {1} of {2} contributions"
        class="alt-pagination"
      >
        <template #contribution="row">
          <span
            :class="
              row.value.active
                ? 'font-weight-bold'
                : 'font-italic font-weight-bold'
            "
            >{{ row.value.contribution
            }}{{ row.value.active ? "" : " (not active)" }}</span
          >
        </template>
        <template #per_paycheck="row">
          <span :class="row.value.active ? '' : 'font-italic'"
            >${{ row.value.per_paycheck }}</span
          >
        </template>
        <template #emergency_amt="row">
          <span :class="row.value.active ? '' : 'font-italic'"
            >${{ row.value.emergency_amt }}</span
          >
        </template>
        <template #emergency_diff="row">
          <span :class="row.value.active ? '' : 'font-italic'"
            >${{ row.value.emergency_diff }}</span
          >
        </template>
        <template #cap="row">
          <span :class="row.value.active ? '' : 'font-italic'"
            >${{ row.value.cap }}</span
          >
        </template>
        <template #edit="row">
          <v-btn variant="plain" icon @click="clickEditButton(row.value)"
            ><v-icon icon="mdi-pencil"></v-icon
          ></v-btn>
          <ContributionForm
            v-model="editContributionDialog"
            :key="row.value.id"
            :isEdit="true"
            @update-dialog="updateEditDialog"
            :passedFormData="selectedContribution"
            @edit-contribution="clickEditContribution"
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
            v-model="deleteContributionDialog"
            :key="row.value.id"
            width="400"
            ><v-card
              ><v-card-title>Delete Contribution?</v-card-title
              ><v-card-text
                ><span>{{
                  selectedContribution.contribution
                }}</span></v-card-text
              >
              <v-card-actions
                ><v-btn @click="deleteContributionDialog = false">Close</v-btn
                ><v-btn @click="clickDeleteContribution(selectedContribution)"
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
import { useContributions } from "@/composables/contributionsComposable";
import ContributionForm from "@/components/ContributionForm.vue";

const contrib_table = ref(null);
const editContributionDialog = ref(false);
const addContributionDialog = ref(false);
const deleteContributionDialog = ref(false);
const selectedContribution = ref(null);
const newContributionData = ref({
  id: 0,
  contribution: null,
  per_paycheck: "0",
  emergency_diff: "0",
  emergency_amt: "0",
  cap: "0",
  active: true,
});

const {
  contributions,
  isLoading,
  addContribution,
  editContribution,
  removeContribution,
} = useContributions();

const columns = ref([
  { field: "id", title: "id", isUnique: true, hide: true },
  {
    field: "contribution",
    title: "Contribution",
    type: "string",
    cellClass: "text-right",
    headerClass: "text-right",
  },
  {
    field: "per_paycheck",
    title: "Paycheck(per)",
    type: "number",
    width: "140px",
    cellClass: "text-center",
  },
  {
    field: "emergency_amt",
    title: "Emergency Amt",
    type: "number",
    width: "140px",
    cellClass: "text-center",
  },
  {
    field: "emergency_diff",
    title: "Difference",
    type: "number",
    width: "140px",
    cellClass: "text-center",
  },
  {
    field: "cap",
    title: "Cap Amount",
    type: "number",
    width: "140px",
    cellClass: "text-center",
  },
  {
    field: "active",
    title: "Active",
    type: "bool",
    hide: true,
  },
  { field: "edit", title: "Edit", width: "40px", cellClass: "text-center" },
  { field: "delete", title: "Delete", width: "40px", cellClass: "text-center" },
]);

const updateAddDialog = () => {
  addContributionDialog.value = false;
};

const updateEditDialog = () => {
  editContributionDialog.value = false;
};

const clickEditButton = contribution => {
  selectedContribution.value = contribution;
  editContributionDialog.value = true;
};

const clickDeleteButton = contribution => {
  selectedContribution.value = contribution;
  deleteContributionDialog.value = true;
};

const clickEditContribution = contribution => {
  editContribution(contribution);
  editContributionDialog.value = false;
};

const clickDeleteContribution = contribution => {
  removeContribution(contribution);
  deleteContributionDialog.value = false;
};

const clickAddContribution = contribution => {
  addContribution(contribution);
  addContributionDialog.value = false;
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
