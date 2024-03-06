<template>
  <v-dialog persistent width="1024" min-height="800px">
    <v-card>
      <v-card-title>
        <span class="text-h5" v-if="props.isEdit == false">Add Reminder</span>
        <span class="text-h5" v-else>Edit Reminder</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col>
              <v-text-field
                v-model="amount"
                variant="outlined"
                label="Amount*"
                :rules="required"
                prefix="$"
                @update:model-value="checkFormComplete"
                type="number"
                step="1.00"
                @update:focused="reformatNumberToMoney"
              ></v-text-field>
            </v-col>
            <v-col>
              <v-text-field
                v-model="formData.description"
                variant="outlined"
                label="Description*"
                :rules="required"
                @update:model-value="checkFormComplete"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                clearable
                label="Transaction Type*"
                :items="transaction_types"
                variant="outlined"
                :loading="transaction_types_isLoading"
                item-title="transaction_type"
                item-value="id"
                v-model="formData.transaction_type_id"
                :rules="required"
                @update:model-value="checkFormComplete"
              ></v-autocomplete>
            </v-col>
            <v-col>
              <!-- TODO: Enable adding tags here -->
              <v-autocomplete
                clearable
                label="Tag*"
                :items="tags"
                variant="outlined"
                :loading="tags_isLoading"
                item-title="tag_name"
                item-value="id"
                v-model="formData.tag_id"
                :rules="required"
                @update:model-value="checkFormComplete"
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
            <v-col>
              <v-autocomplete
                clearable
                label="Source Account*"
                :items="accounts"
                variant="outlined"
                :loading="accounts_isLoading"
                item-title="account_name"
                item-value="id"
                v-model="formData.reminder_source_account_id"
                :rules="required"
                @update:model-value="checkFormComplete"
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
            <v-col>
              <v-autocomplete
                clearable
                label="Destination Account*"
                :items="accounts"
                variant="outlined"
                :loading="accounts_isLoading"
                item-title="account_name"
                item-value="id"
                v-model="formData.reminder_destination_account_id"
                :rules="required"
                @update:model-value="checkFormComplete"
                v-if="formData.transaction_type_id == 3"
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
            <v-col>
              <span class="text-subtitle-2">Start Date</span>
              <VueDatePicker
                v-model="formData.start_date"
                timezone="America/New_York"
                model-type="yyyy-MM-dd"
                :enable-time-picker="false"
                auto-apply
                format="yyyy-MM-dd"
                @closed="checkFormComplete"
                :min-date="tomorrow"
                :teleport="true"
              ></VueDatePicker>
            </v-col>
            <v-col>
              <span class="text-subtitle-2">End Date</span>
              <VueDatePicker
                v-model="formData.end_date"
                timezone="America/New_York"
                model-type="yyyy-MM-dd"
                :enable-time-picker="false"
                auto-apply
                format="yyyy-MM-dd"
                @closed="checkFormComplete"
                :min-date="getLowerLimit()"
                :teleport="true"
                :state="endDateGood"
              ></VueDatePicker>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-autocomplete
                clearable
                label="Repeats*"
                :items="repeats"
                variant="outlined"
                :loading="repeats_isLoading"
                item-title="repeat_name"
                item-value="id"
                v-model="formData.repeat_id"
                :rules="required"
                @update:model-value="checkFormComplete"
              ></v-autocomplete>
            </v-col>
            <v-col>
              <v-switch
                v-model="formData.auto_add"
                hide-details
                label="Auto Add"
                color="secondary"
                @update:model-value="checkFormComplete"
              ></v-switch>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="text" @click="closeDialog">
          Close
        </v-btn>
        <v-btn
          color="secondary"
          variant="text"
          @click="submitForm"
          :disabled="!formComplete"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
import { ref, defineEmits, defineProps, onMounted, watchEffect } from "vue";
import { useTransactionTypes } from "@/composables/transactionTypesComposable";
import { useAccounts } from "@/composables/accountsComposable";
import { useTags } from "@/composables/tagsComposable";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import { useReminders } from "@/composables/remindersComposable";
import { useRepeats } from "@/composables/repeatsComposable";

const today = new Date();
const tomorrow = new Date(today);
tomorrow.setDate(today.getDate() + 1);
const { addReminder, updateReminder } = useReminders();
const { accounts, isLoading: accounts_isLoading } = useAccounts();
const formComplete = ref(false);
const { repeats, isLoading: repeats_isLoading } = useRepeats();
const { transaction_types, isLoading: transaction_types_isLoading } =
  useTransactionTypes();
const props = defineProps({
  isEdit: {
    type: Boolean,
    default: false,
  },
  passedFormData: {
    type: Object,
  },
});

