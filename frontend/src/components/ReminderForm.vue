<template>
  <v-dialog persistent :fullscreen="smAndDown" :width="smAndDown ? undefined : '1024'"
    <form @submit.prevent="submit">
      <v-card>
        <v-card-title>
          <span class="text-h5" v-if="props.isEdit == false">Add Reminder</span>
          <span class="text-h5" v-else>Edit Reminder</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-text-field
                  v-model="amount.value.value"
                  variant="outlined"
                  label="Amount*"
                  :error-messages="amount.errorMessage.value"
                  prefix="$"
                  type="number"
                  step="1.00"
                  @blur="reformatNumberToMoney"
                ></v-text-field>
              </v-col>
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-text-field
                  v-model="description.value.value"
                  variant="outlined"
                  label="Description*"
                  :error-messages="description.errorMessage.value"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-autocomplete
                  clearable
                  label="Transaction Type*"
                  :items="transaction_types"
                  variant="outlined"
                  :loading="transaction_types_isLoading"
                  item-title="transaction_type"
                  item-value="id"
                  v-model="transaction_type_id.value.value"
                  :error-messages="transaction_type_id.errorMessage.value"
                ></v-autocomplete>
              </v-col>
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-autocomplete
                  clearable
                  label="Tag*"
                  :items="tags"
                  variant="outlined"
                  :loading="tags_isLoading"
                  item-title="tag_name"
                  item-value="id"
                  v-model="tag_id.value.value"
                  :error-messages="tag_id.errorMessage.value"
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item
                      v-bind="props"
                      :title="
                        item.raw.parent
                          ? item.raw.parent.tag_name
                          : item.raw.tag_name
                      "
                      :subtitle="item.raw.parent ? item.raw.tag_name : null"
                    >
                      <template v-slot:prepend>
                        <v-icon
                          icon="mdi-tag"
                          :color="tagColor(item.raw.tag_type.id)"
                        ></v-icon>
                      </template>
                    </v-list-item>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>
            <v-row>
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-autocomplete
                  clearable
                  label="Source Account*"
                  :items="accounts"
                  variant="outlined"
                  :loading="accounts_isLoading"
                  item-title="account_name"
                  item-value="id"
                  v-model="reminder_source_account_id.value.value"
                  :error-messages="reminder_source_account_id.errorMessage.value"
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
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-autocomplete
                  clearable
                  label="Destination Account*"
                  :items="accounts"
                  variant="outlined"
                  :loading="accounts_isLoading"
                  item-title="account_name"
                  item-value="id"
                  v-model="reminder_destination_account_id.value.value"
                  :error-messages="reminder_destination_account_id.errorMessage.value"
                  v-if="transaction_type_id.value.value == 3"
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
            <v-row>
              <v-col :cols="smAndDown ? 12 : undefined">
                <span class="text-subtitle-2">Start Date</span>
                <VueDatePicker
                  v-model="start_date.value.value"
                  timezone="America/New_York"
                  model-type="yyyy-MM-dd"
                  :enable-time-picker="false"
                  auto-apply
                  format="yyyy-MM-dd"
                  :min-date="tomorrow"
                  :teleport="true"
                ></VueDatePicker>
                <span
                  class="text-error text-caption"
                  v-if="start_date.errorMessage.value"
                >
                  {{ start_date.errorMessage.value }}
                </span>
              </v-col>
              <v-col :cols="smAndDown ? 12 : undefined">
                <span class="text-subtitle-2">End Date</span>
                <VueDatePicker
                  v-model="end_date.value.value"
                  timezone="America/New_York"
                  model-type="yyyy-MM-dd"
                  :enable-time-picker="false"
                  auto-apply
                  format="yyyy-MM-dd"
                  :min-date="getLowerLimit()"
                  :teleport="true"
                ></VueDatePicker>
                <span
                  class="text-error text-caption"
                  v-if="end_date.errorMessage.value"
                >
                  {{ end_date.errorMessage.value }}
                </span>
              </v-col>
            </v-row>
            <v-row>
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-autocomplete
                  clearable
                  label="Repeats*"
                  :items="repeats"
                  variant="outlined"
                  :loading="repeats_isLoading"
                  item-title="repeat_name"
                  item-value="id"
                  v-model="repeat_id.value.value"
                  :error-messages="repeat_id.errorMessage.value"
                ></v-autocomplete>
              </v-col>
              <v-col :cols="smAndDown ? 12 : undefined">
                <v-switch
                  v-model="auto_add.value.value"
                  hide-details
                  label="Auto Add"
                  color="primary"
                ></v-switch>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                <v-textarea
                  clearable
                  label="Memo"
                  variant="outlined"
                  v-model="memo.value.value"
                  :rows="4"
                  no-resize
                ></v-textarea>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="closeDialog">Close</v-btn>
          <v-btn color="primary" variant="text" type="submit">Save</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </v-dialog>
