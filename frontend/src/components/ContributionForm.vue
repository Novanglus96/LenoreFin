<template>
  <v-dialog :fullscreen="smAndDown" :width="smAndDown ? undefined : '800'">
    <form @submit.prevent="submit">
      <v-card min-height="550px">
        <v-card-text>
          <v-sheet border rounded>
            <v-container>
              <v-row dense>
                <v-col>
                  <h4 class="text-h6 font-weight-bold mb-2">
                    {{ props.isEdit ? "Edit" : "Add" }} Contribution
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="contribution.value.value"
                    variant="outlined"
                    label="Contribution"
                    density="compact"
                    :error-messages="contribution.errorMessage.value"
                    :counter="254"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col :cols="smAndDown ? 6 : 3">
                  <v-text-field
                    v-model="per_paycheck.value.value"
                    variant="outlined"
                    label="Paycheck(per)"
                    density="compact"
                    :error-messages="per_paycheck.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    @update:modelValue="updateDifference"
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 6 : 3">
                  <v-text-field
                    v-model="emergency_amt.value.value"
                    variant="outlined"
                    label="Emergency Amt"
                    density="compact"
                    :error-messages="emergency_amt.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    @update:modelValue="updateDifference"
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 6 : 3">
                  <v-text-field
                    v-model="emergency_diff.value.value"
                    variant="outlined"
                    label="Difference"
                    density="compact"
                    :error-messages="emergency_diff.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    disabled
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 6 : 3">
                  <v-text-field
                    v-model="cap.value.value"
                    variant="outlined"
                    label="Cap"
                    density="compact"
                    :error-messages="cap.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
          <!-- Planner section: what this contribution funds, how the money
               actually moves, and what the account is supposed to do. -->
          <v-sheet border rounded class="mt-3">
            <v-container>
              <v-row dense>
                <v-col>
                  <h4 class="text-subtitle-1 font-weight-bold mb-1">Planner</h4>
                  <div class="text-caption text-medium-emphasis mb-2">
                    Link an account to get suggestions. The reminder is the
                    transfer that actually moves this money.
                  </div>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col :cols="smAndDown ? 12 : 6">
                  <v-select
                    v-model="account_id.value.value"
                    :items="accountOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    label="Funds account"
                    density="compact"
                    clearable
                    :error-messages="account_id.errorMessage.value"
                  ></v-select>
                </v-col>
                <v-col :cols="smAndDown ? 12 : 6">
                  <v-select
                    v-model="reminder_id.value.value"
                    :items="reminderOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    label="Recurring transfer"
                    density="compact"
                    clearable
                    :disabled="!account_id.value.value"
                    :hint="
                      account_id.value.value
                        ? 'Only transfers into the selected account'
                        : 'Pick an account first'
                    "
                    persistent-hint
                    :error-messages="reminder_id.errorMessage.value"
                  ></v-select>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col :cols="smAndDown ? 12 : 4">
                  <v-select
                    v-model="goal_type.value.value"
                    :items="goalOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    label="Goal"
                    density="compact"
                    :error-messages="goal_type.errorMessage.value"
                  ></v-select>
                </v-col>
                <v-col
                  :cols="smAndDown ? 12 : 4"
                  v-if="['target', 'floor', 'grow', 'budget'].includes(goal_type.value.value)"
                >
                  <v-text-field
                    v-model="goal_amount.value.value"
                    variant="outlined"
                    :label="amountLabel"
                    density="compact"
                    type="number"
                    step="1.00"
                    prefix="$"
                    :error-messages="goal_amount.errorMessage.value"
                  ></v-text-field>
                </v-col>
                <v-col
                  :cols="smAndDown ? 12 : 4"
                  v-if="goal_type.value.value === 'target'"
                >
                  <v-text-field
                    v-model="goal_date.value.value"
                    variant="outlined"
                    label="Reach it by"
                    density="compact"
                    type="date"
                    :error-messages="goal_date.errorMessage.value"
                  ></v-text-field>
                </v-col>
                <v-col
                  :cols="smAndDown ? 12 : 4"
                  v-if="goal_type.value.value === 'grow'"
                >
                  <v-text-field
                    v-model="goal_rate.value.value"
                    variant="outlined"
                    label="Or annual rate"
                    density="compact"
                    type="number"
                    step="0.25"
                    suffix="%"
                    hint="Overrides the amount when set"
                    persistent-hint
                    :error-messages="goal_rate.errorMessage.value"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-checkbox
                    v-model="active.value.value"
                    :error-messages="active.errorMessage.value"
                    label="Active"
                    type="checkbox"
                    :value="true"
                  ></v-checkbox>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="clickClose" color="primary">Close</v-btn>
          <v-btn color="primary" type="submit" :disabled="!isOnline">
            {{ props.isEdit ? "Save Changes" : "Add Contribution" }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
  import { computed, defineEmits, defineProps, watchEffect, onMounted } from "vue";
  import { useDisplay } from "vuetify";
  import { useOnlineStatus } from "@/composables/useOnlineStatus";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useReminders } from "@/composables/remindersComposable";
  import { useField, useForm } from "vee-validate";
  const { isOnline } = useOnlineStatus();

  const { smAndDown } = useDisplay();
  const { handleSubmit } = useForm({
    validationSchema: {
      contribution(value) {
        if (value?.length >= 2 && value?.length <= 254) return true;

        return "Contribution needs to be at least 2 characters, and less than 254.";
      },
      per_paycheck(value) {
        if (value == null || value === "")
          return "Paycheck amount is required.";
        if (parseFloat(value) < 1)
          return "Paycheck amount must be more than 0.";
        if (parseFloat(value) < parseFloat(emergency_amt.value.value))
          return "Paycheck amount can't be less than emergency amount.";

        return true;
      },
      emergency_amt(value) {
        if (value == null || value === "")
          return "Emergency amount is required.";
        if (parseFloat(value) < 0) return "Emergency amount must be positive.";
        if (parseFloat(value) > parseFloat(per_paycheck.value.value))
          return "Emergency amount can't be greater than paycheck amount.";

        return true;
      },
      cap(value) {
        if (value == null || value === "")
          return "You must specify a cap(Can be 0).";
        if (value < 0) return "Cap amount must be positive.";

        return true;
      },
      account_id(value) {
        if (goal_type.value.value && goal_type.value.value !== "none" && !value)
          return "Pick the account this goal measures.";

        return true;
      },
      reminder_id() {
        return true;
      },
      goal_type() {
        return true;
      },
      goal_amount(value) {
        const goal = goal_type.value.value;
        if (goal === "budget") {
          if (value == null || value === "" || parseFloat(value) <= 0)
            return "A budget needs the amount to fund per year.";
        }
        if (goal === "target") {
          if (value == null || value === "" || parseFloat(value) <= 0)
            return "A target needs a balance greater than 0.";
        }
        if (goal === "floor") {
          if (value == null || value === "") return "A floor needs a balance.";
          if (parseFloat(value) < 0) return "Floor must be positive.";
        }
        if (goal === "grow") {
          const rate = parseFloat(goal_rate.value.value);
          const amt = parseFloat(value);
          if (!rate && !amt)
            return "Set a growth amount per month, or an annual rate.";
        }

        return true;
      },
      goal_date(value) {
        if (goal_type.value.value !== "target") return true;
        if (!value) return "A target needs a date to reach it by.";
        // A past date cannot be solved for — there are no paychecks left.
        if (new Date(value) <= new Date())
          return "The target date must be in the future.";

        return true;
      },
      goal_rate(value) {
        if (value != null && value !== "" && parseFloat(value) < 0)
          return "Rate must be positive.";

        return true;
      },
    },
  });

  const id = useField("id");
  const contribution = useField("contribution");
  const per_paycheck = useField("per_paycheck");
  const emergency_diff = useField("emergency_diff");
  const emergency_amt = useField("emergency_amt");
  const cap = useField("cap");
  const active = useField("active");
  const account_id = useField("account_id");
  const reminder_id = useField("reminder_id");
  const goal_type = useField("goal_type");
  const goal_amount = useField("goal_amount");
  const goal_date = useField("goal_date");
  const goal_rate = useField("goal_rate");

  const { accounts } = useAccounts(false);
  const { reminders } = useReminders();

  const goalOptions = [
    { title: "No goal", value: "none" },
    { title: "Cover spending, never dip below a floor", value: "floor" },
    { title: "Cover obligations, hold the buffer", value: "hold" },
    { title: "Fund a set amount per year", value: "budget" },
    { title: "Contribute whatever is left over", value: "maximise" },
    { title: "Reach a target by a date", value: "target" },
    { title: "Grow by an amount or rate", value: "grow" },
  ];

  const amountLabel = computed(() => {
    if (goal_type.value.value === "target") return "Target balance";
    if (goal_type.value.value === "floor") return "Floor balance";
    if (goal_type.value.value === "budget") return "Amount per year";
    return "Growth per month";
  });

  const accountOptions = computed(() =>
    (accounts.value ?? []).map(a => ({
      title: a.account_name,
      value: a.id,
    })),
  );

  // Only transfers landing in the chosen account can fund it, and the backend
  // rejects anything else — so the list is filtered rather than letting the
  // user pick something that will bounce on save.
  const reminderOptions = computed(() => {
    const accountId = account_id.value.value;
    if (!accountId) return [];
    return (reminders.value ?? [])
      .filter(r => r.reminder_destination_account?.id === accountId)
      .map(r => ({
        title: `${r.description} ($${r.amount})`,
        value: r.id,
      }));
  });

  const props = defineProps({
    isEdit: {
      type: Boolean,
      default: false,
    },
    passedFormData: Object,
  });

  const watchPassedFormData = () => {
    watchEffect(() => {
      if (props.passedFormData) {
        id.value.value = props.passedFormData.id;
        contribution.value.value = props.passedFormData.contribution;
        per_paycheck.value.value = props.passedFormData.per_paycheck;
        emergency_diff.value.value = props.passedFormData.emergency_diff;
        emergency_amt.value.value = props.passedFormData.emergency_amt;
        cap.value.value = props.passedFormData.cap;
        active.value.value = props.passedFormData.active;
        account_id.value.value = props.passedFormData.account_id ?? null;
        reminder_id.value.value = props.passedFormData.reminder_id ?? null;
        goal_type.value.value = props.passedFormData.goal_type ?? "none";
        goal_amount.value.value = props.passedFormData.goal_amount ?? "0";
        goal_date.value.value = props.passedFormData.goal_date ?? null;
        goal_rate.value.value = props.passedFormData.goal_rate ?? "0";
      }
    });
  };
  const submit = handleSubmit(values => {
    if (props.isEdit) {
      emit("editContribution", values);
    } else {
      emit("addContribution", values);
    }
    emit("updateDialog", false);
  });

  const emit = defineEmits([
    "updateDialog",
    "addContribution",
    "editContribution",
  ]);

  const clickClose = () => {
    emit("updateDialog", false);
  };

  const updateDifference = () => {
    if (per_paycheck.value.value && emergency_amt.value.value) {
      emergency_diff.value.value =
        parseFloat(per_paycheck.value.value) -
        parseFloat(emergency_amt.value.value);
    }
  };

  onMounted(() => {
    watchPassedFormData();
  });
</script>
