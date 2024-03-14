<template>
  <v-dialog persistent width="1024">
    <v-card>
      <v-card-title>
        <span class="text-h5">Import File</span>
      </v-card-title>

      <v-card-text>
        <v-stepper v-model="step" color="secondary" alt-labels>
          <v-stepper-header>
            <v-stepper-item
              value="1"
              title="Upload File"
              icon="mdi-upload"
              :complete="step1Complete"
            ></v-stepper-item>
            <v-divider color="accent" thickness="2"></v-divider>
            <v-stepper-item
              value="2"
              title="Review Mappings"
              icon="mdi-relation-many-to-many"
              :complete="step2Complete"
            ></v-stepper-item>
            <v-divider color="accent" thickness="2"></v-divider>
            <v-stepper-item
              value="3"
              title="Final Check"
              icon="mdi-marker-check"
              :complete="step3Complete"
            ></v-stepper-item>
            <v-divider color="accent" thickness="2"></v-divider>
            <v-stepper-item
              value="4"
              title="Summary"
              icon="mdi-text-box"
              :complete="step4Complete"
            ></v-stepper-item>
          </v-stepper-header>
          <v-stepper-window>
            <v-stepper-window-item value="1">
              <v-banner>
                <v-banner-text
                  >Please upload a valid csv file with transactions you would
                  like to import. Click <a href="/example.csv">here</a> for an
                  example .csv file to download.</v-banner-text
                >
              </v-banner>
              <v-file-input
                :clearable="false"
                label="File Upload"
                variant="outlined"
                chips
                v-model="fileToImport"
                accept=".csv"
                @update:model-value="updateStep1Complete"
              ></v-file-input>
            </v-stepper-window-item>
            <v-stepper-window-item value="2"> Test2 </v-stepper-window-item>
            <v-stepper-window-item value="3"> Test3 </v-stepper-window-item>
            <v-stepper-window-item value="4"> Test4 </v-stepper-window-item>
          </v-stepper-window>
          <v-stepper-actions disabled="prev">
            <template #next>
              <v-btn @click="nextStep" :disabled="nextDisabled">Next</v-btn>
            </template>
          </v-stepper-actions>
        </v-stepper>
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
          :disabled="allStepsComplete"
        >
          Submit
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
/**
 * Vue script setup for file import
 * @fileoverview
 * @author John Adams
 * @version 1.0.0
 */

// Import Vue composition functions and components...
import { ref, defineEmits } from "vue";
import { useTransactionTypes } from "@/composables/transactionTypesComposable";
import { useTransactionStatuses } from "@/composables/transactionStatusesComposable";
import { useAccounts } from "@/composables/accountsComposable";
import { useTags } from "@/composables/tagsComposable";

// Define reactive variables...
const step = ref(0);
const fileToImport = ref(null);
const step1Complete = ref(false);
const step2Complete = ref(false);
const step3Complete = ref(false);
const step4Complete = ref(false);
const nextDisabled = ref(true);

// Initialize Mappings
const mappings = ref({
  transaction_types: [],
  transaction_statuses: [],
  accounts: [],
  tags: [],
});

// Define emits
const emit = defineEmits(["updateDialog"]);

// API calls and data retrieval...

const { transaction_types } = useTransactionTypes();
const { transaction_statuses } = useTransactionStatuses();
const { accounts } = useAccounts();
const { tags } = useTags();

// Define functions...

/**
 * `closeDialog` Emits updateDialog to close form.
 */
const closeDialog = () => {
  step.value = 0;
  fileToImport.value = null;
  step1Complete.value = false;
  step2Complete.value = false;
  step3Complete.value = false;
  step4Complete.value = false;
  nextDisabled.value = false;
  emit("updateDialog", false);
};

/**
 * `nextStep` Advances the stepper to next step.
 */
const nextStep = () => {
  if (step.value < 4) {
    nextDisabled.value = true;
    step.value++;
  }
};

/**
 * `updateStep1Complete` Updates Step 1 Completed status.
 */
const updateStep1Complete = () => {
  processFile();
  if (fileToImport.value && fileToImport.value !== "") {
    step1Complete.value = true;
    nextDisabled.value = false;
  } else {
    step1Complete.value = false;
    nextDisabled.value = true;
  }
};

/**
 * `allStepsComplete` Returns true if all steps are complete.
 */
const allStepsComplete = () => {
  if (
    step1Complete.value &&
    step2Complete.value &&
    step3Complete.value &&
    step4Complete.value
  ) {
    return true;
  } else {
    return false;
  }
};

/**
 * `processFile` Processes the csv file.
 */
