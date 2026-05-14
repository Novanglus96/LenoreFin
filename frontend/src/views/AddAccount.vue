<template>
  <form @submit.prevent="submit">
    <v-card v-if="page1">
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
              v-model="bank_id.value.value"
              :error-messages="bank_id.errorMessage.value"
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
              v-model="account_type_id.value.value"
              :error-messages="account_type_id.errorMessage.value"
            ></v-autocomplete>
          </v-col>
        </v-row>
        <v-row dense>
          <v-col>
            <v-text-field
              v-model="account_name.value.value"
              :error-messages="account_name.errorMessage.value"
              variant="outlined"
              label="Name Your Account*"
            ></v-text-field>
            <span class="text-error text-subtitle-2 font-italic">
              * required
            </span>
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="goToPage2" :disabled="!page1Valid">Next</v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-if="page2" min-height="500">
      <v-card-title>Just need a little more information...</v-card-title>
      <v-card-text>
        <v-row dense>
          <v-col>
            When did you open this account?*
            <VueDatePicker
              v-model="open_date.value.value"
              timezone="America/New_York"
              model-type="yyyy-MM-dd"
              :enable-time-picker="false"
              auto-apply
              format="yyyy-MM-dd"
            ></VueDatePicker>
            <span
              class="text-error text-caption"
              v-if="open_date.errorMessage.value"
            >
              {{ open_date.errorMessage.value }}
            </span>
          </v-col>
        </v-row>
        <v-row dense>
          <v-col>
            <v-text-field
              v-model="opening_balance.value.value"
              variant="outlined"
              label="Opening Balance*"
              :error-messages="opening_balance.errorMessage.value"
              prefix="$"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row dense v-if="account_type_id.value.value == 1">
          <v-col>
            <v-text-field
              v-model="annual_rate.value.value"
              variant="outlined"
              label="Annual Rate (APR/APY)*"
              :error-messages="annual_rate.errorMessage.value"
              suffix="%"
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              v-model="credit_limit.value.value"
              variant="outlined"
              label="Credit Limit*"
              :error-messages="credit_limit.errorMessage.value"
              prefix="$"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row dense v-if="account_type_id.value.value == 1">
          <v-col>
            When is your next due date?
            <VueDatePicker
              v-model="due_date.value.value"
              timezone="America/New_York"
              model-type="yyyy-MM-dd"
              :enable-time-picker="false"
              auto-apply
              format="yyyy-MM-dd"
            ></VueDatePicker>
          </v-col>
          <v-col>
            When does this statement period end?
            <VueDatePicker
              v-model="next_cycle_date.value.value"
              timezone="America/New_York"
              model-type="yyyy-MM-dd"
              :enable-time-picker="false"
              auto-apply
              format="yyyy-MM-dd"
            ></VueDatePicker>
          </v-col>
        </v-row>
        <v-row dense v-if="account_type_id.value.value == 1">
          <v-col>
            <v-select
              label="Statement Cycle Length"
              :items="intervals"
              v-model="statement_cycle_length.value.value"
            ></v-select>
          </v-col>
          <v-col>
            <v-select
              label="Statement Cycle Period"
              :items="units"
              v-model="statement_cycle_period.value.value"
              item-value="letter"
              item-title="name"
            ></v-select>
          </v-col>
        </v-row>
        <span class="text-error text-subtitle-2 font-italic">* required</span>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="goBack">Back</v-btn>
        <v-btn type="submit">Submit</v-btn>
      </v-card-actions>
    </v-card>
  </form>
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
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  const router = useRouter();
  const today = new Date();
  const formattedDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  const mainstore = useMainStore();

  const schema = yup.object({
    bank_id: yup
      .number()
      .typeError("Bank is required.")
      .required("Bank is required."),
    account_type_id: yup
      .number()
      .typeError("Account type is required.")
      .required("Account type is required."),
    account_name: yup.string().required("Account name is required."),
    open_date: yup.string().nullable().required("Open date is required."),
    opening_balance: yup
      .number()
      .typeError("Opening balance is required.")
      .required("Opening balance is required."),
    annual_rate: yup.number().when("account_type_id", {
      is: 1,
      then: schema =>
        schema
          .typeError("Annual rate is required.")
          .required("Annual rate is required."),
      otherwise: schema => schema.notRequired(),
    }),
    credit_limit: yup.number().when("account_type_id", {
      is: 1,
      then: schema =>
        schema
          .typeError("Credit limit is required.")
          .required("Credit limit is required."),
      otherwise: schema => schema.notRequired(),
    }),
    due_date: yup.string().nullable().notRequired(),
    next_cycle_date: yup.string().nullable().notRequired(),
    statement_cycle_length: yup.number().nullable().notRequired(),
    statement_cycle_period: yup.string().nullable().notRequired(),
  });

  const { handleSubmit } = useForm({ validationSchema: schema });

  const bank_id = useField("bank_id");
  const account_type_id = useField("account_type_id");
  const account_name = useField("account_name");
  const open_date = useField("open_date");
  const opening_balance = useField("opening_balance");
  const annual_rate = useField("annual_rate");
  const credit_limit = useField("credit_limit");
  const due_date = useField("due_date");
  const next_cycle_date = useField("next_cycle_date");
  const statement_cycle_length = useField("statement_cycle_length");
  const statement_cycle_period = useField("statement_cycle_period");

  // Initialise defaults
  open_date.value.value = formattedDate;
  opening_balance.value.value = 0;
  annual_rate.value.value = 0.0;
  credit_limit.value.value = 0;

  const page1 = ref(true);
  const page2 = ref(false);

  const page1Valid = computed(
    () =>
      !!bank_id.value.value &&
      !!account_type_id.value.value &&
      !!account_name.value.value,
  );

  const { banks, isLoading } = useBanks();
  const { account_types, isLoading: account_types_isLoading } =
    useAccountTypes();
  const { addAccount } = useAccounts();

  const goToPage2 = () => {
    page1.value = false;
    page2.value = true;
  };

  const goBack = () => {
    page2.value = false;
    page1.value = true;
    annual_rate.value.value = 0.0;
    due_date.value.value = null;
    next_cycle_date.value.value = null;
    statement_cycle_length.value.value = null;
    statement_cycle_period.value.value = null;
    credit_limit.value.value = 0;
  };

  const submit = handleSubmit(values => {
    addAccount({ ...values, active: true });
    router.push("/");
  });

  const units = computed(() => mainstore.units);
  const intervals = computed(() => mainstore.intervals);
</script>
