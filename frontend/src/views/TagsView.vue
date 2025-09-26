<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <TagsHeaderWidget @tag-selected="clickSelectedTag" />
      </v-col>
    </v-row>
    <TagTransactionsWidget
      :tagID="selected_tag"
      :key="selected_tag"
      v-if="selected_tag"
    />
    <div v-else>
      <v-row class="pa-1 ga-1 rounded" no-gutters>
        <v-col class="rounded">
          <v-card variant="outlined" :elevation="4" class="bg-surface">
            <v-card-text class="text-center">
              <span class="text-subtitle-2 text-error">
                Please select a tag...
              </span>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>
</template>
<script setup>
  import TagsHeaderWidget from "@/components/TagsHeaderWidget.vue";
  import { ref } from "vue";
  import TagTransactionsWidget from "@/components/TagTransactionsWidget.vue";

  const selected_tag = ref(null);

  const clickSelectedTag = tag_id => {
    selected_tag.value = tag_id;
  };
</script>