</template>
<script setup>
  import { defineEmits, defineProps, onMounted, watchEffect, watch } from "vue";
  import { useDisplay } from "vuetify";
  import { useTransactionTypes } from "@/composables/transactionTypesComposable";
  import { useAccounts } from "@/composables/accountsComposable";
  import { useTags } from "@/composables/tagsComposable";
  import VueDatePicker from "@vuepic/vue-datepicker";
  import "@vuepic/vue-datepicker/dist/main.css";
  import { useReminders } from "@/composables/remindersComposable";
  import { useRepeats } from "@/composables/repeatsComposable";
  import { useField, useForm } from "vee-validate";
  import * as yup from "yup";

  const schema = yup.object({
    description: yup.string().required("Description is required."),
    amount: yup
      .number()
      .typeError("Amount is required.")
      .required("Amount is required.")
      .positive("Amount must be greater than zero."),
    transaction_type_id: yup
      .number()
      .typeError("Transaction type is required.")
      .required("Transaction type is required."),
    tag_id: yup
      .number()
      .typeError("Tag is required.")
      .required("Tag is required."),
    reminder_source_account_id: yup
      .number()
      .typeError("Source account is required.")
      .required("Source account is required."),
    reminder_destination_account_id: yup.mixed().when("transaction_type_id", {
      is: 3,
      then: schema => schema.required("Destination account is required for transfers."),
      otherwise: schema => schema.nullable().notRequired(),
    }),
    start_date: yup.string().nullable().required("Start date is required."),
    end_date: yup
      .string()
      .nullable()
      .notRequired()
      .test(
        "end-after-start",
        "End date must be on or after start date.",
        function (value) {
          const { start_date } = this.parent;
          if (!value || !start_date) return true;
          return value >= start_date;
        },
      ),
    repeat_id: yup
      .number()
      .typeError("Repeat type is required.")
      .required("Repeat type is required."),
    auto_add: yup.boolean().notRequired(),
    memo: yup.string().nullable().notRequired(),
  });

  const { smAndDown } = useDisplay();
  const { handleSubmit } = useForm({ validationSchema: schema });

  const description = useField("description");
  const amount = useField("amount");
  const transaction_type_id = useField("transaction_type_id");
  const tag_id = useField("tag_id");
  const reminder_source_account_id = useField("reminder_source_account_id");
  const reminder_destination_account_id = useField(
    "reminder_destination_account_id",
  );
  const start_date = useField("start_date");
  const end_date = useField("end_date");
  const repeat_id = useField("repeat_id");
  const auto_add = useField("auto_add");
  const memo = useField("memo");

  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  const { addReminder, updateReminder } = useReminders();
  const { accounts, isLoading: accounts_isLoading } = useAccounts();
  const { repeats, isLoading: repeats_isLoading } = useRepeats();
  const { transaction_types, isLoading: transaction_types_isLoading } =
    useTransactionTypes();
  const { tags, isLoading: tags_isLoading } = useTags();

  const emit = defineEmits(["updateDialog"]);
  const props = defineProps({
    isEdit: { type: Boolean, default: false },
    passedFormData: { type: Object },
  });

  // When one-time repeat is selected, lock end_date to start_date
  watch(
    () => repeat_id.value.value,
    newVal => {
      if (newVal == 6) {
        end_date.value.value = start_date.value.value;
      }
    },
  );

  const submit = handleSubmit(values => {
    const payload = { ...values };
    payload.amount =
      values.transaction_type_id == 2
        ? Math.abs(values.amount)
        : -Math.abs(values.amount);
    if (values.repeat_id == 6) {
      payload.end_date = values.start_date;
    }
    if (values.transaction_type_id != 3) {
      payload.reminder_destination_account_id = null;
    }
    payload.next_date = values.start_date;
    payload.id = props.passedFormData.id;

    if (props.isEdit) {
      updateReminder(payload);
    } else {
      addReminder(payload);
    }
    closeDialog();
  });

  const closeDialog = () => {
    emit("updateDialog", false);
  };

  const initializeFormData = () => {
    description.value.value = props.passedFormData.description ?? null;
    amount.value.value = props.passedFormData.amount
      ? parseFloat(Math.abs(props.passedFormData.amount)).toFixed(2)
      : null;
    transaction_type_id.value.value =
      props.passedFormData.transaction_type?.id ?? null;
    tag_id.value.value = props.passedFormData.tag?.id ?? null;
    reminder_source_account_id.value.value =
      props.passedFormData.reminder_source_account?.id ?? null;
    reminder_destination_account_id.value.value =
      props.passedFormData.reminder_destination_account?.id ?? null;
    start_date.value.value = props.passedFormData.start_date ?? null;
    end_date.value.value = props.passedFormData.end_date ?? null;
    repeat_id.value.value = props.passedFormData.repeat?.id ?? null;
    auto_add.value.value = props.passedFormData.auto_add ?? true;
    memo.value.value = props.passedFormData.memo ?? null;
  };

  onMounted(() => {
    watchEffect(() => {
      if (props.passedFormData) {
        initializeFormData();
      }
    });
  });

  const reformatNumberToMoney = () => {
    if (amount.value.value) {
      amount.value.value = parseFloat(amount.value.value).toFixed(2);
    }
  };

  const tagColor = typeID => {
    if (typeID == 1) return "error";
    if (typeID == 2) return "success";
    if (typeID == 3) return "info";
  };

  const getLowerLimit = () => {
    const startVal = start_date.value.value;
    if (!startVal) return new Date();
    const d = new Date(startVal);
    d.setDate(d.getDate() + 1);
    return d;
  };
</script>
