<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="pa-6" elevation="4" rounded="lg">
          <div class="d-flex justify-center mb-4">
            <v-img src="/logov2.png" max-width="150" />
          </div>

          <v-form @submit.prevent="handleLogin">
            <v-text-field
              v-model="username"
              label="Username"
              prepend-inner-icon="mdi-account"
              variant="outlined"
              density="comfortable"
              :disabled="loading"
              autofocus
              class="mb-3"
            />

            <v-text-field
              v-model="password"
              label="Password"
              prepend-inner-icon="mdi-lock"
              :type="showPassword ? 'text' : 'password'"
              :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
              variant="outlined"
              density="comfortable"
              :disabled="loading"
              class="mb-4"
              @click:append-inner="showPassword = !showPassword"
            />

            <v-alert v-if="error" type="error" density="compact" class="mb-4">
              {{ error }}
            </v-alert>

            <v-btn
              type="submit"
              color="primary"
              block
              size="large"
              :loading="loading"
            >
              Sign in
            </v-btn>
          </v-form>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
  import { ref } from "vue";
  import { useRouter, useRoute } from "vue-router";
  import { useAuthStore } from "@/stores/auth";

  const router = useRouter();
  const route = useRoute();
  const authStore = useAuthStore();

  const username = ref("");
  const password = ref("");
  const showPassword = ref(false);
  const loading = ref(false);
  const error = ref("");

  async function handleLogin() {
    if (!username.value || !password.value) {
      error.value = "Please enter your username and password.";
      return;
    }
    loading.value = true;
    error.value = "";
    try {
      await authStore.login(username.value, password.value);
      const redirect = route.query.redirect || "/";
      router.push(redirect);
    } catch {
      error.value = "Invalid username or password.";
    } finally {
      loading.value = false;
    }
  }
</script>
