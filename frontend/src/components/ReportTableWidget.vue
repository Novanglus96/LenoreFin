<template>
  <div>
    <v-row class="pa-1 ga-1 ma-0 rounded" no-gutters>
      <v-col class="rounded pa-0 ga-0 ma-0">
        <v-card variant="outlined" :elevation="4" class="bg-surface w-100">
          <v-card-title class="text-left">
            <span class="text-subtitle-2 text-primary">
              {{ props.data[0].year1 }}
            </span>
          </v-card-title>
          <v-card-text class="ma-0 pa-0 ga-0">
            <v-data-table-server
              :headers="displayHeaders"
              :items="local_data ? local_data : []"
              :items-length="local_data ? local_data.length : 0"
              :loading="props.isLoading"
              no-data-text="No report data!"
              loading-text="Report transactions..."
              disable-sort
              :show-select="false"
              striped="odd"
              density="compact"
              :hide-default-footer="true"
              width="100%"
              class="ma-0 pa-0 ga-0 bg-background"
              :header-props="{ class: 'font-weight-bold bg-secondary' }"
            >
              <template v-slot:[`header.item`] v-if="mdAndUp">
                <div class="font-weight-bold"></div>
              </template>
              <template v-slot:[`header.jan`] v-if="mdAndUp">
                <div class="font-weight-bold text-center text-caption">Jan</div>
              </template>
              <template v-slot:[`header.feb`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Feb</div>
              </template>
              <template v-slot:[`header.mar`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Mar</div>
              </template>
              <template v-slot:[`header.apr`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Apr</div>
              </template>
              <template v-slot:[`header.may`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">May</div>
              </template>
              <template v-slot:[`header.jun`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Jun</div>
              </template>
              <template v-slot:[`header.jul`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Jul</div>
              </template>
              <template v-slot:[`header.aug`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Aug</div>
              </template>
              <template v-slot:[`header.sep`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Sep</div>
              </template>
              <template v-slot:[`header.oct`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Oct</div>
              </template>
              <template v-slot:[`header.nov`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Nov</div>
              </template>
              <template v-slot:[`header.dec`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">Dec</div>
              </template>
              <template v-slot:[`header.ytd`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">YTD</div>
              </template>
              <template v-slot:[`header.avg`] v-if="mdAndUp">
                <div class="font-weight-bold text-caption text-center">AVG</div>
              </template>
              <template v-slot:[`item.item`]="{ item }" v-if="mdAndUp">
                <div
                  class="text-right text-caption font-weight-bold text-primary"
                >
                  {{ item.item }}
                </div>
              </template>
              <template v-slot:[`item.jan`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.jan }}
                </div>
              </template>
              <template v-slot:[`item.feb`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.feb }}
                </div>
              </template>
              <template v-slot:[`item.mar`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.mar }}
                </div>
              </template>
              <template v-slot:[`item.apr`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.apr }}
                </div>
              </template>
              <template v-slot:[`item.may`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.may }}
                </div>
              </template>
              <template v-slot:[`item.jun`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.jun }}
                </div>
              </template>
              <template v-slot:[`item.jul`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.jul }}
                </div>
              </template>
              <template v-slot:[`item.aug`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.aug }}
                </div>
              </template>
              <template v-slot:[`item.sep`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.sep }}
                </div>
              </template>
              <template v-slot:[`item.oct`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.oct }}
                </div>
              </template>
              <template v-slot:[`item.nov`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.nov }}
                </div>
              </template>
              <template v-slot:[`item.dec`]="{ item }" v-if="mdAndUp">
                <div class="text-center text-caption">
                  {{ item.dec }}
                </div>
              </template>
              <template v-slot:[`item.ytd`]="{ item }" v-if="mdAndUp">
                <div
                  class="text-center text-caption font-weight-bold text-accent"
                >
                  {{ item.ytd }}
                </div>
              </template>
              <template v-slot:[`item.avg`]="{ item }" v-if="mdAndUp">
                <div
                  class="text-center text-caption font-weight-bold text-accent"
                >
                  {{ item.avg }}
                </div>
              </template>
              <!-- Mobile View -->
              <template v-slot:[`item.mobile`]="{ item }">
                <v-container class="ma-0 pa-0 ga-0">
                  <v-row dense class="ma-0 pa-0 ga-0">
                    <v-col class="ma-0 pa-0 ga-0 font-weight-bold text-primary">
                      {{ item.item }}
                    </v-col>
                  </v-row>
                  <v-row dense class="ma-0 pa-0 ga-0">
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Jan
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Feb
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Mar
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Apr
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      May
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Jun
                    </v-col>
                  </v-row>
                  <v-row dense class="ma-0 pa-0 ga-0">
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.jan }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.feb }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.mar }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.apr }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.may }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.jun }}
                    </v-col>
                  </v-row>
                  <v-row dense class="ma-0 pa-0 ga-0">
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Jul
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Aug
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Sep
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Oct
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Nov
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption"
                      cols="2"
                    >
                      Dec
                    </v-col>
                  </v-row>
                  <v-row dense class="ma-0 pa-0 ga-0">
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.jul }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.aug }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.sep }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.oct }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.nov }}
                    </v-col>
                    <v-col class="ma-0 pa-0 ga-0 text-caption" cols="2">
                      {{ item.dec }}
                    </v-col>
                  </v-row>
                  <v-row dense class="ma-0 pa-0 ga-0">
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption text-accent"
                      cols="6"
                    >
                      YTD
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 font-weight-bold text-caption text-accent"
                      cols="6"
                    >
                      AVG
                    </v-col>
                  </v-row>
                  <v-row dense class="ma-0 pa-0 ga-0">
                    <v-col
                      class="ma-0 pa-0 ga-0 text-caption text-accent"
                      cols="6"
                    >
                      {{ item.ytd }}
                    </v-col>
                    <v-col
                      class="ma-0 pa-0 ga-0 text-caption text-accent"
                      cols="6"
                    >
                      {{ item.avg }}
                    </v-col>
                  </v-row>
                </v-container>
              </template>
            </v-data-table-server>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
