<template>
  <v-dialog width="800">
    <form @submit.prevent="submit">
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
                    v-model="account_name.value.value"
                    variant="outlined"
                    label="Account Name*"
                    density="comfortable"
                    :error-messages="account_name.errorMessage.value"
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
                    v-model="bank_id.value.value"
                    density="comfortable"
                    :error-messages="bank_id.errorMessage.value"
                  ></v-autocomplete>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-date-input
                    label="Open Date"
                    prepend-icon=""
                    prepend-inner-icon="$calendar"
                    variant="outlined"
                    :error-messages="open_date.errorMessage.value"
                    v-model="open_date.value.value"
                    density="compact"
                    clearable
                    @click:clear="open_date.value.value = null"
                  ></v-date-input>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="opening_balance.value.value"
                    variant="outlined"
                    label="Opening Balance*"
                    prefix="$"
                    density="comfortable"
                    :error-messages="opening_balance.errorMessage.value"
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
                  <h4 class="text-h6 font-weight-bold mb-2">
                    Credit Card Info
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-checkbox
                    v-model="calculate_payments.value.value"
                    label="Calculate Payments"
                    :error-messages="calculate_payments.errorMessage.value"
                  ></v-checkbox>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="credit_limit.value.value"
                    variant="outlined"
                    label="Credit Limit*"
                    prefix="$"
                    density="comfortable"
                    :error-messages="credit_limit.errorMessage.value"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="apy.value.value"
                    variant="outlined"
                    label="APY*"
                    suffix="%"
                    density="comfortable"
                    :error-messages="apy.errorMessage.value"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-date-input
                    label="Next Statement Date"
                    prepend-icon=""
                    prepend-inner-icon="$calendar"
                    variant="outlined"
                    :error-messages="next_cycle_date.errorMessage.value"
                    v-model="next_cycle_date.value.value"
                    density="compact"
                    clearable
                    @click:clear="next_cycle_date.value.value = null"
                  ></v-date-input>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-select
                    label="Statement Cycle Length"
                    :items="intervals"
                    v-model="statement_cycle_length.value.value"
                    density="comfortable"
                    clearable
                    :error-messages="statement_cycle_length.errorMessage.value"
                  ></v-select>
                </v-col>
                <v-col>
                  <v-select
                    label="Statment Cycle Period"
                    :items="units"
                    v-model="statement_cycle_period.value.value"
                    item-value="letter"
                    item-title="name"
                    density="comfortable"
                    clearable
                    :error-messages="statement_cycle_period.errorMessage.value"
                  ></v-select>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-date-input
                    label="Due Date"
                    prepend-icon=""
                    prepend-inner-icon="$calendar"
                    variant="outlined"
                    :error-messages="due_date.errorMessage.value"
                    v-model="due_date.value.value"
                    density="compact"
                    clearable
                    @click:clear="due_date.value.value = null"
                  ></v-date-input>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="last_statement_amount.value.value"
                    variant="outlined"
                    label="Last Statement Amount"
                    prefix="$"
                    density="comfortable"
                    clearable
                    :error-messages="last_statement_amount.errorMessage.value"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="rewards_amount.value.value"
                    variant="outlined"
                    label="Rewards Earned"
                    prefix="$"
                    density="comfortable"
                    :error-messages="rewards_amount.errorMessage.value"
                    clearable
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense v-if="calculate_payments.value.value">
                <v-col>
                  <v-autocomplete
                    label="Payment Strategy"
                    :items="payment_strategies"
                    variant="outlined"
                    item-title="strategy_name"
                    item-value="strategy_code"
                    v-model="payment_strategy.value.value"
                    density="compact"
                    :error-messages="payment_strategy.errorMessage.value"
                    clearable
                  ></v-autocomplete>
                </v-col>
                <v-col>
                  <v-autocomplete
                    clearable
                    label="Funding Account"
                    :items="accounts"
                    variant="outlined"
                    :loading="accounts_isLoading"
                    item-title="account_name"
                    item-value="id"
                    v-model="funding_account_id.value.value"
                    density="compact"
                    :error-messages="funding_account_id.errorMessage.value"
                    :return-object="false"
                  >
                    <template v-slot:item="{ props, item }">
                      <v-list-item
                        v-bind="props"
                        :title="item.raw.account_name"
                        :subtitle="item.raw.bank.bank_name"
                      >
                        <template v-slot:prepend>
                          <v-icon :icon="item.raw.account_type.icon"></v-icon>
                        </template>
                      </v-list-item>
                    </template>
                  </v-autocomplete>
                </v-col>
              </v-row>
              <v-row dense v-if="calculate_payments.value.value">
                <v-col v-if="payment_strategy.value.value == 'O'">
                  <v-text-field
                    v-model="payment_amount.value.value"
                    variant="outlined"
                    label="Payment Amount"
                    prefix="$"
                    density="comfortable"
                    clearable
                    :error-messages="payment_amount.errorMessage.value"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="minimum_payment_amount.value.value"
                    variant="outlined"
                    label="Monthly Minimum"
                    prefix="$"
                    density="comfortable"
                    clearable
                    :error-messages="minimum_payment_amount.errorMessage.value"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="closeForm()" color="secondary">Close</v-btn>
          <v-btn color="secondary" type="submit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
  import {
    defineEmits,
    defineProps,
    computed,
    onMounted,
    watchEffect,
    ref,
  } from "vue";
  import { useBanks } from "@/composables/banksComposable";
  import { useAccountByID } from "@/composables/accountsComposable";
  import { useMainStore } from "@/stores/main";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  const schema = yup.object({
    account_name: yup.string().required("Must provide an account name."),
    account_type_id: yup.number().required("Must select an account type."),
    opening_balance: yup.number().required("Must provide opening balance."),
    apy: yup.number().when("account_type_id", {
      is: 1,
      then: schema => schema.required("Must provide APY."),
      otherwise: schema => schema.notRequired(),
    }),
    due_date: yup.string().when(["account_type_id", "calculate_payments"], {
      is: (type, calc) => type === 1 && calc === true,
      then: schema => schema.required("Must enter a due date."),
      otherwise: schema => schema.notRequired(),
    }),
    active: yup.boolean().required("Must mark active/inactive."),
    open_date: yup.string().required("Must provide opening date."),
    next_cycle_date: yup
      .string()
      .when(["account_type_id", "calculate_payments"], {
        is: (type, calc) => type === 1 && calc === true,
        then: schema => schema.required("Must enter a statement date."),
        otherwise: schema => schema.notRequired(),
      }),
    statement_cycle_length: yup
      .number()
      .when(["account_type_id", "calculate_payments"], {
        is: (type, calc) => type === 1 && calc === true,
        then: schema =>
          schema
            .required("Must enter a statement length.")
            .positive("Must be greater than 0"),
        otherwise: schema => schema.notRequired(),
      }),
    statement_cycle_period: yup
      .string()
      .when(["account_type_id", "calculate_payments"], {
        is: (type, calc) => type === 1 && calc === true,
        then: schema => schema.required("Must enter a cycle period."),
        otherwise: schema => schema.notRequired(),
      }),
    bank_id: yup.number().required("Must select a bank."),
    last_statement_amount: yup
      .number()
      .when(["account_type_id", "calculate_payments"], {
        is: (type, calc) => type === 1 && calc === true,
        then: schema => schema.required("Must enter last statement amount."),
        otherwise: schema => schema.notRequired(),
      }),
    funding_account_id: yup
      .mixed()
      .when(["account_type_id", "calculate_payments"], {
        is: (type, calc) => type === 1 && calc === true,
        then: schema => schema.required("Must select funding account."),
        otherwise: schema => schema.notRequired(),
      }),
    payment_strategy: yup
      .mixed()
      .when(["account_type_id", "calculate_payments"], {
        is: (type, calc) => type === 1 && calc === true,
        then: schema => schema.required("Must select payment strategy."),
        otherwise: schema => schema.notRequired(),
      }),
    payment_amount: yup
      .number()
      .when(["account_type_id", "calculate_payments", "payment_strategy"], {
        is: (type, calc, strat) => type === 1 && calc === true && strat,
        then: schema => schema.required("Must enter a payment amount."),
        otherwise: schema => schema.notRequired(),
      }),
    minimum_payment_amount: yup
      .number()
      .when(["account_type_id", "calculate_payments"], {
        is: (type, calc) => type === 1 && calc === true,
        then: schema => schema.required("Must enter a minumum payment amount."),
        otherwise: schema => schema.notRequired(),
      }),
  });

  const { handleSubmit } = useForm({
    validationSchema: schema,
  });

  const id = useField("id");
  const account_name = useField("account_name");
  const account_type_id = useField("account_type_id");
  const opening_balance = useField("opening_balance");
  const apy = useField("apy");
  const due_date = useField("due_date");
  const active = useField("active");
  const open_date = useField("open_date");
  const next_cycle_date = useField("next_cycle_date");
  const statement_cycle_length = useField("statement_cycle_length");
  const statement_cycle_period = useField("statement_cycle_period");
  const rewards_amount = useField("rewards_amount");
  const credit_limit = useField("credit_limit");
  const bank_id = useField("bank_id");
  const last_statement_amount = useField("last_statement_amount");
  const funding_account_id = useField("funding_account_id");
  const calculate_payments = useField("calculate_payments");
  const calculate_interest = useField("calculate_interest");
  const payment_strategy = useField("payment_strategy");
  const payment_amount = useField("payment_amount");
  const minimum_payment_amount = useField("minimum_payment_amount");

  const { accounts, isLoading: accounts_isLoading } = useAccounts();
  const { banks, isLoading } = useBanks();
  const mainstore = useMainStore();
  const emit = defineEmits(["updateDialog"]);
  const props = defineProps({
    account: Object,
  });
  const { editAccount } = useAccountByID(props.account.id);
  const generalError = ref("");

  const submit = handleSubmit(
    values => {
      // Form is valid
      generalError.value = ""; // Clear any old error
      editAccount(values);
      closeForm();
    },
    errors => {
      // Validation failed
      generalError.value = "Please fix the errors below before saving.";
      console.log(errors);
    },
  );

  const payment_strategies = [
    { strategy_name: "Pay Full Balance", strategy_code: "F" },
    { strategy_name: "Pay Minimum Due", strategy_code: "M" },
    { strategy_name: "Custom Payment", strategy_code: "O" },
  ];

  const units = computed(() => {
    return mainstore.units;
  });
  const intervals = computed(() => {
    return mainstore.intervals;
  });

  const watchPassedFormData = () => {
    watchEffect(() => {
      if (props.account) {
        initializeFormData();
      }
    });
  };

  onMounted(() => {
    watchPassedFormData();
  });

  const closeForm = () => {
    emit("updateDialog", false);
    initializeFormData();
  };

  const initializeFormData = () => {
    id.value.value = props.account.id;
    account_name.value.value = props.account.account_name;
    account_type_id.value.value = props.account.account_type.id;
    opening_balance.value.value = props.account.opening_balance;
    apy.value.value = props.account.apy;
    due_date.value.value = parseDateAsLocal(props.account.due_date);
    active.value.value = props.account.active;
    open_date.value.value = parseDateAsLocal(props.account.open_date);
    next_cycle_date.value.value = parseDateAsLocal(
      props.account.next_cycle_date,
    );
    statement_cycle_length.value.value = props.account.statement_cycle_length;
    statement_cycle_period.value.value = props.account.statement_cycle_period;
    rewards_amount.value.value = props.account.rewards_amount;
    credit_limit.value.value = props.account.credit_limit;
    bank_id.value.value = props.account.bank.id;
    last_statement_amount.value.value = props.account.last_statement_amount;
    funding_account_id.value.value = props.account.funding_account
      ? props.account.funding_account.id
      : null;
    calculate_payments.value.value = props.account.calculate_payments;
    calculate_interest.value.value = props.account.calculate_interest;
    payment_strategy.value.value = props.account.payment_strategy;
    payment_amount.value.value = props.account.payment_amount;
    minimum_payment_amount.value.value = props.account.minimum_payment_amount;
  };

  function parseDateAsLocal(dateString) {
    if (!dateString) {
      console.error("parseDateAsLocal: Received null or undefined dateString");
      return null; // Or handle appropriately
    }
    const [year, month, day] = dateString.split("-").map(Number);
    return new Date(year, month - 1, day); // No timezone adjustment
  }
</script>
