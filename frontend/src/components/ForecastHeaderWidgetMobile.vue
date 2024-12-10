<template>
  <div>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-secondary pa-0 ga-0"
      v-if="!accounts_isLoading && accounts && accounts.length > 0"
    >
      <template v-slot:text>
        <v-row desnity="compact">
          <v-col>
            <v-slide-group
              v-model="account_selected"
              class="pa-1"
              selected-class="bg-accent"
              show-arrows
              center-active
            >
              <v-slide-group-item
                v-for="account in accounts"
                :key="account.id"
                v-slot="{ toggle, selectedClass }"
                :value="account.id"
                @group:selected="clickAccountUpdate"
              >
                <v-card
                  color="primary"
                  :class="['ma-1', selectedClass]"
                  height="75"
                  width="175"
                  @click="toggle"
                  ><template v-slot:prepend>
                    <v-icon :icon="account.account_type.icon"></v-icon>
                  </template>
                  <template v-slot:title>
                    <span class="text-subtitle-1 font-weight-bold">{{
                      account.account_name
                    }}</span>
                  </template>
                  <template v-slot:subtitle>
                    <span>{{ account.bank.bank_name }}</span>
                  </template>
                </v-card>
              </v-slide-group-item>
            </v-slide-group>
          </v-col>
        </v-row>
      </template>
    </v-card>
    <v-skeleton-loader
      type="card"
      v-if="accounts_isLoading"
    ></v-skeleton-loader>
    <v-card
      variant="outlined"
      :elevation="4"
      class="bg-secondary"
      v-if="accounts && accounts.length === 0"
      title="No Accounts"
    ></v-card>
  </div>
</template>
<script setup>
import { useAccounts } from "@/composables/accountsComposable";
import { ref, defineEmits } from "vue";

const emit = defineEmits(["updateAccount"]);
const account_selected = ref(null);
const { accounts, isLoading: accounts_isLoading } = useAccounts();

const clickAccountUpdate = () => {
  emit("updateAccount", account_selected.value);
};
</script>
