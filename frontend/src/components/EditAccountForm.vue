<template>
  <v-dialog width="800">
    <v-card min-height="550px">
      <v-card-text>
        <v-sheet border rounded>
          <v-container>
            <v-row dense>
              <v-col>
                <h4 class="text-h6 font-weight-bold mb-2">Account Info</h4>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-text-field
                  v-model="formData.account_name"
                  :rules="required"
                  @update:model-value="checkForm"
                  variant="outlined"
                  label="Account Name*"
                  density="comfortable"
                ></v-text-field>
              </v-col>
              <v-col>
                <v-autocomplete
                  clearable
                  label="Bank Name*"
                  :items="banks"
                  variant="outlined"
                  :loading="isLoading"
                  item-title="bank_name"
                  item-value="id"
                  v-model="formData.bank_id"
                  :rules="required"
                  @update:model-value="checkForm"
                  density="comfortable"
                ></v-autocomplete>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <span class="text-subtitle-2">Open Date</span>
                <VueDatePicker
                  v-model="formData.open_date"
                  timezone="America/New_York"
                  model-type="yyyy-MM-dd"
                  :enable-time-picker="false"
                  auto-apply
                  format="yyyy-MM-dd"
                  @update:model-value="checkForm"
                ></VueDatePicker>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-text-field
                  v-model="formData.opening_balance"
                  variant="outlined"
                  label="Opening Balance*"
                  :rules="required"
                  prefix="$"
                  @update:model-value="checkForm"
                  density="comfortable"
                ></v-text-field>
              </v-col>
              <v-col>
                <v-spacer></v-spacer>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
        <v-sheet border rounded v-if="props.account.account_type.id == 1">
          <v-container>
            <v-row dense>
              <v-col>
                <h4 class="text-h6 font-weight-bold mb-2">Credit Card Info</h4>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-text-field
                  v-model="formData.credit_limit"
                  variant="outlined"
                  label="Credit Limit*"
                  :rules="required"
                  prefix="$"
                  @update:model-value="checkForm"
                  density="comfortable"
                ></v-text-field>
              </v-col>
              <v-col>
                <v-text-field
                  v-model="formData.apy"
                  variant="outlined"
                  label="APY*"
                  :rules="required"
                  suffix="%"
                  @update:model-value="checkForm"
                  density="comfortable"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <span class="text-subtitle-2">Next Statment Date</span>
                <VueDatePicker
                  v-model="formData.next_cycle_date"
                  timezone="America/New_York"
                  model-type="yyyy-MM-dd"
                  :enable-time-picker="false"
                  auto-apply
                  format="yyyy-MM-dd"
                  @update:model-value="checkForm"
                ></VueDatePicker>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-select
                  label="Statment Cycle Length"
                  required
                  :items="intervals"
                  v-model="formData.statement_cycle_length"
                  @update:model-value="checkForm"
                  density="comfortable"
                >
                </v-select>
              </v-col>
              <v-col>
                <v-select
                  label="Statment Cycle Period"
                  required
                  :items="units"
                  v-model="formData.statement_cycle_period"
                  item-value="letter"
                  item-title="name"
                  @update:model-value="checkForm"
                  density="comfortable"
                >
                </v-select>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <span class="text-subtitle-2">Next Due Date</span>
                <VueDatePicker
                  v-model="formData.due_date"
                  timezone="America/New_York"
                  model-type="yyyy-MM-dd"
                  :enable-time-picker="false"
                  auto-apply
                  format="yyyy-MM-dd"
                  @update:model-value="checkForm"
                ></VueDatePicker>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-text-field
                  v-model="formData.last_statement_amount"
                  variant="outlined"
                  label="Last Statement Amount"
                  prefix="$"
                  @update:model-value="checkForm"
                  density="comfortable"
                ></v-text-field>
              </v-col>
              <v-col>
                <v-text-field
                  v-model="formData.rewards_amount"
                  variant="outlined"
                  label="Rewards Earned"
                  prefix="$"
                  @update:model-value="checkForm"
                  density="comfortable"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-sheet>
      </v-card-text>
      <v-card-actions
        ><v-spacer></v-spacer
        ><v-btn @click="emit('updateDialog', false)" color="secondary"
          >Close</v-btn
        ><v-btn
          @click="clickEditAccount()"
          color="secondary"
          :disabled="editSubmit"
          >Save</v-btn
        ></v-card-actions
      >
    </v-card>
  </v-dialog>
</template>
<script setup>
import { defineEmits, defineProps, ref, computed } from "vue";
import { useBanks } from "@/composables/banksComposable";
import { useAccountByID } from "@/composables/accountsComposable";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useMainStore } from "@/stores/main";

const { banks, isLoading } = useBanks();
const editSubmit = ref(true);
const mainstore = useMainStore();
const emit = defineEmits(["updateDialog"]);
const props = defineProps({
  account: Object,
});
const { editAccount } = useAccountByID(props.account.id);
const formData = ref({
  id: props.account.id,
  account_name: props.account.account_name,
  account_type_id: props.account.account_type.id,
  opening_balance: props.account.opening_balance,
  apy: props.account.apy,
  due_date: props.account.due_date,
  active: props.account.active,
  open_date: props.account.open_date,
  next_cycle_date: props.account.next_cycle_date,
  statement_cycle_length: props.account.statement_cycle_length,
  statement_cycle_period: props.account.statement_cycle_period,
  rewards_amount: props.account.rewards_amount,
  credit_limit: props.account.credit_limit,
  bank_id: props.account.bank.id,
  last_statement_amount: props.account.last_statement_amount,
});

const clickEditAccount = () => {
  editAccount(formData.value);
  emit("updateDialog", false);
};

const required = [
  value => {
    if (value) return true;

    return "This field is required.";
  },
];

const checkForm = async () => {
  if (
    formData.value.account_name !== null &&
    formData.value.account_name !== "" &&
    formData.value.bank_id !== null &&
    formData.value.bank_id !== "" &&
    formData.value.open_date !== null &&
    formData.value.open_date !== "" &&
    formData.value.opening_balance !== null &&
    formData.value.opening_balance !== "" &&
    formData.value.credit_limit !== null &&
    formData.value.credit_limit !== "" &&
    formData.value.apy !== null &&
    formData.value.apy !== ""
  ) {
    editSubmit.value = false;
  } else {
    editSubmit.value = true;
  }
};

const units = computed(() => {
  return mainstore.units;
});
const intervals = computed(() => {
  return mainstore.intervals;
});
</script>
