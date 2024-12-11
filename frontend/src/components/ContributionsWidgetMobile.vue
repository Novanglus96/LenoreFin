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
    <ContributionFormMobile
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
          ><v-col class="text-body-2 text-center"
            ><v-tooltip text="Per Paycheck Total" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-checkbook" v-bind="props"></v-icon>
              </template>
            </v-tooltip>
            <NumberFlow
              :value="contributions ? contributions.per_paycheck_total : 0"
              :format="{ style: 'currency', currency: 'USD' }"
            /> </v-col
          ><v-col class="text-body-2 text-center">
            <v-tooltip text="Emergency Per Paycheck Total" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-alert-box" v-bind="props"></v-icon>
              </template> </v-tooltip
            ><NumberFlow
              :value="
                contributions ? contributions.emergency_paycheck_total : 0
              "
              :format="{ style: 'currency', currency: 'USD' }" /></v-col
          ><v-col class="text-body-2 text-center"
            ><v-tooltip text="Emergency Total" location="top">
              <template v-slot:activator="{ props }">
                <v-icon icon="mdi-vector-difference" v-bind="props"></v-icon>
              </template> </v-tooltip
            ><NumberFlow
              :value="contributions ? contributions.total_emergency : 0"
              :format="{ style: 'currency', currency: 'USD' }" /></v-col
        ></v-row>
      </v-container>
      <v-data-iterator
        :items="contributions ? contributions.contributions : []"
        :loading="isLoading"
        items-per-page="10"
      >
        <template v-slot:default="{ items }">
          <template v-for="(item, i) in items" :key="i">
            <v-card class="flex ma-0 pa-0 ga-0"
              ><v-card-text
                ><v-container class="flex ma-0 pa-0 ga-0"
                  ><v-row dense
                    ><v-col class="font-weight-bold">{{
                      item.raw.contribution
                    }}</v-col></v-row
                  ><v-row dense
                    ><v-col
                      ><v-tooltip text="Per Paycheck" location="top">
                        <template v-slot:activator="{ props }">
                          <v-icon icon="mdi-checkbook" v-bind="props"></v-icon>
                        </template> </v-tooltip
                      >{{ formatCurrency(item.raw.per_paycheck) }}</v-col
                    ><v-col
                      ><v-tooltip text="Emergency Amount" location="top">
                        <template v-slot:activator="{ props }">
                          <v-icon icon="mdi-alert-box" v-bind="props"></v-icon>
                        </template> </v-tooltip
                      >{{ formatCurrency(item.raw.emergency_amt) }}</v-col
                    ><v-col
                      ><v-tooltip text="Emergency Difference" location="top">
                        <template v-slot:activator="{ props }">
                          <v-icon
                            icon="mdi-vector-difference"
                            v-bind="props"
                          ></v-icon>
                        </template> </v-tooltip
                      >{{ formatCurrency(item.raw.emergency_diff) }}</v-col
                    ><v-col
                      ><v-tooltip text="Cap" location="top">
                        <template v-slot:activator="{ props }">
                          <v-icon icon="mdi-finance" v-bind="props"></v-icon>
                        </template> </v-tooltip
                      >{{ formatCurrency(item.raw.cap) }}</v-col
                    ></v-row
                  ></v-container
                ></v-card-text
              ><v-card-actions
                ><v-spacer></v-spacer
                ><v-btn @click="clickEditButton(i, item.raw)">Edit</v-btn
                ><ContributionFormMobile
                  v-model="editContributionDialog[i]"
                  :key="item.raw.id"
                  :isEdit="true"
                  @update-dialog="clickEditButton(i)"
                  :passedFormData="selectedContribution"
                  @edit-contribution="clickEditContribution"
                />
                <v-btn @click="clickDeleteButton(i, item.raw)">Delete</v-btn
                ><v-dialog
                  v-model="deleteContributionDialog[i]"
                  :key="item.raw.id"
                  width="400"
                  ><v-card
                    ><v-card-title>Delete Contribution?</v-card-title
                    ><v-card-text
                      ><span>{{
                        selectedContribution.contribution
                      }}</span></v-card-text
                    >
                    <v-card-actions
                      ><v-btn @click="clickDeleteButton(i)">Close</v-btn
                      ><v-btn
                        @click="
                          clickDeleteContribution(selectedContribution, i)
                        "
                        >Delete</v-btn
                      ></v-card-actions
                    ></v-card
                  ></v-dialog
                ></v-card-actions
              ></v-card
            >
            <br />
          </template>
        </template>
        <template v-slot:loader
          ><v-skeleton-loader
            class="border"
            type="paragraph"
          ></v-skeleton-loader
        ></template>
        <template v-slot:footer="{ page, pageCount, prevPage, nextPage }">
          <div class="d-flex align-center justify-center pa-4">
            <v-btn
              :disabled="page === 1"
              density="comfortable"
              icon="mdi-arrow-left"
              variant="tonal"
              rounded
              @click="prevPage"
            ></v-btn>

            <div class="mx-2 text-caption">
              Page {{ page }} of {{ pageCount }}
            </div>

            <v-btn
              :disabled="page >= pageCount"
              density="comfortable"
              icon="mdi-arrow-right"
              variant="tonal"
              rounded
              @click="nextPage"
            ></v-btn>
          </div>
        </template>
      </v-data-iterator>
    </template>
  </v-card>
</template>
<script setup>
import { ref } from "vue";
import { useContributions } from "@/composables/contributionsComposable";
import ContributionFormMobile from "@/components/ContributionFormMobile.vue";
import NumberFlow from "@number-flow/vue";

const editContributionDialog = ref({});
const addContributionDialog = ref(false);
const deleteContributionDialog = ref({});
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

const updateAddDialog = () => {
  addContributionDialog.value = false;
};

const clickEditButton = (index, contribution) => {
  if (contribution) {
    selectedContribution.value = contribution;
  }
  editContributionDialog.value[index] = !editContributionDialog.value[index];
};

const clickDeleteButton = (index, contribution) => {
  if (contribution) {
    selectedContribution.value = contribution;
  }
  deleteContributionDialog.value[index] =
    !deleteContributionDialog.value[index];
};

const clickEditContribution = contribution => {
  editContribution(contribution);
};

const clickDeleteContribution = (contribution, index) => {
  removeContribution(contribution);
  deleteContributionDialog.value[index] =
    !deleteContributionDialog.value[index];
};

const clickAddContribution = contribution => {
  addContribution(contribution);
  addContributionDialog.value = false;
};
const formatCurrency = value => {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
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