<script setup>
  import { ref, computed, defineProps } from "vue";
  import { useDisplay } from "vuetify";

  const props = defineProps({
    isLoading: Boolean,
    data: Array,
  });
  const { mdAndUp } = useDisplay();
  const local_data = computed(() => {
    let formatted_data = [];
    let totals = [];

    props.data.forEach(() => {
      totals.push(0);
    });

    const currentMonth = new Date().getMonth() + 1;
    props.data.forEach((row, index) => {
      const new_object = {};
      new_object.id = index;
      new_object.item = row.pretty_name;
      let total = 0;
      for (let i = 0; i <= 11; i++) {
        const date = new Date();
        date.setMonth(i);
        const monthname = date.toLocaleString("en-US", { month: "short" });
        const lower_monthname = monthname.toLowerCase();
        new_object[lower_monthname] = formatToUSD(
          parseFloat(row.data.datasets[0].data[i]),
        );
        total += parseFloat(row.data.datasets[0].data[i]);
      }
      new_object.ytd = formatToUSD(total);
      new_object.avg = formatToUSD(total / currentMonth);
      formatted_data.push(new_object);
    });

    return formatted_data;
  });

  const headers = ref([
    { title: "", key: "item", width: "10px" },
    { title: "Jan", key: "jan" },
    { title: "Feb", key: "feb" },
    { title: "Mar", key: "mar" },
    { title: "Apr", key: "apr" },
    { title: "May", key: "may" },
    { title: "Jun", key: "jun" },
    { title: "Jul", key: "jul" },
    { title: "Aug", key: "aug" },
    { title: "Sep", key: "sep" },
    { title: "Oct", key: "oct" },
    { title: "Nov", key: "nov" },
    { title: "Dec", key: "dec" },
    { title: "YTD", key: "ytd" },
    { title: "AVG", key: "avg" },
  ]);
  const displayHeaders = computed(() => {
    if (mdAndUp.value) {
      return headers.value;
    }
    // For small screens, use your single mobile column
    return [{ title: "", key: "mobile" }];
  });

  const formatToUSD = amount => {
    return amount.toLocaleString("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    });
  };
</script>
