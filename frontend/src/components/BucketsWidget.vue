<template>
  <v-card variant="outlined" :elevation="4" class="bg-surface">
    <v-card-title class="text-left">
      <span class="text-subtitle-2 text-primary">
        Per Paycheck Windfall Rules
      </span>
      <v-tooltip text="Add Bucket" location="top" v-if="authStore.isFullAccess">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-pail-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="addBucketDialog = true"
            size="small"
            :disabled="!isOnline"
          ></v-btn>
        </template>
      </v-tooltip>

      <BucketForm
        v-model="addBucketDialog"
        key="0"
        :isEdit="false"
        @update-dialog="updateAddDialog"
        @add-bucket="clickAddBucket"
        :passedFormData="newBucketData"
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
              :value="buckets ? buckets.per_paycheck_total : 0"
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
                buckets ? buckets.emergency_paycheck_total : 0
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
              :value="buckets ? buckets.total_emergency : 0"
              :format="{ style: 'currency', currency: 'USD' }"
            />
          </v-col>
        </v-row>
      </v-container>
      <v-data-table
        :headers="displayHeaders"
        :items="buckets ? buckets.buckets : []"
        :items-length="buckets ? buckets.buckets.length : 0"
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
        items-per-page-text="Buckets per page"
        no-data-text="No buckets!"
        loading-text="Loading buckets..."
        disable-sort
        :show-select="true"
        fixed-footer
        striped="odd"
        density="compact"
        :hide-default-header="mdAndUp ? false : true"
        width="100%"
        :header-props="{ class: 'font-weight-bold bg-secondary' }"
        v-model="selectedBucket"
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
            <template v-if="authStore.isFullAccess">
              <v-btn
                variant="plain"
                icon
                @click="editBucketDialog = true"
                :disabled="selectedBucket.length === 0 || !isOnline"
              >
                <v-icon icon="mdi-pencil"></v-icon>
              </v-btn>
              <BucketForm
                v-model="editBucketDialog"
                :key="editingBucket ? editingBucket.id : 0"
                :isEdit="true"
                @update-dialog="updateEditDialog"
                :passedFormData="editingBucket"
                @edit-bucket="clickEditBucket"
              />
              <v-btn
                variant="plain"
                icon
                :disabled="selectedBucket.length === 0 || !isOnline"
              >
                <v-icon
                  icon="mdi-delete"
                  @click="deleteBucketDialog = true"
                  color="error"
                ></v-icon>
              </v-btn>
              <v-dialog
                v-model="deleteBucketDialog"
                :key="editingBucket ? editingBucket.id : 0"
                width="400"
              >
                <v-card>
                  <v-card-title>Delete Bucket?</v-card-title>
                  <v-card-text>
                    <span>{{ editingBucket.bucket }}</span>
                  </v-card-text>
                  <v-card-actions>
                    <v-btn @click="deleteBucketDialog = false">Close</v-btn>
                    <v-btn @click="clickDeleteBucket(editingBucket)" :disabled="!isOnline">
                      Delete
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </template>
          </div>
        </template>
        <template v-slot:[`header.per_paycheck`] v-if="mdAndUp">
          <div class="text-center">Paycheck(per)</div>
        </template>
        <template v-slot:[`header.minimum_per_paycheck`] v-if="mdAndUp">
          <div class="text-center">Minimum</div>
        </template>
        <template v-slot:[`header.difference`] v-if="mdAndUp">
          <div class="text-center">Difference</div>
        </template>
        <template v-slot:[`header.target_balance`] v-if="mdAndUp">
          <div class="text-center">Target</div>
        </template>
        <template v-slot:[`item.bucket`]="{ item }" v-if="mdAndUp">
          <div>
            <span
              :class="
                item.active
                  ? 'font-weight-bold'
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ item.bucket }}
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
        <template
          v-slot:[`item.minimum_per_paycheck`]="{ item }"
          v-if="mdAndUp"
        >
          <div class="text-center">
            <span
              :class="
                item.active
                  ? ''
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ minimumLabel(item) }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.difference`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span
              :class="
                item.active
                  ? ''
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ differenceLabel(item) }}
            </span>
          </div>
        </template>
        <template v-slot:[`item.target_balance`]="{ item }" v-if="mdAndUp">
          <div class="text-center">
            <span
              :class="
                item.active
                  ? ''
                  : 'font-italic text-warning text-decoration-line-through'
              "
            >
              {{ targetLabel(item) }}
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
                {{ item.bucket }}
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Per
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Min
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Diff
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center font-weight-bold">
                Target
              </v-col>
            </v-row>
            <v-row dense class="ma-0 pa-0 ga-0">
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ formatCurrency(item.per_paycheck) }}
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ minimumLabel(item) }}
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ differenceLabel(item) }}
              </v-col>
              <v-col class="pa-0 ga-0 ma-0 text-center">
                {{ targetLabel(item) }}
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
  import { useBuckets } from "@/composables/bucketsComposable";
  import BucketForm from "@/components/BucketForm.vue";
  import NumberFlow from "@number-flow/vue";
  import { useDisplay } from "vuetify";
  import { useAuthStore } from "@/stores/auth";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";
  const { isOnline } = useOnlineStatus();

  const page = ref(1);
  const itemsPerPage = ref(5);
  const { smAndDown, mdAndUp } = useDisplay();
  const authStore = useAuthStore();
  const editBucketDialog = ref(false);
  const addBucketDialog = ref(false);
  const deleteBucketDialog = ref(false);
  const selectedBucket = ref([]);
  const editingBucket = ref({ id: 0 });
  const newBucketData = ref({
    id: 0,
    bucket: null,
    contribution_per_paycheck: "0",
    // Null, not zero: blank means "work the minimum out from the budgets and
    // the dated bills", which is what most buckets want.
    minimum_per_paycheck: null,
    target_balance: null,
    target_date: null,
    sweep: false,
    sweep_share: 1,
    priority: 100,
    lendable: true,
    receives_rewards: false,
    budget_ids: [],
    scope_tag_ids: [],
    active: true,
    account_id: null,
    reminder_id: null,
  });

  const {
    buckets,
    isLoading,
    addBucket,
    editBucket,
    removeBucket,
  } = useBuckets();

  const headers = ref([
    { title: "Bucket", key: "bucket" },
    { title: "Paycheck(per)", key: "contribution_per_paycheck", width: "140px" },
    { title: "Minimum", key: "minimum_per_paycheck", width: "140px" },
    { title: "Difference", key: "difference", width: "140px" },
    { title: "Target", key: "target_balance", width: "140px" },
  ]);

  // A blank minimum is not zero — it means the planner derives it — so it
  // reads as "auto" rather than as a dollar figure nobody entered.
  const minimumLabel = item =>
    item.minimum_per_paycheck === null || item.minimum_per_paycheck === undefined
      ? "auto"
      : formatCurrency(item.minimum_per_paycheck);

  const differenceLabel = item => {
    if (
      item.minimum_per_paycheck === null ||
      item.minimum_per_paycheck === undefined
    )
      return "—";
    return formatCurrency(item.per_paycheck - item.minimum_per_paycheck);
  };

  const targetLabel = item => {
    if (item.sweep) return "leftover";
    if (item.target_balance === null || item.target_balance === undefined)
      return "—";
    return formatCurrency(item.target_balance);
  };
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });

  const updateAddDialog = () => {
    addBucketDialog.value = false;
  };

  const updateEditDialog = () => {
    editBucketDialog.value = false;
  };

  const clickEditBucket = bucket => {
    editBucket(bucket);
    editBucketDialog.value = false;
    selectedBucket.value = [];
  };

  const clickDeleteBucket = bucket => {
    removeBucket(bucket);
    deleteBucketDialog.value = false;
    selectedBucket.value = [];
  };

  const clickAddBucket = bucket => {
    addBucket(bucket);
    addBucketDialog.value = false;
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
    buckets.value && itemsPerPage.value
      ? Math.ceil(buckets.value.buckets.length / itemsPerPage.value)
      : 1,
  );
  watch(
    () => selectedBucket.value,
    val => {
      if (val) {
        editingBucket.value = val[0];
      }
    },
  );
  function getRowProps({ item }) {
    let rowformat = "";
    const isSelected = selectedBucket.value.some(
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
