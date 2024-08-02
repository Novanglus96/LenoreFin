<template>
  <v-form @submit.prevent>
    <v-card v-if="page1">
      <!--TODO: use v-stepper here-->
      <v-card-title>What bank is this account with?</v-card-title>
      <v-card-text>
        <v-row dense>
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
              @update:model-value="checkNext"
            ></v-autocomplete>
          </v-col>
        </v-row>
        <v-row dense>
          <v-col>
            <AddBankForm />
          </v-col>
        </v-row>
        <v-row dense>
          <v-col>
            <v-autocomplete
              clearable
              label="Account Type*"
              :items="account_types"
              variant="outlined"
              :loading="account_types_isLoading"
              item-title="account_type"
              item-value="id"
              v-model="formData.account_type_id"
              :rules="required"
              @update:model-value="checkNext"
            ></v-autocomplete>
          </v-col>
        </v-row>
        <v-row dense>
          <v-col>
            <v-text-field
              v-model="formData.account_name"
              :rules="required"
              @update:model-value="checkNext"
              variant="outlined"
              label="Name Your Account*"
            ></v-text-field>
            <span class="text-red text-subtitle-2 font-italic">* required</span>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn
          @click="
            page1
              ? ((page1 = false), (page2 = true))
              : ((page1 = true), (page2 = false))
          "
          :disabled="next1"
        >
          Next
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-if="page2" min-height="500">
      <v-card-title>Just need a little more information...</v-card-title>
      <v-card-text>
        <v-row dense>
          <v-col>
            When did you open this account?*
            <VueDatePicker
              v-model="formData.open_date"
              timezone="America/New_York"
              model-type="yyyy-MM-dd"
              :enable-time-picker="false"
              auto-apply
              format="yyyy-MM-dd"
              @update:model-value="checkNext"
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
              @update:model-value="checkNext"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row dense v-if="formData.account_type_id == 1">
          <v-col>
            <v-text-field
              v-model="formData.apy"
              variant="outlined"
              label="APY*"
              :rules="required"
              suffix="%"
              @update:model-value="checkNext"
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              v-model="formData.credit_limit"
              variant="outlined"
              label="Credit Limit*"
              :rules="required"
              prefix="$"
              @update:model-value="checkNext"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row dense v-if="formData.account_type_id == 1">
          <v-col>
            When is your next due date?
            <VueDatePicker
              v-model="formData.due_date"
              timezone="America/New_York"
              model-type="yyyy-MM-dd"
              :enable-time-picker="false"
              auto-apply
              format="yyyy-MM-dd"
            ></VueDatePicker>
          </v-col>
          <v-col>
            When does this statment period end?
            <VueDatePicker
              v-model="formData.next_cycle_date"
              timezone="America/New_York"
              model-type="yyyy-MM-dd"
              :enable-time-picker="false"
              auto-apply
              format="yyyy-MM-dd"
            ></VueDatePicker>
          </v-col>
        </v-row>
        <v-row dense v-if="formData.account_type_id == 1">
          <v-col>
            <v-select
              label="Statment Cycle Length"
              required
              :items="intervals"
              v-model="formData.statement_cycle_length"
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
            >
            </v-select>
          </v-col>
        </v-row>
        <span class="text-red text-subtitle-2 font-italic">* required</span>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="goBack"> Back </v-btn>
        <v-btn @click="submitForm" :disabled="submitDisabled"> Submit </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
</template>
<script setup>
import { useBanks } from "@/composables/banksComposable";
import { useAccountTypes } from "@/composables/accountTypesComposable";
import { useAccounts } from "@/composables/accountsComposable";
import { ref, computed } from "vue";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useMainStore } from "@/stores/main";
import { useRouter } from "vue-router";
import AddBankForm from "@/components/AddBankForm.vue";

const router = useRouter();
const today = new Date();
const year = today.getFullYear();
const month = String(today.getMonth() + 1).padStart(2, "0");
const day = String(today.getDate()).padStart(2, "0");

const formattedDate = `${year}-${month}-${day}`;
const mainstore = useMainStore();
const required = [
  value => {
    if (value) return true;

    return "This field is required.";
  },
];
const formData = ref({
  account_name: null,
  account_type_id: null,
  opening_balance: 0,
  apy: 0.0,
  due_date: null,
  active: true,
  open_date: formattedDate,
  next_cycle_date: null,
  statement_cycle_length: null,
  statement_cycle_period: null,
  credit_limit: 0,
  bank_id: null,
});

const submitDisabled = ref(true);
const page1 = ref(true);
const next1 = ref(true);
const page2 = ref(false);
const { banks, isLoading } = useBanks();
const { account_types, isLoading: account_types_isLoading } = useAccountTypes();
const { addAccount } = useAccounts();
const goBack = async () => {
  page2.value = false;
  page1.value = true;
  formData.value.apy = 0.0;
  formData.value.due_date = null;
  formData.value.next_cycle_date = null;
  formData.value.statement_cycle_length = null;
  formData.value.statement_cycle_period = null;
  formData.value.credit_limit = 0;
};

const checkNext = async () => {
  if (
    formData.value.account_name !== null &&
    formData.value.bank_id !== null &&
    formData.value.account_name !== "" &&
    formData.value.account_type_id !== null
  ) {
    next1.value = false;
  } else {
    next1.value = true;
  }
  if (
    formData.value.apy !== null &&
    formData.value.apy !== "" &&
    formData.value.credit_limit !== null &&
    formData.value.credit_limit !== "" &&
    formData.value.open_date !== null &&
    formData.value.open_date !== "" &&
    formData.value.opening_balance !== null &&
    formData.value.opening_balance !== ""
  ) {
    submitDisabled.value = false;
  } else {
    submitDisabled.value = true;
  }
};
const units = computed(() => {
  return mainstore.units;
});
const intervals = computed(() => {
  return mainstore.intervals;
});
const submitForm = () => {
  addAccount(formData.value);
  router.push("/");
};
</script>
