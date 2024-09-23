<template>
  <v-card variant="outlined" :elevation="4" class="bg-white">
    <template v-slot:append>
      <v-tooltip text="Add Rule" location="top">
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-table-plus"
            flat
            variant="plain"
            v-bind="props"
            @click="importFileDialog = true"
          ></v-btn>
        </template>
      </v-tooltip>
    </template>
    <template v-slot:title>
      <span class="text-subtitle-2 text-secondary">Rules</span>
    </template>
    <template v-slot:text>
      <v-list :selected="rule_selected" nav>
        <v-list-item
          v-for="(item, i) in props.rules"
          :key="i"
          @click="selectRule(item.id)"
          color="accent"
          :value="item.id"
        >
          <v-list-item-title>{{ item.name }}</v-list-item-title>
          <template #append>
            <v-btn variant="plain" icon @click.stop="editRule(item.id)">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn variant="plain" icon @click.stop="deleteRule(item.id)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
    </template>
  </v-card>
</template>
<script setup>
import { ref, defineProps, defineEmits } from "vue";

const emit = defineEmits(["ruleSelected"]);

const rule_selected = ref(null);

const props = defineProps({
  rules: Object,
  isLoading: Boolean,
});

const selectRule = value => {
  emit("ruleSelected", value);
};
</script>
<style>
.icon-with-text {
  position: relative;
  display: inline-block;
}

.icon-text {
  position: absolute;
  top: 0;
  right: 1;
  color: black;
  padding: 4px 1px;
  font-size: 0.7rem;
}
</style>
