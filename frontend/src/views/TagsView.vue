<template>
  <div>
    <v-row class="pa-1 ga-1" no-gutters>
      <v-col class="rounded">
        <TagsHeaderWidget @tag-selected="clickSelectedTag" v-if="!isMobile" />
        <TagsHeaderWidgetMobile
          @tag-selected="clickSelectedTag"
          v-if="isMobile"
        />
      </v-col>
    </v-row>
    <TagTransactionsWidget
      :tagID="selected_tag"
      :key="selected_tag"
      v-if="selected_tag && !isMobile"
    />
    <TagTransactionsWidgetMobile
      :tagID="selected_tag"
      :key="selected_tag"
      v-if="selected_tag && isMobile"
    />
    <v-card v-else>
      <v-card-title>Please select a tag</v-card-title>
    </v-card>
  </div>
</template>
<script setup>
import TagsHeaderWidget from "@/components/TagsHeaderWidget.vue";
import TagsHeaderWidgetMobile from "@/components/TagsHeaderWidgetMobile.vue";
import { ref } from "vue";
import TagTransactionsWidget from "@/components/TagTransactionsWidget.vue";
import TagTransactionsWidgetMobile from "@/components/TagTransactionsWidgetMobile.vue";
import { useDisplay } from "vuetify";

const { smAndDown } = useDisplay();
const isMobile = smAndDown;

const selected_tag = ref(null);

const clickSelectedTag = tag_id => {
  selected_tag.value = tag_id;
};
</script>