const formData = ref({
  id: props.passedFormData.id || 0,
  tag_id: props.passedFormData.tag.id || null,
  amount: props.passedFormData.amount || null,
  reminder_source_account_id:
    props.passedFormData.reminder_source_account.id || null,
  reminder_destination_account_id:
    props.passedFormData.reminder_destination_account.id || null,
  description: props.passedFormData.description || null,
  transaction_type_id: props.passedFormData.transaction_type.id || 1,
  start_date: props.passedFormData.start_date || null,
  end_date: props.passedFormData.end_date || null,
  repeat_id: props.passedFormData.repeat.id || null,
  auto_add: props.passedFormData.auto_add || true,
});

const { tags, isLoading: tags_isLoading } = useTags();
const emit = defineEmits(["updateDialog"]);
const watchPassedFormData = () => {
  watchEffect(() => {
    if (props.passedFormData) {
      formData.value = {
        id: props.passedFormData.id,
        tag_id: props.passedFormData.tag.id,
        amount: props.passedFormData.amount,
        reminder_source_account_id:
          props.passedFormData.reminder_source_account.id,
        reminder_destination_account_id:
          props.passedFormData.reminder_destination_account &&
          props.passedFormData.reminder_destination_account.id
            ? props.passedFormData.reminder_destination_account.id
            : null,
        description: props.passedFormData.description,
        transaction_type_id: props.passedFormData.transaction_type.id,
        start_date: props.passedFormData.start_date,
        end_date: props.passedFormData.end_date,
        repeat_id: props.passedFormData.repeat.id,
        auto_add: props.passedFormData.auto_add,
      };
      amount.value = props.passedFormData.amount
        ? parseFloat(Math.abs(props.passedFormData.amount)).toFixed(2)
        : null;
    }
  });
};
const endDateGood = ref(true);
const required = [
  value => {
    if (value) return true;

    return "This field is required.";
  },
];
const amount = ref(
  props.passedFormData.amount
    ? parseFloat(Math.abs(props.passedFormData.amount)).toFixed(2)
    : null,
);
const checkFormComplete = async () => {
  if (formData.value.repeat_id == 6) {
    formData.value.end_date = formData.value.start_date;
  }
  if (formData.value.end_date) {
    if (formData.value.end_date >= formData.value.start_date) {
      endDateGood.value = true;
    } else {
      endDateGood.value = false;
    }
  }
  if (
    formData.value.transaction_type_id !== null &&
    formData.value.transaction_type_id !== "" &&
    formData.value.description !== "" &&
    formData.value.description !== null &&
    formData.value.reminder_source_account_id !== "" &&
    formData.value.reminder_source_account_id !== null &&
    formData.value.tag_id !== "" &&
    formData.value.tag_id !== null &&
    amount.value !== "" &&
    amount.value !== null &&
    formData.value.start_date !== "" &&
    formData.value.start_date !== null &&
    formData.value.repeat_id !== "" &&
    formData.value.repeat_id !== null
  ) {
    if (formData.value.transaction_type_id == 3) {
      if (
        formData.value.reminder_destination_account_id !== null &&
        formData.value.reminder_destination_account_id !== ""
      ) {
        formComplete.value = true;
      } else {
        formComplete.value = false;
      }
    } else {
      formData.value.reminder_destination_account_id = null;
      formComplete.value = true;
    }
    if (formData.value.end_date) {
      if (formData.value.end_date >= formData.value.start_date) {
        formComplete.value = true;
      } else {
        formComplete.value = false;
      }
    }
  } else {
    formComplete.value = false;
  }
};

const reformatNumberToMoney = () => {
  amount.value = parseFloat(amount.value).toFixed(2);
};

onMounted(() => {
  watchPassedFormData();
});

const submitForm = async () => {
  if (formData.value.transaction_type_id == 2) {
    formData.value.amount = amount.value;
  } else {
    formData.value.amount = -amount.value;
  }
  formData.value.next_date = formData.value.start_date;
  if (props.isEdit == false) {
    await addReminder(formData.value);
  } else {
    await updateReminder(formData.value);
  }

  closeDialog();
};

const closeDialog = () => {
  emit("updateDialog", false);
};

const tagColor = typeID => {
  if (typeID == 1) {
    return "red";
  } else if (typeID == 2) {
    return "green";
  } else if (typeID == 3) {
    return "grey";
  }
};

const getLowerLimit = () => {
  const lowerLimit = new Date();
  const start_date = new Date(formData.value.start_date);
  lowerLimit.setDate(start_date.getDate() + 1);
  return lowerLimit;
};
</script>
