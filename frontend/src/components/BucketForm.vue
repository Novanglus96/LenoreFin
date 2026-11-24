<template>
  <v-card>
    <v-card-title>{{ form.id ? "Edit bucket" : "New bucket" }}</v-card-title>
    <v-card-subtitle class="text-wrap">
      What the bucket is and where its money goes. The amount each paycheck is
      set by accepting a plan.
    </v-card-subtitle>
    <v-card-text>
      <v-form ref="formRef" @submit.prevent="submit">
        <v-text-field
          v-model="form.name"
          label="Name"
          :rules="[v => !!v || 'Required']"
          density="compact"
        />
        <v-autocomplete
          v-model="form.reminder_id"
          :items="transferReminders"
          item-title="title"
          item-value="id"
          label="Funding transfer"
          hint="The recurring transfer that feeds this bucket. Sets the account."
          persistent-hint
          clearable
          density="compact"
          class="mb-3"
          @update:model-value="pickReminder"
        />
        <v-autocomplete
          v-model="form.account_id"
          :items="accountItems"
          item-title="account_name"
          item-value="id"
          label="Account"
          :disabled="!!form.reminder_id"
          clearable
          density="compact"
        />
        <v-row dense>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.goal_amount"
              label="Goal (optional)"
              prefix="$"
              type="number"
              hint="Funding stops once the account reaches it"
              persistent-hint
              clearable
              density="compact"
            />
          </v-col>
          <v-col cols="12" sm="6">
            <v-text-field
              v-model="form.goal_date"
              label="Goal date (optional)"
              type="date"
              hint="Blank means the end of the plan"
              persistent-hint
              clearable
              density="compact"
            />
          </v-col>
        </v-row>
        <v-switch
          v-model="form.active"
          label="Part of the plan"
          color="primary"
          density="compact"
          hide-details
        />
      </v-form>
    </v-card-text>
    <v-card-actions>
      <v-btn
        v-if="form.id"
        color="error"
        variant="text"
        @click="$emit('delete', form.id)"
      >
        Delete
      </v-btn>
      <v-spacer />
      <v-btn variant="text" @click="$emit('close')">Cancel</v-btn>
      <v-btn color="primary" variant="flat" @click="submit">Save</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
  import { computed, reactive, ref } from "vue";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useReminders } from "@/composables/remindersComposable";

  const props = defineProps({ bucket: { type: Object, default: null } });
  const emit = defineEmits(["save", "close", "delete"]);

  const formRef = ref(null);
  const form = reactive({
    id: props.bucket?.id ?? null,
    name: props.bucket?.name ?? "",
    contribution_per_paycheck: props.bucket?.contribution_per_paycheck ?? 0,
    goal_amount: props.bucket?.goal_amount ?? null,
    goal_date: props.bucket?.goal_date ?? null,
    active: props.bucket?.active ?? true,
    account_id: props.bucket?.account_id ?? null,
    reminder_id: props.bucket?.reminder_id ?? null,
  });

  const { accounts } = useAccounts(false);
  const { reminders } = useReminders();

  const accountItems = computed(() =>
    (accounts.value ?? []).filter(a => !a.is_parent_account),
  );
  const transferReminders = computed(() =>
    (reminders.value ?? [])
      .filter(r => r.reminder_destination_account)
      .map(r => ({
        id: r.id,
        title: `${r.description} — ${Math.abs(Number(r.amount)).toFixed(2)} → ${r.reminder_destination_account.account_name}`,
        account_id: r.reminder_destination_account.id,
      })),
  );

  const pickReminder = id => {
    const reminder = transferReminders.value.find(r => r.id === id);
    if (reminder) form.account_id = reminder.account_id;
  };

  const blankToNull = v => (v === "" || v === undefined ? null : v);

  const submit = async () => {
    const { valid } = await formRef.value.validate();
    if (!valid) return;
    emit("save", {
      ...form,
      goal_amount: blankToNull(form.goal_amount),
      goal_date: blankToNull(form.goal_date),
    });
  };
</script>
