<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span class="text-subtitle-2 text-primary">
        Per Paycheck Contribution Rules
      </span>
      <v-tooltip text="Add Contribution" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-pail-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addContributionDialog = true"
            size="small"
            color="grey"
          ></v-btn>
        </template>
      </v-tooltip>

      <ContributionForm
        v-model="addContributionDialog"
        key="0"
        :isEdit="false"
        @update-dialog="updateAddDialog"
        @add-contribution="clickAddContribution"
        :passedFormData="newContributionData"
      />
    </v-card-title>
    <v-card-text class="ma-0 pa-0 ga-0">
      <v-container>
        <v-row dense>
          <!-- Label -->
          <v-col
            :class="
              smAndDown
                ? 'text-center text-subtitle-2 font-weight-bold'
                : 'text-right text-subtitle-2 font-weight-bold'
            "
            cols="12"
            sm="6"
            md="3"
          >
            Paycheck Total (non Emergency)
          </v-col>
          <!-- Value -->
          <v-col
            :class="
              smAndDown ? 'text-center text-body-2' : 'text-left text-body-2'
            "
            cols="12"
            sm="6"
            md="1"
          >
            <NumberFlow
              :value="contributions ? contributions.per_paycheck_total : 0"
              :format="{ style: 'currency', currency: 'USD' }"
            />
          </v-col>

          <!-- Label -->
          <v-col
            :class="
              smAndDown
                ? 'text-center text-subtitle-2 font-weight-bold'
                : 'text-right text-subtitle-2 font-weight-bold'
            "
            cols="12"
            sm="6"
            md="3"
          >
            Paycheck Total (Emergency)
          </v-col>
          <!-- Value -->
          <v-col
            :class="
              smAndDown ? 'text-center text-body-2' : 'text-left text-body-2'
            "
            cols="12"
            sm="6"
            md="1"
          >
            <NumberFlow
              :value="
                contributions ? contributions.emergency_paycheck_total : 0
              "
              :format="{ style: 'currency', currency: 'USD' }"
            />
          </v-col>

          <!-- Label -->
          <v-col
            :class="
              smAndDown
                ? 'text-center text-subtitle-2 font-weight-bold'
                : 'text-right text-subtitle-2 font-weight-bold'
            "
            cols="12"
            sm="6"
            md="3"
          >
            Emergency Total
          </v-col>
          <!-- Value -->
          <v-col
            :class="
              smAndDown ? 'text-center text-body-2' : 'text-left text-body-2'
            "
            cols="12"
            sm="6"
            md="1"
          >
            <NumberFlow
              :value="contributions ? contributions.total_emergency : 0"
              :format="{ style: 'currency', currency: 'USD' }"
            />
          </v-col>
        </v-row>
      </v-container>
      <v-data-table
        :headers="displayHeaders"
        :items="contributions ? contributions.contributions : []"
        :items-length="contributions ? contributions.contributions.length : 0"
        :loading="isLoading"
        item-value="id"
        v-model:items-per-page="itemsPerPage"
        v-model:page="page"
        :items-per-page-options="[
          {
            value: 5,
            title: 5,
          },
        ]"
        items-per-page-text="Contributions per page"
        no-data-text="No contributions!"
        loading-text="Loading contributions..."
        disable-sort
        :show-select="true"
        fixed-footer
        striped="odd"
        density="compact"
        :hide-default-header="mdAndUp ? false : true"
        width="100%"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        v-model="selectedContribution"
        select-strategy="single"
        return-object
        :row-props="getRowProps"
        class="bg-background"
      >
        <template v-slot:bottom>
          <div class="text-center pt-2">
            <v-pagination v-model="page" :length="pageCount"></v-pagination>
          </div>
        </template>
        <template v-slot:top>
          <div class="d-flex align-center">
            <v-btn
              variant="plain"
              icon
              @click="editContributionDialog = true"
              :disabled="selectedContribution.length === 0"
            >
              <v-icon icon="mdi-pencil"></v-icon>
            </v-btn>
            <ContributionForm
              v-model="editContributionDialog"
              :key="editContrib ? editContrib.id : 0"
              :isEdit="true"
              @update-dialog="updateEditDialog"
              :passedFormData="editContrib"
              @edit-contribution="clickEditContribution"
            />
            <v-btn
              variant="plain"
              icon
              :disabled="selectedContribution.length === 0"
            >
              <v-icon
                icon="mdi-delete"
                @click="deleteContributionDialog = true"
                color="error"
              ></v-icon>
            </v-btn>
            <v-dialog
              v-model="deleteContributionDialog"
              :key="editContrib ? editContrib.id : 0"
              width="400"
            >
              <v-card>
                <v-card-title>Delete Contribution?</v-card-title>
                <v-card-text>
                  <span>{{ editContrib.contribution }}</span>
                </v-card-text>
                <v-card-actions>
                  <v-btn @click="deleteContributionDialog = false">Close</v-btn>
                  <v-btn @click="clickDeleteContribution(editContrib)">
                    Delete
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </div>
        </template>
        <template v-slot:[`header.per_paycheck`] v-if="mdAndUp">
          <div class="text-center">Paycheck(per)</div>
        </template>
        <template v-slot:[`header.emergency_amt`] v-if="mdAndUp">
          <div class="text-center">Emergenct Amt</div>
        </template>
        <template v-slot:[`header.emergency_diff`] v-if="mdAndUp">
          <div class="text-center">Difference</div>
        </template>
        <template v-slot:[`header.cap`] v-if="mdAndUp">
          <div class="text-center">Cap Amount</div>
        </template>
        <template v-slot:[`item.contribution`]="{ item }" v-if="mdAndUp">
          <div>
            <span
              :class="
                item.active
                  ? 'font-weight-bold'
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ item.contribution }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.per_paycheck`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span
              :class="
                item.active
                  ? ''
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ formatCurrency(item.per_paycheck) }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.emergency_amt`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span
              :class="
                item.active
                  ? ''
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ formatCurrency(item.emergency_amt) }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.emergency_diff`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span
              :class="
                item.active
                  ? ''
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ formatCurrency(item.emergency_diff) }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.cap`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span
              :class="
                item.active
                  ? ''
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ formatCurrency(item.cap) }}
            </span>
          </div>
        </template>
        <!-- Mobile View -->
        <template v-slot:[`item.mobile`]="{ item }">
          <v-container class="ma-0 pa-0 ga-0">
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col
                class="ma-0 pa-0 ga-0 font-weight-bold text-primary"
                cols="12"
              >
                {{ item.contribution }}
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Per
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Emer
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Diff
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Cap
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ formatCurrency(item.per_paycheck) }}
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ formatCurrency(item.emergency_amt) }}
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ formatCurrency(item.emergency_diff) }}
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ formatCurrency(item.cap) }}
              </v-col>
            </v-row>
          </v-container>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>
