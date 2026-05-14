<template>
  <v-dialog fullscreen persistent>
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
                    :error-messages="account_name.errorMessage.value"
                    variant="outlined"
                    label="Account Name*"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
              </v-row>
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
                    density="comfortable"
                  ></v-autocomplete>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <span class="text-subtitle-2">Open Date</span>
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
                    :error-messages="opening_balance.errorMessage.value"
                    variant="outlined"
                    label="Opening Balance*"
                    prefix="$"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-spacer></v-spacer>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
          <v-sheet border rounded v-if="!props.account.is_parent_account">
            <v-container>
              <v-row dense>
                <v-col>
                  <h4 class="text-h6 font-weight-bold mb-2">Parent Account</h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-autocomplete
                    clearable
                    label="Parent Account"
                    :items="sameTypeAccounts"
                    variant="outlined"
                    :loading="accounts_isLoading"
                    item-title="account_name"
                    item-value="id"
                    v-model="parent_account_id.value.value"
                    density="comfortable"
                    hint="Roll this account up under a parent. Interest is calculated at the parent level."
                    persistent-hint
                  ></v-autocomplete>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
          <v-sheet border rounded v-if="props.account.is_parent_account">
            <v-container>
              <v-row dense>
                <v-col>
                  <h4 class="text-h6 font-weight-bold mb-2">Child Accounts</h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-autocomplete
                    clearable
                    label="Interest Child Account"
                    :items="childAccounts"
                    variant="outlined"
                    item-title="account_name"
                    item-value="id"
                    v-model="interest_child_account_id.value.value"
                    density="comfortable"
                    hint="Interest forecast deposits will be posted to this child account."
                    persistent-hint
                  ></v-autocomplete>
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
                    v-model="credit_limit.value.value"
                    :error-messages="credit_limit.errorMessage.value"
                    variant="outlined"
                    label="Credit Limit*"
                    prefix="$"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="annual_rate.value.value"
                    :error-messages="annual_rate.errorMessage.value"
                    variant="outlined"
                    label="Annual Rate(APR/APY)*"
                    suffix="%"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <span class="text-subtitle-2">Next Statement Date</span>
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
              <v-row dense>
                <v-col>
                  <v-select
                    label="Statement Cycle Length"
                    :items="intervals"
                    v-model="statement_cycle_length.value.value"
                    density="comfortable"
                  ></v-select>
                </v-col>
                <v-col>
                  <v-select
                    label="Statement Cycle Period"
                    :items="units"
                    v-model="statement_cycle_period.value.value"
                    item-value="letter"
                    item-title="name"
                    density="comfortable"
                  ></v-select>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <span class="text-subtitle-2">Next Due Date</span>
                  <VueDatePicker
                    v-model="due_date.value.value"
                    timezone="America/New_York"
                    model-type="yyyy-MM-dd"
                    :enable-time-picker="false"
                    auto-apply
                    format="yyyy-MM-dd"
                  ></VueDatePicker>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="statement_balance.value.value"
                    variant="outlined"
                    label="Statement Balance"
                    prefix="$"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-text-field
                    v-model="rewards_amount.value.value"
                    variant="outlined"
                    label="Rewards Earned"
                    prefix="$"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
          <v-sheet
            border
            rounded
            v-if="['savings', 'investment'].includes(props.account.account_type.slug) && !parent_account_id.value.value"
          >
            <v-container>
              <v-row dense>
                <v-col>
                  <h4 class="text-h6 font-weight-bold mb-2">
                    Savings / Investment Info
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-checkbox
                    v-model="calculate_interest.value.value"
                    label="Calculate Interest"
                  ></v-checkbox>
                </v-col>
              </v-row>
              <v-row dense v-if="calculate_interest.value.value">
                <v-col>
                  <v-text-field
                    v-model="annual_rate.value.value"
                    :error-messages="annual_rate.errorMessage.value"
                    variant="outlined"
                    label="Annual Rate (APY)"
                    suffix="%"
                    density="comfortable"
                  ></v-text-field>
                </v-col>
                <v-col>
                  <v-select
                    label="Interest Deposit Day"
                    :items="intervals"
                    v-model="interest_deposit_day.value.value"
                    density="comfortable"
                    clearable
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="emit('updateDialog', false)" color="primary">
            Close
          </v-btn>
          <v-btn color="primary" type="submit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
  import { defineEmits, defineProps, onMounted, watchEffect, computed } from "vue";
  import { useBanks } from "@/composables/banksComposable";
  import { useAccountByID, useAccounts } from "@/composables/accountsComposable";
  import VueDatePicker from "@vuepic/vue-datepicker";
  import "@vuepic/vue-datepicker/dist/main.css";
  import { useMainStore } from "@/stores/main";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  const schema = yup.object({
    account_name: yup.string().required("Must provide an account name."),
    bank_id: yup.number().required("Must select a bank."),
    open_date: yup.string().required("Must provide opening date."),
    opening_balance: yup.number().required("Must provide opening balance."),
    annual_rate: yup.number().when(["account_type_id", "calculate_interest"], {
      is: (type, calc) => type === 1 || ((type === 3 || type === 4) && calc === true),
      then: schema => schema.required("Must provide annual rate (APR/APY)."),
      otherwise: schema => schema.nullable().notRequired(),
    }),
    credit_limit: yup.number().when("account_type_id", {
      is: 1,
      then: schema => schema.required("Must provide credit limit."),
      otherwise: schema => schema.nullable().notRequired(),
    }),
    due_date: yup.string().nullable().notRequired(),
    next_cycle_date: yup.string().nullable().notRequired(),
    statement_cycle_length: yup.number().nullable().notRequired(),
    statement_cycle_period: yup.string().nullable().notRequired(),
    statement_balance: yup.number().nullable().notRequired(),
    rewards_amount: yup.number().nullable().notRequired(),
    calculate_interest: yup.boolean().nullable().notRequired(),
    interest_deposit_day: yup.number().nullable().notRequired(),
    parent_account_id: yup.number().nullable().notRequired(),
    interest_child_account_id: yup.number().nullable().notRequired(),
    account_type_id: yup.number().notRequired(),
    active: yup.boolean().notRequired(),
  });

  const { handleSubmit } = useForm({ validationSchema: schema });

  const account_name = useField("account_name");
  const bank_id = useField("bank_id");
  const open_date = useField("open_date");
  const opening_balance = useField("opening_balance");
  const annual_rate = useField("annual_rate");
  const credit_limit = useField("credit_limit");
  const due_date = useField("due_date");
  const next_cycle_date = useField("next_cycle_date");
  const statement_cycle_length = useField("statement_cycle_length");
  const statement_cycle_period = useField("statement_cycle_period");
  const statement_balance = useField("statement_balance");
  const rewards_amount = useField("rewards_amount");
  const calculate_interest = useField("calculate_interest");
  const interest_deposit_day = useField("interest_deposit_day");
  const parent_account_id = useField("parent_account_id");
  const interest_child_account_id = useField("interest_child_account_id");
  const account_type_id = useField("account_type_id");
  const active = useField("active");

  const { banks, isLoading } = useBanks();
  const { accounts, isLoading: accounts_isLoading } = useAccounts();
  const mainstore = useMainStore();
  const emit = defineEmits(["updateDialog"]);
  const props = defineProps({ account: Object });
  const { editAccount } = useAccountByID(props.account.id);

  const sameTypeAccounts = computed(() => {
    if (!accounts.value) return [];
    return accounts.value.filter(
      a =>
        a.id !== props.account.id &&
        a.account_type.id === props.account.account_type.id &&
        a.parent_account_id === null,
    );
  });

  const childAccounts = computed(() => {
    if (!accounts.value) return [];
    return accounts.value.filter(a => a.parent_account_id === props.account.id);
  });

  const submit = handleSubmit(values => {
    editAccount(values);
    emit("updateDialog", false);
  });

  const units = computed(() => mainstore.units);
  const intervals = computed(() => mainstore.intervals);

  const initializeFormData = () => {
    account_name.value.value = props.account.account_name;
    bank_id.value.value = props.account.bank.id;
    open_date.value.value = props.account.open_date;
    opening_balance.value.value = props.account.opening_balance;
    annual_rate.value.value = props.account.annual_rate;
    credit_limit.value.value = props.account.credit_limit;
    due_date.value.value = props.account.due_date ?? null;
    next_cycle_date.value.value = props.account.next_cycle_date ?? null;
    statement_cycle_length.value.value = props.account.statement_cycle_length ?? null;
    statement_cycle_period.value.value = props.account.statement_cycle_period ?? null;
    statement_balance.value.value = props.account.statement_balance ?? null;
    rewards_amount.value.value = props.account.rewards_amount ?? null;
    calculate_interest.value.value = props.account.calculate_interest ?? false;
    interest_deposit_day.value.value = props.account.interest_deposit_day ?? null;
    parent_account_id.value.value = props.account.parent_account_id ?? null;
    interest_child_account_id.value.value = props.account.interest_child_account_id ?? null;
    account_type_id.value.value = props.account.account_type.id;
    active.value.value = props.account.active;
  };

  onMounted(() => {
    watchEffect(() => {
      if (props.account) {
        initializeFormData();
      }
    });
  });
</script>