const processFile = () => {
  const file = fileToImport.value[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = e => {
    const contents = e.target.result;
    const data = parseCSV(contents);
    createMappings(data);
  };
  reader.readAsText(file);
};

/**
 * `parseCSV` Parse the csv file.
 */
const parseCSV = csvFile => {
  const lines = csvFile.split("\n");
  if (!lines.length) return [];
  const header = lines[0].split(",");
  const data = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;
    const values = line.split(",");
    const obj = {};
    for (let j = 0; j < header.length; j++) {
      obj[header[j].trim()] = values[j].trim();
    }
    data.push(obj);
  }
  return data;
};

/**
 * `createMappings` Create mappings for transaction fields.
 */
const createMappings = transactions => {
  let types = [];
  let statuses = [];
  let map_accounts = [];
  let map_tags = [];
  for (let i = 0; i < transactions.length; i++) {
    let transaction = transactions[i];
    let trans_type = {
      file_type: transaction.TransactionType,
      type_id: 0,
    };
    let trans_status = {
      file_status: transaction.TransactionStatus,
      status_id: 0,
    };
    let source_account = {
      file_account: transaction.SourceAccount,
      account_id: 0,
    };
    let destination_account = {
      file_account: transaction.DestinationAccount,
      account_id: 0,
    };

    // Map TransactionTypes, set to 0 if it doesn't exist
    let type_exists = true;
    if (transaction.TransactionType !== "") {
      type_exists = types.some(
        item => item.file_type == transaction.TransactionType,
      );
    }
    if (type_exists == false) {
      for (let j = 0; j < transaction_types.value.length; j++) {
        if (
          transaction_types.value[j].transaction_type ==
          transaction.TransactionType
        ) {
          trans_type = {
            file_type: transaction.TransactionType,
            type_id: transaction_types.value[j].id,
          };
          break;
        }
      }
      types.push(trans_type);
    }

    // Map TransactionStatuses, set to 0 if it doesn't exist
    let status_exists = true;
    if (transaction.TransactionStatus !== "") {
      status_exists = statuses.some(
        item => item.file_status == transaction.TransactionStatus,
      );
    }
    if (!status_exists) {
      for (let k = 0; k < transaction_statuses.value.length; k++) {
        if (
          transaction_statuses.value[k].transaction_status ==
          transaction.TransactionStatus
        ) {
          trans_status = {
            file_status: transaction.TransactionStatus,
            status_id: transaction_statuses.value[k].id,
          };
          break;
        }
      }
      statuses.push(trans_status);
    }

    // Map Accounts, set to 0 if it doesn't exist
    let source_account_exists = true;
    let destination_account_exists = true;
    if (transaction.SourceAccount !== "") {
      source_account_exists = map_accounts.some(
        item => item.file_account == transaction.SourceAccount,
      );
    }
    if (transaction.DestinationAccount !== "") {
      destination_account_exists = map_accounts.some(
        item => item.file_account == transaction.DestinationAccount,
      );
    }
    if (!source_account_exists) {
      for (let l = 0; l < accounts.value.length; l++) {
        if (accounts.value[l].account_name == transaction.SourceAccount) {
          source_account = {
            file_account: transaction.SourceAccount,
            account_id: accounts.value[l].id,
          };
          break;
        }
      }
      map_accounts.push(source_account);
    }
    if (!destination_account_exists) {
      for (let m = 0; m < accounts.value.length; m++) {
        if (accounts.value[m].account_name == transaction.DestinationAccount) {
          destination_account = {
            file_account: transaction.DestinationAccount,
            account_id: accounts.value[m].id,
          };
          break;
        }
      }
      map_accounts.push(destination_account);
    }

    // Map tags, set to 0 if it doesn't exist
    const all_tags = transaction.Tags.split(";").map(substring =>
      substring.split(":")[0].trim(),
    );
    for (let n = 0; n < all_tags.length; n++) {
      let trans_tag = {
        file_tag: all_tags[n],
        tag_id: 0,
      };
      let tag_exists = true;
      if (transaction.Tags !== "") {
        tag_exists = map_tags.some(item => item.file_tag == all_tags[n]);
      }
      if (!tag_exists) {
        for (let p = 0; p < tags.value.length; p++) {
          if (tags.value[p].tag_name == all_tags[n]) {
            trans_tag = {
              file_tag: all_tags[n],
              tag_id: tags.value[p].id,
            };
            break;
          }
        }
        map_tags.push(trans_tag);
      }
    }
  }

  mappings.value.transaction_types = types;
  mappings.value.transaction_statuses = statuses;
  mappings.value.accounts = map_accounts;
  mappings.value.tags = map_tags;
  console.log("mappings:", mappings.value);
};
</script>
