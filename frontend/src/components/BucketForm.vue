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
                    {{ props.isEdit ? "Edit" : "Add" }} Bucket
                  </h4>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-text-field
                    v-model="name.value.value"
                    variant="outlined"
                    label="Bucket"
                    density="compact"
                    :error-messages="name.errorMessage.value"
                    :counter="254"
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col :cols="smAndDown ? 6 : 4">
                  <v-text-field
                    v-model="contribution_per_paycheck.value.value"
                    variant="outlined"
                    label="Paycheck(per)"
                    density="compact"
                    :error-messages="contribution_per_paycheck.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    hint="What the transfer moves today"
                    persistent-hint
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 6 : 4">
                  <v-text-field
                    v-model="minimum_per_paycheck.value.value"
                    variant="outlined"
                    label="Minimum"
                    density="compact"
                    :error-messages="minimum_per_paycheck.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    hint="Blank works it out from budgets and bills"
                    persistent-hint
                    clearable
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 6 : 4">
                  <v-text-field
                    v-model="buffer.value.value"
                    variant="outlined"
                    label="Buffer"
                    density="compact"
                    :error-messages="buffer.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    hint="Cushion to hold on its worst day"
                    persistent-hint
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 6 : 4">
                  <v-text-field
                    v-model="difference"
                    variant="outlined"
                    label="Difference"
                    density="compact"
                    type="number"
                    prefix="$"
                    hint="Freed up in emergency mode"
                    persistent-hint
                    disabled
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-sheet>
          <!-- Planner section: what this bucket funds, how the money
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
                    label="Account"
                    density="compact"
                    :error-messages="account_id.errorMessage.value"
                    clearable
                  ></v-select>
                </v-col>
                <v-col :cols="smAndDown ? 12 : 6">
                  <v-select
                    v-model="reminder_id.value.value"
                    :items="reminderOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    label="Funded by reminder"
                    density="compact"
                    :error-messages="reminder_id.errorMessage.value"
                    :disabled="!account_id.value.value"
                    :hint="
                      account_id.value.value
                        ? 'Transfers landing in this account'
                        : 'Pick an account first'
                    "
                    persistent-hint
                    clearable
                  ></v-select>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-select
                    v-model="budget_ids.value.value"
                    :items="budgetOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    label="Budgets this covers"
                    density="compact"
                    multiple
                    chips
                    closable-chips
                    clearable
                    hint="The spending this bucket exists to pay for. Leave empty when the spending is genuinely sporadic — save toward a target instead."
                    persistent-hint
                  ></v-select>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-select
                    v-model="scope_main_tag_ids.value.value"
                    :items="mainTagOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    label="Spending families this covers"
                    density="compact"
                    multiple
                    chips
                    closable-chips
                    clearable
                    hint="Claims every tag in the family, including ones added later. Prefer this — naming tags one by one means a new subcategory silently belongs to nobody."
                    persistent-hint
                  ></v-select>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col>
                  <v-select
                    v-model="scope_tag_ids.value.value"
                    :items="tagOptions"
                    item-title="title"
                    item-value="value"
                    variant="outlined"
                    label="Spending tags this covers"
                    density="compact"
                    multiple
                    chips
                    closable-chips
                    clearable
                    hint="Individual tags, for anything the families above do not cover. A tag a linked budget already covers is ignored, so nothing is counted twice."
                    persistent-hint
                  ></v-select>
                </v-col>
              </v-row>
              <v-row dense>
                <v-col :cols="smAndDown ? 12 : 6">
                  <v-select
                    v-model="mode.value.value"
                    :items="MODES"
                    item-title="label"
                    item-value="value"
                    variant="outlined"
                    label="What this bucket is for"
                    density="compact"
                    :error-messages="mode.errorMessage.value"
                    :hint="MODE_HINTS[mode.value.value]"
                    persistent-hint
                  ></v-select>
                </v-col>
                <v-col v-if="mode.value.value === 'maintain'" :cols="smAndDown ? 12 : 6">
                  <v-text-field
                    v-model="minimum_balance.value.value"
                    variant="outlined"
                    label="Balance to hold"
                    density="compact"
                    :error-messages="minimum_balance.errorMessage.value"
                    type="number"
                    step="1.00"
                    prefix="$"
                    hint="A floor under this account every day, which is the most expensive thing a bucket can be asked for"
                    persistent-hint
                    clearable
                  ></v-text-field>
                </v-col>
                <template v-if="mode.value.value === 'goal'">
                  <v-col :cols="smAndDown ? 12 : 3">
                    <v-text-field
                      v-model="goal_amount.value.value"
                      variant="outlined"
                      label="Goal amount"
                      density="compact"
                      :error-messages="goal_amount.errorMessage.value"
                      type="number"
                      step="1.00"
                      prefix="$"
                      hint="What to reach"
                      persistent-hint
                      clearable
                    ></v-text-field>
                  </v-col>
                  <v-col :cols="smAndDown ? 12 : 3">
                    <v-text-field
                      v-model="goal_date.value.value"
                      variant="outlined"
                      label="Reach it by"
                      density="compact"
                      :error-messages="goal_date.errorMessage.value"
                      type="date"
                      hint="The date is what makes this cheaper than holding it"
                      persistent-hint
                      clearable
                    ></v-text-field>
                  </v-col>
                </template>
              </v-row>
              <v-row dense>
                <v-col :cols="smAndDown ? 12 : 4">
                  <v-text-field
                    v-model="priority.value.value"
                    variant="outlined"
                    label="Priority"
                    density="compact"
                    :error-messages="priority.errorMessage.value"
                    type="number"
                    step="1"
                    hint="Lower is funded first"
                    persistent-hint
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 12 : 4">
                  <v-text-field
                    v-if="mode.value.value === 'maximise'"
                    v-model="sweep_share.value.value"
                    variant="outlined"
                    label="Share"
                    density="compact"
                    :error-messages="sweep_share.errorMessage.value"
                    type="number"
                    step="1"
                    min="1"
                    hint="Relative weight when several accounts sweep"
                    persistent-hint
                    class="mt-2"
                  ></v-text-field>
                </v-col>
                <v-col :cols="smAndDown ? 12 : 4">
                  <v-checkbox
                    v-model="lendable.value.value"
                    :error-messages="lendable.errorMessage.value"
                    label="Can be borrowed from"
                    density="compact"
                    hide-details
                  ></v-checkbox>
                  <div class="text-caption text-medium-emphasis">
                    The planner may move money out of here for a few days to
                    cover a gap, and puts it back.
                  </div>
                  <v-checkbox
                    v-model="receives_rewards.value.value"
                    :error-messages="receives_rewards.errorMessage.value"
                    label="Card rewards land here"
                    density="compact"
                    hide-details
                    class="mt-2"
                  ></v-checkbox>
                  <div class="text-caption text-medium-emphasis">
                    Counted as money arriving when the cards are cashed in,
                    rather than money this account has to save.
                  </div>
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
            {{ props.isEdit ? "Save Changes" : "Add Bucket" }}
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
  import { useBudgets } from "@/composables/budgetsComposable";
  import { useTags } from "@/composables/tagsComposable";
  import { useField, useForm } from "vee-validate";
  const { isOnline } = useOnlineStatus();

  // Blank is a real answer for several of these fields and it does not mean
  // zero: a blank minimum means "work it out from the budgets and the bills",
  // and a blank target means there is no target. Sending 0 instead would be
  // stating a figure the user never gave.
  const blankIsNull = value =>
    value === "" || value === null || value === undefined ? null : value;

  // What a bucket is *for*. Stated rather than inferred from which fields
  // happen to be filled in — one field used to mean both "hold this from
  // today" and "reach this by then", and those differ by more than an order of
  // magnitude in what they cost a paycheck.
  const MODES = [
    { value: "cover", label: "Cover its spending" },
    { value: "maintain", label: "Maintain a balance" },
    { value: "goal", label: "Reach a goal by a date" },
    { value: "maximise", label: "Take what is left over" },
  ];
  const MODE_HINTS = {
    cover: "Funds what this bucket has to spend, and nothing on top.",
    maintain:
      "A floor under the account every day. The most expensive option — if the money is wanted by a date, use a goal instead.",
    goal: "Spreads the amount across every payday until the date, so it costs a fraction of holding it.",
    maximise: "Absorbs whatever is left once every other bucket is funded.",
  };

  const { smAndDown } = useDisplay();
  const { handleSubmit } = useForm({
    validationSchema: {
      name(value) {
        if (value?.length >= 2 && value?.length <= 254) return true;

        return "Bucket needs to be at least 2 characters, and less than 254.";
      },
      contribution_per_paycheck(value) {
        if (value == null || value === "")
          return "Paycheck amount is required.";
        if (parseFloat(value) < 0)
          return "Paycheck amount cannot be negative.";

        return true;
      },
      buffer(value) {
        if (value == null || value === "") return true;
        if (parseFloat(value) < 0) return "A buffer cannot be negative.";

        return true;
      },
      minimum_per_paycheck(value) {
        if (blankIsNull(value) === null) return true;
        if (parseFloat(value) < 0) return "A minimum cannot be negative.";

        return true;
      },
      mode() {
        return true;
      },
      minimum_balance(value) {
        if (mode.value.value !== "maintain") return true;
        if (blankIsNull(value) === null)
          return "A bucket set to Maintain needs the balance to hold.";
        if (parseFloat(value) < 0) return "A minimum balance cannot be negative.";
        if (!account_id.value.value)
          return "Set an account before giving this a balance to hold.";

        return true;
      },
      goal_amount(value) {
        if (mode.value.value !== "goal") return true;
        if (blankIsNull(value) === null) return "A goal needs an amount.";
        if (parseFloat(value) < 0) return "A goal amount cannot be negative.";
        if (!account_id.value.value)
          return "Set an account before giving this a goal.";

        return true;
      },
      goal_date(value) {
        if (mode.value.value !== "goal") return true;
        // Without the date this is a Maintain wearing a goal's clothes, which
        // is the confusion modes exist to end — and the date is the whole
        // reason a goal costs a fraction of a floor.
        if (blankIsNull(value) === null) return "A goal needs the date to reach it by.";
        // A past date cannot be solved for — there are no paychecks left.
        if (new Date(value) <= new Date())
          return "The goal date must be in the future.";

        return true;
      },
      sweep_share(value) {
        if (mode.value.value !== "maximise") return true;
        if (value == null || value === "") return "A sweep needs a share.";
        if (parseInt(value) < 1) return "A share must be at least 1.";

        return true;
      },
      priority(value) {
        if (value == null || value === "") return "Priority is required.";
        if (parseInt(value) < 0) return "Priority cannot be negative.";

        return true;
      },
      account_id() {
        return true;
      },
      reminder_id() {
        return true;
      },
    },
  });

  const id = useField("id");
  const name = useField("name");
  const contribution_per_paycheck = useField("contribution_per_paycheck");
  const minimum_per_paycheck = useField("minimum_per_paycheck");
  const buffer = useField("buffer");
  const mode = useField("mode");
  const minimum_balance = useField("minimum_balance");
  const goal_amount = useField("goal_amount");
  const goal_date = useField("goal_date");
  const sweep_share = useField("sweep_share");
  const priority = useField("priority");
  const lendable = useField("lendable");
  const receives_rewards = useField("receives_rewards");
  const budget_ids = useField("budget_ids");
  const scope_tag_ids = useField("scope_tag_ids");
  const scope_main_tag_ids = useField("scope_main_tag_ids");
  const active = useField("active");
  const account_id = useField("account_id");
  const reminder_id = useField("reminder_id");

  const { accounts } = useAccounts(false);
  const { reminders } = useReminders();
  const { budgets } = useBudgets(false);
  const { tags } = useTags();

  // What the emergency plan frees up, shown rather than stored — it is the gap
  // between what this moves now and the floor it may not go below.
  const difference = computed(() => {
    const per = parseFloat(contribution_per_paycheck.value.value);
    const min = parseFloat(minimum_per_paycheck.value.value);
    if (isNaN(per)) return "0";
    if (isNaN(min)) return "0";
    return (per - min).toFixed(2);
  });

  const accountOptions = computed(() =>
    (accounts.value ?? []).map(a => ({
      title: a.account_name,
      value: a.id,
    })),
  );

  // The list endpoint wraps each budget in its spend totals, so the budget
  // itself is a level down.
  const budgetOptions = computed(() =>
    (budgets.value ?? []).map(b => ({
      title: b.budget?.name ?? b.name,
      value: b.budget?.id ?? b.id,
    })),
  );

  // A family is a main tag: claiming it claims every child, now and later.
  const mainTagOptions = computed(() => {
    const seen = new Map();
    for (const t of tags.value ?? []) {
      if (t.parent && !seen.has(t.parent.id)) {
        seen.set(t.parent.id, { title: t.parent.tag_name, value: t.parent.id });
      }
    }
    return [...seen.values()].sort((a, b) => a.title.localeCompare(b.title));
  });

  // Named parent/child the way the rest of the app shows a tag, so "Christmas"
  // and "Christmas / Ellie" are distinguishable in a long list.
  const tagOptions = computed(() =>
    (tags.value ?? []).map(t => ({
      title: t.child ? `${t.parent.tag_name} / ${t.child.tag_name}` : t.parent.tag_name,
      value: t.id,
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
        name.value.value = props.passedFormData.name;
        contribution_per_paycheck.value.value =
          props.passedFormData.contribution_per_paycheck;
        minimum_per_paycheck.value.value =
          props.passedFormData.minimum_per_paycheck ?? null;
        buffer.value.value = props.passedFormData.buffer ?? "0";
        mode.value.value = props.passedFormData.mode ?? "cover";
        minimum_balance.value.value =
          props.passedFormData.minimum_balance ?? null;
        goal_amount.value.value = props.passedFormData.goal_amount ?? null;
        goal_date.value.value = props.passedFormData.goal_date ?? null;
        sweep_share.value.value = props.passedFormData.sweep_share ?? 1;
        priority.value.value = props.passedFormData.priority ?? 100;
        lendable.value.value = props.passedFormData.lendable ?? true;
        receives_rewards.value.value =
          props.passedFormData.receives_rewards ?? false;
        budget_ids.value.value = props.passedFormData.budget_ids ?? [];
        scope_tag_ids.value.value = props.passedFormData.scope_tag_ids ?? [];
        scope_main_tag_ids.value.value =
          props.passedFormData.scope_main_tag_ids ?? [];
        active.value.value = props.passedFormData.active;
        account_id.value.value = props.passedFormData.account_id ?? null;
        reminder_id.value.value = props.passedFormData.reminder_id ?? null;
      }
    });
  };
  const submit = handleSubmit(values => {
    const payload = {
      ...values,
      minimum_per_paycheck: blankIsNull(values.minimum_per_paycheck),
      buffer: values.buffer ?? 0,
      // Only the field its mode gives meaning to is sent; the API rejects a
      // figure the chosen mode would ignore rather than storing it silently.
      mode: values.mode ?? "cover",
      minimum_balance:
        values.mode === "maintain" ? blankIsNull(values.minimum_balance) : null,
      goal_amount: values.mode === "goal" ? blankIsNull(values.goal_amount) : null,
      goal_date: values.mode === "goal" ? blankIsNull(values.goal_date) : null,
      sweep_share: parseInt(values.sweep_share ?? 1),
      lendable: values.lendable ?? true,
      receives_rewards: values.receives_rewards ?? false,
      priority: parseInt(values.priority ?? 100),
      budget_ids: values.budget_ids ?? [],
      scope_tag_ids: values.scope_tag_ids ?? [],
      scope_main_tag_ids: values.scope_main_tag_ids ?? [],
    };
    if (props.isEdit) {
      emit("editBucket", payload);
    } else {
      emit("addBucket", payload);
    }
    emit("updateDialog", false);
  });

  const emit = defineEmits([
    "updateDialog",
    "addBucket",
    "editBucket",
  ]);

  const clickClose = () => {
    emit("updateDialog", false);
  };

  onMounted(() => {
    watchPassedFormData();
  });
</script>
