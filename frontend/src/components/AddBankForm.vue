<template>
  <v-dialog v-model="dialog" persistent width="300">
    <template v-slot:activator="{ props }">
      <v-btn
        color="accent"
        v-bind="props"
        @click="
          bankForm.bank_name = '';
          bankSubmit = true;
        "
        >Don't see your bank?</v-btn
      >
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Add Bank</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col>
              <v-text-field
                label="Bank Name*"
                required
                :rules="required"
                variant="outlined"
                @update:model-value="checkBank"
                v-model="bankForm.bank_name"
              ></v-text-field>
            </v-col>
          </v-row>
        </v-container>
        <span class="text-red text-subtitle-2 font-italic">* required</span>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="accent" variant="text" @click="dialog = false">
          Close
        </v-btn>
        <v-btn
          color="accent"
          variant="text"
          @click="submitForm"
          :disabled="bankSubmit"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
import { ref } from "vue";
import { useBanks } from "@/composables/banksComposable";

const { addBank } = useBanks();
const bankSubmit = ref(true);
const dialog = ref(false);
const bankForm = ref({
  bank_name: null,
});
const checkBank = async () => {
  if (bankForm.value.bank_name !== "" && bankForm.value.bank_name !== null) {
    bankSubmit.value = false;
  } else {
    bankSubmit.value = true;
  }
};
const submitForm = async () => {
  addBank(bankForm.value);
  dialog.value = false;
};
</script>