<script setup>
  import { ref, computed, watch } from "vue";
  import { useContributions } from "@/composables/contributionsComposable";
  import ContributionForm from "@/components/ContributionForm.vue";
  import NumberFlow from "@number-flow/vue";
  import { useDisplay } from "vuetify";

  const page = ref(1);
  const itemsPerPage = ref(5);
  const { smAndDown, mdAndUp } = useDisplay();
  const editContributionDialog = ref(false);
  const addContributionDialog = ref(false);
  const deleteContributionDialog = ref(false);
  const selectedContribution = ref([]);
  const editContrib = ref({ id: 0 });
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

  const headers = ref([
    { title: "Contribution", key: "contribution" },
    { title: "Paycheck(per)", key: "per_paycheck", width: "140px" },
    { title: "Emergency Amt", key: "emergency_amt", width: "140px" },
    { title: "Difference", key: "emergency_diff", width: "140px" },
    { title: "Cap Amount", key: "cap", width: "140px" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });

  const updateAddDialog = () => {
    addContributionDialog.value = false;
  };

  const updateEditDialog = () => {
    editContributionDialog.value = false;
  };

  const clickEditContribution = contribution => {
    editContribution(contribution);
    editContributionDialog.value = false;
    selectedContribution.value = [];
  };

  const clickDeleteContribution = contribution => {
    removeContribution(contribution);
    deleteContributionDialog.value = false;
    selectedContribution.value = [];
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
  const pageCount = computed(() =>
    contributions.value && itemsPerPage.value
      ? Math.ceil(contributions.value.contributions.length / itemsPerPage.value)
      : 1,
  );
  watch(
    () => selectedContribution.value,
    val => {
      if (val) {
        editContrib.value = val[0];
      }
    },
  );
  function getRowProps({ item }) {
    let rowformat = "";
    const isSelected = selectedContribution.value.some(
      sel => sel.id === item.id,
    );
    if (isSelected) {
      rowformat += "bg-primary-lighten-3";
    }
    return {
      class: rowformat,
    };
  }
</script>
