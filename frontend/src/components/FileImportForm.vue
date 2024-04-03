<template>
  <v-dialog persistent width="75%">
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
              title="Status Mappings"
              icon="mdi-relation-many-to-many"
              :complete="step2Complete"
            ></v-stepper-item>
            <v-stepper-item
              value="3"
              title="Type Mappings"
              icon="mdi-relation-many-to-many"
              :complete="step3Complete"
            ></v-stepper-item>
            <v-stepper-item
              value="4"
              title="Tag Mappings"
              icon="mdi-relation-many-to-many"
              :complete="step4Complete"
            ></v-stepper-item>
            <v-stepper-item
              value="5"
              title="Account Mappings"
              icon="mdi-relation-many-to-many"
              :complete="step5Complete"
            ></v-stepper-item>
            <v-divider color="accent" thickness="2"></v-divider>
            <v-stepper-item
              value="6"
              title="Transaction Errors"
              icon="mdi-marker-check"
              :complete="step6Complete"
            ></v-stepper-item>
            <v-divider color="accent" thickness="2"></v-divider>
            <v-stepper-item
              value="7"
              title="Summary"
              icon="mdi-text-box"
              :complete="step7Complete"
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
              <span
                class="text-subtitle-2 font-italic text-error"
                v-if="!fileIsValid"
                >*** There's a problem with the file you uploaded. Make sure to
                check the formatting and use this
                <a href="/example.csv">example</a> as a template.</span
              >
            </v-stepper-window-item>
            <v-stepper-window-item value="2">
              <v-data-iterator
                :items="mappings.transaction_statuses"
                item-value="file_status"
                :items-per-page="4"
              >
                <template
                  v-slot:header="{ page, pageCount, prevPage, nextPage }"
                >
                  <h1
                    class="text-subtitle-2 font-weight-bold d-flex justify-space-between mb-4 align-center"
                  >
                    <div class="text-truncate">Status Mappings</div>
                    <div class="d-flex align-center">
                      <div class="d-inline-flex">
                        <v-btn
                          :disabled="page === 1"
                          class="me-2"
                          icon="mdi-arrow-left"
                          size="small"
                          variant="tonal"
                          @click="prevPage"
                        ></v-btn>

                        <v-btn
                          :disabled="page === pageCount"
                          icon="mdi-arrow-right"
                          size="small"
                          variant="tonal"
                          @click="nextPage"
                        ></v-btn>
                      </div>
                    </div>
                  </h1>
                </template>
                <template v-slot:default="{ items }">
                  <v-row>
                    <v-col
                      v-for="(item, i) in items"
                      :key="i"
                      cols="12"
                      sm="6"
                      xl="3"
                    >
                      <v-sheet border
                        ><v-container
                          ><v-row dense
                            ><v-col>{{ item.raw.file_status }}</v-col></v-row
                          ><v-row dense
                            ><v-col class="text-center text-caption font-bold"
                              >will be mapped to</v-col
                            ></v-row
                          ><v-row dense
                            ><v-col
                              ><v-autocomplete
                                clearable
                                label="Status*"
                                :items="transaction_statuses"
                                variant="outlined"
                                :loading="transaction_statuses_isLoading"
                                item-title="transaction_status"
                                item-value="id"
                                v-model="item.raw.status_id"
                                :rules="required"
                                density="compact"
                                @update:model-value="updateStep2Complete"
                              ></v-autocomplete></v-col></v-row></v-container></v-sheet></v-col
                  ></v-row>
                </template>
                <template v-slot:footer="{ page, pageCount }">
                  <v-footer
                    class="justify-space-between text-body-2 mt-4"
                    color="surface-variant"
                  >
                    Total status(es): {{ mappings.transaction_statuses.length }}

                    <div>Page {{ page }} of {{ pageCount }}</div>
                  </v-footer>
                </template>
              </v-data-iterator>
            </v-stepper-window-item>
            <v-stepper-window-item value="3">
              <v-data-iterator
                :items="mappings.transaction_types"
                item-value="file_type"
                :items-per-page="4"
              >
                <template
                  v-slot:header="{ page, pageCount, prevPage, nextPage }"
                >
                  <h1
                    class="text-subtitle-2 font-weight-bold d-flex justify-space-between mb-4 align-center"
                  >
                    <div class="text-truncate">Type Mappings</div>
                    <div class="d-flex align-center">
                      <div class="d-inline-flex">
                        <v-btn
                          :disabled="page === 1"
                          class="me-2"
                          icon="mdi-arrow-left"
                          size="small"
                          variant="tonal"
                          @click="prevPage"
                        ></v-btn>

                        <v-btn
                          :disabled="page === pageCount"
                          icon="mdi-arrow-right"
                          size="small"
                          variant="tonal"
                          @click="nextPage"
                        ></v-btn>
                      </div>
                    </div>
                  </h1>
                </template>
                <template v-slot:default="{ items }">
                  <v-row>
                    <v-col
                      v-for="(item, i) in items"
                      :key="i"
                      cols="12"
                      sm="6"
                      xl="3"
                    >
                      <v-sheet border
                        ><v-container
                          ><v-row dense
                            ><v-col>{{ item.raw.file_type }}</v-col></v-row
                          ><v-row dense
                            ><v-col class="text-center text-caption font-bold"
                              >will be mapped to</v-col
                            ></v-row
                          ><v-row dense
                            ><v-col
                              ><v-autocomplete
                                clearable
                                label="Status*"
                                :items="transaction_types"
                                variant="outlined"
                                :loading="transaction_types_isLoading"
                                item-title="transaction_type"
                                item-value="id"
                                v-model="item.raw.type_id"
                                :rules="required"
                                density="compact"
                                @update:model-value="updateStep3Complete"
                              ></v-autocomplete></v-col></v-row></v-container></v-sheet></v-col
                  ></v-row>
                </template>
                <template v-slot:footer="{ page, pageCount }">
                  <v-footer
                    class="justify-space-between text-body-2 mt-4"
                    color="surface-variant"
                  >
                    Total type(s): {{ mappings.transaction_types.length }}

                    <div>Page {{ page }} of {{ pageCount }}</div>
                  </v-footer>
                </template>
              </v-data-iterator>
            </v-stepper-window-item>
            <v-stepper-window-item value="4">
              <v-data-iterator
                :items="mappings.tags"
                item-value="file_tag"
                :items-per-page="4"
              >
                <template
                  v-slot:header="{ page, pageCount, prevPage, nextPage }"
                >
                  <h1
                    class="text-subtitle-2 font-weight-bold d-flex justify-space-between mb-4 align-center"
                  >
                    <div class="text-truncate">Tag Mappings</div>
                    <div class="d-flex align-center">
                      <div class="d-inline-flex">
                        <v-btn
                          :disabled="page === 1"
                          class="me-2"
                          icon="mdi-arrow-left"
                          size="small"
                          variant="tonal"
                          @click="prevPage"
                        ></v-btn>

                        <v-btn
                          :disabled="page === pageCount"
                          icon="mdi-arrow-right"
                          size="small"
                          variant="tonal"
                          @click="nextPage"
                        ></v-btn>
                      </div>
                    </div>
                  </h1>
                </template>
                <template v-slot:default="{ items }">
                  <v-row>
                    <v-col
                      v-for="(item, i) in items"
                      :key="i"
                      cols="12"
                      sm="6"
                      xl="3"
                    >
                      <v-sheet border
                        ><v-container
                          ><v-row dense
                            ><v-col>{{ item.raw.file_tag }}</v-col></v-row
                          ><v-row dense
                            ><v-col class="text-center text-caption font-bold"
                              >will be mapped to</v-col
                            ></v-row
                          ><v-row dense
                            ><v-col
                              ><v-autocomplete
                                clearable
                                label="Tag*"
                                :items="tags"
                                variant="outlined"
                                :loading="tags_isLoading"
                                item-title="tag_name"
                                item-value="id"
                                v-model="item.raw.tag_id"
                                :rules="required"
                                density="compact"
                                @update:model-value="updateStep4Complete"
                              >
                                <template v-slot:item="{ props, item }">
                                  <v-list-item
                                    v-bind="props"
                                    :title="
                                      item.raw.parent
                                        ? item.raw.parent.tag_name
                                        : item.raw.tag_name
                                    "
                                    :subtitle="
                                      item.raw.parent ? item.raw.tag_name : null
                                    "
                                  >
                                    <template v-slot:prepend>
                                      <v-icon
                                        icon="mdi-tag"
                                        :color="tagColor(item.raw.tag_type.id)"
                                      ></v-icon>
                                    </template>
                                  </v-list-item>
                                </template> </v-autocomplete></v-col></v-row></v-container></v-sheet></v-col
                  ></v-row>
                </template>
                <template v-slot:footer="{ page, pageCount }">
                  <v-footer
                    class="justify-space-between text-body-2 mt-4"
                    color="surface-variant"
                  >
                    Total tag(s): {{ mappings.tags.length }}

                    <div>Page {{ page }} of {{ pageCount }}</div>
                  </v-footer>
                </template>
              </v-data-iterator>
            </v-stepper-window-item>
            <v-stepper-window-item value="5">
              <v-data-iterator
                :items="mappings.accounts"
                item-value="file_account"
                :items-per-page="4"
              >
                <template
                  v-slot:header="{ page, pageCount, prevPage, nextPage }"
                >
                  <h1
                    class="text-subtitle-2 font-weight-bold d-flex justify-space-between mb-4 align-center"
                  >
                    <div class="text-truncate">Account Mappings</div>
                    <div class="d-flex align-center">
                      <div class="d-inline-flex">
                        <v-btn
                          :disabled="page === 1"
                          class="me-2"
                          icon="mdi-arrow-left"
                          size="small"
                          variant="tonal"
                          @click="prevPage"
                        ></v-btn>

                        <v-btn
                          :disabled="page === pageCount"
                          icon="mdi-arrow-right"
                          size="small"
                          variant="tonal"
                          @click="nextPage"
                        ></v-btn>
                      </div>
                    </div>
                  </h1>
                </template>
                <template v-slot:default="{ items }">
                  <v-row>
                    <v-col
                      v-for="(item, i) in items"
                      :key="i"
                      cols="12"
                      sm="6"
                      xl="3"
                    >
                      <v-sheet border
                        ><v-container
                          ><v-row dense
                            ><v-col>{{ item.raw.file_account }}</v-col></v-row
                          ><v-row dense
                            ><v-col class="text-center text-caption font-bold"
                              >will be mapped to</v-col
                            ></v-row
                          ><v-row dense
                            ><v-col
                              ><v-autocomplete
                                clearable
                                label="Account*"
                                :items="accounts"
                                variant="outlined"
                                :loading="accounts_isLoading"
                                item-title="account_name"
                                item-value="id"
                                v-model="item.raw.account_id"
                                :rules="required"
                                density="compact"
                                @update:model-value="updateStep5Complete"
                              ></v-autocomplete></v-col></v-row></v-container></v-sheet></v-col
                  ></v-row>
                </template>
                <template v-slot:footer="{ page, pageCount }">
                  <v-footer
                    class="justify-space-between text-body-2 mt-4"
                    color="surface-variant"
                  >
                    Total account(s): {{ mappings.accounts.length }}

                    <div>Page {{ page }} of {{ pageCount }}</div>
                  </v-footer>
                </template>
              </v-data-iterator>
            </v-stepper-window-item>
            <v-stepper-window-item value="6">
              <v-data-iterator
                :items="mappings.transactions"
                item-value="description"
                :items-per-page="2"
              >
                <template
                  v-slot:header="{ page, pageCount, prevPage, nextPage }"
                >
                  <h1
                    class="text-subtitle-2 font-weight-bold d-flex justify-space-between mb-4 align-center"
                  >
                    <div class="text-truncate">Transaction Errors</div>
                    <div class="d-flex align-center">
                      <div class="d-inline-flex">
                        <v-btn
                          :disabled="page === 1"
                          class="me-2"
                          icon="mdi-arrow-left"
                          size="small"
                          variant="tonal"
                          @click="prevPage"
                        ></v-btn>

                        <v-btn
                          :disabled="page === pageCount"
                          icon="mdi-arrow-right"
                          size="small"
                          variant="tonal"
                          @click="nextPage"
                        ></v-btn>
                      </div>
                    </div>
                  </h1>
                </template>
                <template v-slot:default="{ items }">
                  <v-row>
                    <v-col v-for="(item, i) in items" :key="i" sm="6" xl="3">
                      <v-sheet border
                        ><v-container>
                          <v-row dense>
                            <v-col>Line #{{ item.raw.line_id }}</v-col>
                          </v-row>
                          <v-row dense
                            ><v-col
                              ><span class="text-h6 font-bold">Errors:</span
                              ><br />
                              <span
                                v-for="(error, j) in item.raw.errors"
                                :key="j"
                                :class="
                                  error.status == 0
                                    ? 'font-italic text-subtitle-2 text-error'
                                    : 'text-subtitle-2 text-grey text-decoration-line-through'
                                "
                                >{{ error.text
                                }}<span
                                  v-if="j < item.raw.errors.length - 1"
                                  class="text-black font-bold"
                                >
                                  &bull;
                                </span>
                              </span></v-col
                            >
                          </v-row>
                          <v-row dense>
                            <v-col
                              ><VueDatePicker
                                v-model="item.raw.transactionDate"
                                timezone="America/New_York"
                                model-type="yyyy-MM-dd"
                                :enable-time-picker="false"
                                auto-apply
                                format="yyyy-MM-dd"
                                :teleport="true"
                                @update:model-value="verifyErrors(i)"
                              ></VueDatePicker
                            ></v-col>
                          </v-row>
                          <v-row dense>
                            <v-col
                              ><v-autocomplete
                                clearable
                                label="Transaction Type*"
                                :items="transaction_types"
                                variant="outlined"
                                :loading="transaction_types_isLoading"
                                item-title="transaction_type"
                                item-value="id"
                                v-model="item.raw.transactionTypeID"
                                :rules="required"
                                density="compact"
                                @update:model-value="verifyErrors(i)"
                              ></v-autocomplete
                            ></v-col>
                            <v-col>
                              <v-autocomplete
                                clearable
                                label="Transaction Status*"
                                :items="transaction_statuses"
                                variant="outlined"
                                :loading="transaction_statuses_isLoading"
                                item-title="transaction_status"
                                item-value="id"
                                v-model="item.raw.transactionStatusID"
                                :rules="required"
                                density="compact"
                                @update:model-value="verifyErrors(i)"
                              ></v-autocomplete>
                            </v-col>
                          </v-row>
                          <v-row dense>
                            <v-col>
                              <v-text-field
                                v-model="item.raw.amount"
                                variant="outlined"
                                label="Amount*"
                                :rules="required"
                                prefix="$"
                                type="number"
                                step="1.00"
                                density="compact"
                                @update:model-value="verifyErrors(i)"
                              ></v-text-field>
                            </v-col>
                            <v-col>
                              <v-text-field
                                v-model="item.raw.description"
                                variant="outlined"
                                label="Description*"
                                :rules="required"
                                density="compact"
                                @update:model-value="verifyErrors(i)"
                              ></v-text-field>
                            </v-col>
                          </v-row>
                          <v-row dense>
                            <v-col>
                              <v-autocomplete
                                clearable
                                label="Source Account*"
                                :items="accounts"
                                variant="outlined"
                                :loading="accounts_isLoading"
                                item-title="account_name"
                                item-value="id"
                                v-model="item.raw.sourceAccountID"
                                :rules="required"
                                density="compact"
                                @update:model-value="verifyErrors(i)"
                              >
                                <template v-slot:item="{ props, item }">
                                  <v-list-item
                                    v-bind="props"
                                    :title="item.raw.account_name"
                                    :subtitle="item.raw.bank.bank_name"
                                  >
                                    <template v-slot:prepend>
                                      <v-icon
                                        :icon="item.raw.account_type.icon"
                                      ></v-icon>
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
                                v-model="item.raw.destinationAccountID"
                                :rules="required"
                                density="compact"
                                @update:model-value="verifyErrors(i)"
                              >
                                <template v-slot:item="{ props, item }">
                                  <v-list-item
                                    v-bind="props"
                                    :title="item.raw.account_name"
                                    :subtitle="item.raw.bank.bank_name"
                                  >
                                    <template v-slot:prepend>
                                      <v-icon
                                        :icon="item.raw.account_type.icon"
                                      ></v-icon>
                                    </template>
                                  </v-list-item>
                                </template>
                              </v-autocomplete>
                            </v-col>
                          </v-row>
                          <v-row dense>
                            <v-col>
                              <v-textarea
                                clearable
                                label="Memo"
                                variant="outlined"
                                v-model="item.raw.memo"
                                :rows="2"
                                no-resize
                                @update:model-value="verifyErrors(i)"
                              ></v-textarea>
                            </v-col>
                          </v-row>
                          <v-row dense>
                            <v-col>
                              <TagTable
                                :key="i"
                                v-if="item.raw.transactionTypeID !== 3"
                                :tags="item.raw.tags"
                                :totalAmount="item.raw.amount"
                                :noItems="2"
                                :transID="i"
                                @tag-table-updated="updateTags"
                              ></TagTable>
                            </v-col>
                          </v-row>
                        </v-container>
                      </v-sheet>
                    </v-col>
                  </v-row>
                </template>
                <template v-slot:footer="{ page, pageCount }">
                  <v-footer
                    class="justify-space-between text-body-2 mt-4"
                    color="surface-variant"
                  >
                    Total transaction(s): {{ mappings.transactions.length }}

                    <div>Page {{ page }} of {{ pageCount }}</div>
                  </v-footer>
                </template>
              </v-data-iterator>
            </v-stepper-window-item>
            <v-stepper-window-item value="7">
              <v-banner><v-banner-text>Summary</v-banner-text></v-banner>
              <v-timeline side="end">
                <v-timeline-item size="small" dot-color="secondary">
                  <v-alert
                    color="secondary"
                    icon="mdi-information"
                    :value="true"
                    title="Transaction Status Mappings"
                  >
                    <v-container>
                      <v-row
                        dense
                        v-for="(status, i) in mappings.transaction_statuses"
                        :key="i"
                      >
                        <v-col
                          ><span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{ status.file_status }}</span
                          >
                          will be mapped to
                          <span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{
                              transaction_statuses.find(
                                item => item.id === status.status_id,
                              ).transaction_status
                            }}</span
                          ></v-col
                        >
                      </v-row>
                    </v-container>
                  </v-alert>
                </v-timeline-item>
                <v-timeline-item size="small" dot-color="secondary">
                  <v-alert
                    color="secondary"
                    icon="mdi-information"
                    :value="true"
                    title="Transaction Type Mappings"
                  >
                    <v-container>
                      <v-row
                        dense
                        v-for="(type, i) in mappings.transaction_types"
                        :key="i"
                      >
                        <v-col
                          ><span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{ type.file_type }}</span
                          >
                          will be mapped to
                          <span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{
                              transaction_types.find(
                                item => item.id === type.type_id,
                              ).transaction_type
                            }}</span
                          ></v-col
                        >
                      </v-row>
                    </v-container>
                  </v-alert>
                </v-timeline-item>
                <v-timeline-item size="small" dot-color="secondary">
                  <v-alert
                    color="secondary"
                    icon="mdi-information"
                    :value="true"
                    title="Tag Mappings"
                  >
                    <v-container>
                      <v-row dense v-for="(tag, i) in mappings.tags" :key="i">
                        <v-col
                          ><span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{ tag.file_tag }}</span
                          >
                          will be mapped to
                          <span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{
                              tags.find(item => item.id === tag.tag_id).tag_name
                            }}</span
                          ></v-col
                        >
                      </v-row>
                    </v-container>
                  </v-alert>
                </v-timeline-item>
                <v-timeline-item size="small" dot-color="secondary">
                  <v-alert
                    color="secondary"
                    icon="mdi-information"
                    :value="true"
                    title="Account Mappings"
                  >
                    <v-container>
                      <v-row
                        dense
                        v-for="(account, i) in mappings.accounts"
                        :key="i"
                      >
                        <v-col
                          ><span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{ account.file_account }}</span
                          >
                          will be mapped to
                          <span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >{{
                              accounts.find(
                                item => item.id === account.account_id,
                              ).account_name
                            }}</span
                          ></v-col
                        >
                      </v-row>
                    </v-container>
                  </v-alert>
                </v-timeline-item>
                <v-timeline-item size="small" dot-color="secondary">
                  <v-alert
                    color="secondary"
                    icon="mdi-information"
                    :value="true"
                    title="Fixed Transaction Errors"
                  >
                    <v-container>
                      <v-row
                        dense
                        v-for="(transaction, i) in mappings.transactions"
                        :key="i"
                      >
                        <v-col
                          >#{{ transaction.line_id }}:
                          {{ transaction.transactionDate }} &bull;
                          {{ transaction.description }} &bull; ${{
                            transaction.amount
                          }}</v-col
                        >
                        <v-col
                          ><span
                            class="font-weight-bold text-subtitle-2 text-decoration-underline"
                            >Fixed:
                          </span>
                          <span
                            v-for="(error, e) in transaction.errors"
                            :key="e"
                            >{{ error.text
                            }}<span
                              class="font-weight-bold text-accent"
                              v-if="e < transaction.errors.length - 1"
                            >
                              &bull;
                            </span></span
                          ></v-col
                        >
                      </v-row>
                    </v-container>
                  </v-alert>
                </v-timeline-item>
              </v-timeline>
              <p class="text-subtitle-2 font-italic text-error">
                * Imports can take up to 5 minutes to process on the backend.
                Check the inbox or logs for updates.
                <br />* Duplicates WILL be imported.
              </p>
            </v-stepper-window-item>
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
          :disabled="!allStepsComplete"
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
import { uploadFile } from "@/composables/fileImportComposable";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";
import TagTable from "@/components/TagTable";

// Define reactive variables...
const step = ref(0);
const fileToImport = ref(null);
const step1Complete = ref(false);
const step2Complete = ref(false);
const step3Complete = ref(false);
const step4Complete = ref(false);
const step5Complete = ref(false);
const step6Complete = ref(false);
const nextDisabled = ref(true);
const fileIsValid = ref(true);
const fileData = ref(null);
const allStepsComplete = ref(false);

// Initialize Mappings
const mappings = ref({
  transaction_types: [],
  transaction_statuses: [],
  accounts: [],
  tags: [],
  transactions: [],
});

// Define emits
const emit = defineEmits(["updateDialog"]);

// API calls and data retrieval...

const { transaction_types, isLoading: transaction_types_isLoading } =
  useTransactionTypes();
const { transaction_statuses, isLoading: transaction_statuses_isLoading } =
  useTransactionStatuses();
const { accounts, isLoading: accounts_isLoading } = useAccounts();
const { tags, isLoading: tags_isLoading } = useTags();

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
  step5Complete.value = false;
  step6Complete.value = false;
  allStepsComplete.value = false;
  nextDisabled.value = true;
  mappings.value = {
    transaction_types: [],
    transaction_statuses: [],
    accounts: [],
    tags: [],
    transactions: [],
  };
  fileIsValid.value = true;
  emit("updateDialog", false);
};

/**
 * `nextStep` Advances the stepper to next step.
 */
const nextStep = () => {
  if (step.value < 7) {
    if (fileIsValid.value) {
      nextDisabled.value = true;
      step.value++;
    }
  }
  if (step6Complete.value) {
    allStepsComplete.value = true;
  } else {
    allStepsComplete.value = false;
  }
  if (step.value == 1) {
    updateStep2Complete();
  }
  if (step.value == 2) {
    updateStep3Complete();
  }
  if (step.value == 3) {
    updateStep4Complete();
  }
  if (step.value == 4) {
    updateStep5Complete();
  }
  if (step.value == 5) {
    updateStep6Complete();
  }
};

/**
 * `updateStep1Complete` Updates Step 1 Completed status.
 */
const updateStep1Complete = async () => {
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
 * `updateStep2Complete` Updates Step 2 Completed status.
 */
const updateStep2Complete = () => {
  let totalComplete = 0;
  for (let x = 0; x < mappings.value.transaction_statuses.length; x++) {
    if (mappings.value.transaction_statuses[x].status_id !== null) {
      totalComplete += 1;
    }
  }
  if (totalComplete == mappings.value.transaction_statuses.length) {
    step2Complete.value = true;
    nextDisabled.value = false;
  } else {
    step2Complete.value = false;
    nextDisabled.value = true;
  }
};

/**
 * `updateStep3Complete` Updates Step 3 Completed status.
 */
const updateStep3Complete = () => {
  let totalComplete = 0;
  for (let x = 0; x < mappings.value.transaction_types.length; x++) {
    if (mappings.value.transaction_types[x].type_id !== null) {
      totalComplete += 1;
    }
  }
  if (totalComplete == mappings.value.transaction_types.length) {
    step3Complete.value = true;
    nextDisabled.value = false;
  } else {
    step3Complete.value = false;
    nextDisabled.value = true;
  }
};

/**
 * `updateStep4Complete` Updates Step 4 Completed status.
 */
const updateStep4Complete = () => {
  let totalComplete = 0;
  for (let x = 0; x < mappings.value.tags.length; x++) {
    if (mappings.value.tags[x].tag_id !== null) {
      totalComplete += 1;
    }
  }
  if (totalComplete == mappings.value.tags.length) {
    step4Complete.value = true;
    nextDisabled.value = false;
  } else {
    step4Complete.value = false;
    nextDisabled.value = true;
  }
};

/**
 * `updateStep5Complete` Updates Step 5 Completed status.
 */
const updateStep5Complete = () => {
  let totalComplete = 0;
  for (let x = 0; x < mappings.value.accounts.length; x++) {
    if (mappings.value.accounts[x].account_id !== null) {
      totalComplete += 1;
    }
  }
  if (totalComplete == mappings.value.accounts.length) {
    verifyTransactions(fileData.value);
    step5Complete.value = true;
    nextDisabled.value = false;
  } else {
    step5Complete.value = false;
    nextDisabled.value = true;
  }
};

/**
 * `updateStep6Complete` Updates Step 6 Completed status.
 */
const updateStep6Complete = () => {
  if (
    verifyBaseRequired() == true &&
    verifyTagTotal() == true &&
    verifyTransactionType() == true
  ) {
    step6Complete.value = true;
    nextDisabled.value = false;
  } else {
    step6Complete.value = false;
    nextDisabled.value = true;
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
    fileData.value = parseCSV(contents);
    verifyFile(fileData.value);
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
      let formatted_header = header[j].trim();
      let formatted_value = values[j].trim();
      if (
        (formatted_header.startsWith('"') && formatted_header.endsWith('"')) ||
        (formatted_header.startsWith("'") && formatted_header.endsWith("'"))
      ) {
        formatted_header = formatted_header.slice(1, -1);
      }
      if (
        (formatted_value.startsWith('"') && formatted_value.endsWith('"')) ||
        (formatted_value.startsWith("'") && formatted_value.endsWith("'"))
      ) {
        formatted_value = formatted_value.slice(1, -1);
      }
      obj[formatted_header] = formatted_value;
    }
    data.push(obj);
  }
  return data;
};

/**
 * `verifyFile` Verifies the integrity of the file.
 */
const verifyFile = data => {
  if (
    data.length >= 1 &&
    data[0].TransactionDate &&
    data[0].TransactionType &&
    data[0].TransactionStatus &&
    data[0].Amount &&
    data[0].Description &&
    data[0].SourceAccount
  ) {
    fileIsValid.value = true;
    createMappings(data);
  } else {
    fileIsValid.value = false;
    mappings.value = {
      transaction_types: [],
      transaction_statuses: [],
      accounts: [],
      tags: [],
      transactions: [],
    };
  }
};

/**
 * `verifyTransactions` Verifies transaction integrity.
 */
const verifyTransactions = transactions => {
  for (let i = 0; i < transactions.length; i++) {
    let transaction = transactions[i];
    let trans_obj = {
      line_id: i,
      transactionDate: transaction.TransactionDate,
      transactionTypeID: null,
      transactionStatusID: null,
      amount: transaction.Amount,
      description: transaction.Description,
      sourceAccountID: null,
      destinationAccountID: null,
      tags: [],
      memo: transaction.Memo,
      errors: [],
    };

    // Format tags
    if (transaction.Tags) {
      const tagStrings = transaction.Tags.split(";");
      const tagObjects = tagStrings.map(tagString => {
        const [tagName, tagAmount] = tagString.split(":");
        return {
          tag_id: null,
          tag_name: tagName.trim(),
          tag_amount: parseFloat(tagAmount.trim()),
        };
      });
      for (let o = 0; o < tagObjects.length; o++) {
        for (let t = 0; t < mappings.value.tags.length; t++) {
          if (tagObjects[o].tag_name == mappings.value.tags[t].file_tag) {
            tagObjects[o].tag_id = mappings.value.tags[t].tag_id;
            break;
          }
        }
      }
      trans_obj.tags = tagObjects;
    }
    // Verify required fields are filled out and correct format
    if (
      transaction.TransactionDate == null ||
      transaction.TransactionDate === ""
    ) {
      trans_obj.errors.push({ text: "Missing Date", status: 0 });
      trans_obj.transactionDate = null;
    } else {
      if (!isValidDateFormat(transaction.TransactionDate)) {
        trans_obj.errors.push({ text: "Invalid Date", status: 0 });
        trans_obj.transactionDate = null;
      }
    }
    if (
      transaction.TransactionType == null ||
      transaction.TransactionType === ""
    ) {
      trans_obj.errors.push({ text: "Missing Transaction Type", status: 0 });
      trans_obj.transactionTypeID = null;
    } else {
      for (let y = 0; y < mappings.value.transaction_types.length; y++) {
        if (
          mappings.value.transaction_types[y].file_type ==
          transaction.TransactionType
        ) {
          trans_obj.transactionTypeID =
            mappings.value.transaction_types[y].type_id;
          break;
        }
      }
      if (
        trans_obj.transactionTypeID === 3 &&
        (transaction.DestinationAccount == null ||
          transaction.DestinationAccount === "")
      ) {
        trans_obj.errors.push({
          text: "Missing Transfer Destination Account",
          status: 0,
        });
        trans_obj.destinationAccountID = null;
      }
    }
    if (
      transaction.TransactionStatus == null ||
      transaction.TransactionStatus === ""
    ) {
      trans_obj.errors.push({ text: "Missing Transaction Status", status: 0 });
      trans_obj.transactionStatusID = null;
    } else {
      for (let s = 0; s < mappings.value.transaction_statuses.length; s++) {
        if (
          mappings.value.transaction_statuses[s].file_status ==
          transaction.TransactionStatus
        ) {
          trans_obj.transactionStatusID =
            mappings.value.transaction_statuses[s].status_id;
          break;
        }
      }
    }
    if (transaction.Amount == null || transaction.Amount === "") {
      trans_obj.errors.push({ text: "Missing Amount", status: 0 });
      trans_obj.amount = null;
    } else {
      if (!isValidFloat(transaction.Amount)) {
        trans_obj.errors.push({ text: "Invalid Amount", status: 0 });
        trans_obj.amount = null;
      }
    }
    if (transaction.Description == null || transaction.Description === "") {
      trans_obj.errors.push({ text: "Missing Description", status: 0 });
      trans_obj.description = null;
    }
    if (transaction.SourceAccount == null || transaction.SourceAccount === "") {
      trans_obj.errors.push({ text: "Missing Source Account", status: 0 });
      trans_obj.sourceAccountID = null;
    } else {
      for (let sa = 0; sa < mappings.value.accounts.length; sa++) {
        if (
          mappings.value.accounts[sa].file_account == transaction.SourceAccount
        ) {
          trans_obj.sourceAccountID = mappings.value.accounts[sa].account_id;
        }
      }
    }
    if (
      transaction.DestinationAccount !== null &&
      transaction.DestinationAccount !== "" &&
      trans_obj.transactionTypeID !== 3
    ) {
      trans_obj.errors.push({
        text: "Destination Account Set For Non Transfer",
        status: 0,
      });
    }
    if (transaction.Tags !== null && transaction.Tags !== "") {
      let tag_total = 0;
      for (let k = 0; k < trans_obj.tags.length; k++) {
        tag_total += trans_obj.tags[k].tag_amount;
      }
      if (parseFloat(tag_total) !== parseFloat(transaction.Amount)) {
        trans_obj.errors.push({ text: "Tags Do Not Equal Total", status: 0 });
      }
    }

    if (trans_obj.errors.length > 0) {
      mappings.value.transactions.push(trans_obj);
    }
  }
};

/**
 * `verifyErrors` Updates error status if errors are resolved.
 */
const verifyErrors = i => {
  let transaction = mappings.value.transactions[i];
  for (let x = 0; x < transaction.errors.length; x++) {
    const error = transaction.errors[x];
    if (error.text == "Invalid Amount") {
      if (isValidFloat(transaction.amount)) {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Missing Date") {
      if (
        transaction.transactionDate !== null &&
        transaction.transactionDate !== ""
      ) {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Invalid Date") {
      if (isValidDateFormat(transaction.transactionDate)) {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Missing Transaction Type") {
      if (
        transaction.transactionTypeID !== null &&
        transaction.transactionTypeID !== ""
      ) {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Missing Amount") {
      if (transaction.amount !== null && transaction.amount !== "") {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Missing Description") {
      if (transaction.description !== null && transaction.description !== "") {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Missing Source Account") {
      if (
        transaction.sourceAccountID !== null &&
        transaction.sourceAccountID !== ""
      ) {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Destination Account Set For Non Transfer") {
      if (
        transaction.transactionTypeID !== 3 &&
        (transaction.destinationAccountID == null ||
          transaction.destinationAccountID == "")
      ) {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Tags Do Not Equal Total") {
      if (transaction.tags !== null && transaction.tags !== "") {
        let tag_total = 0;
        for (let k = 0; k < transaction.tags.length; k++) {
          tag_total += transaction.tags[k].tag_amount;
        }
        if (parseFloat(tag_total) == parseFloat(transaction.amount)) {
          error.status = 1;
        } else {
          error.status = 0;
        }
      } else {
        error.status = 0;
      }
    }
    if (error.text == "Missing Transfer Destination Account") {
      if (
        transaction.destinationAccountID !== null &&
        transaction.destinationAccountID !== ""
      ) {
        error.status = 1;
      } else {
        error.status = 0;
      }
    }
  }
  updateStep6Complete();
};

/**
 * `verifyBaseRequired` Verifies base requirements for form completeion
 * @returns {boolean}- True if base requirements met
 */
const verifyBaseRequired = () => {
  let verified = 0;
  for (let x = 0; x < mappings.value.transactions.length; x++) {
    const transaction = mappings.value.transactions[x];
    if (
      transaction.transactionTypeID !== null &&
      transaction.transactionTypeID !== "" &&
      transaction.transactionStatusID !== null &&
      transaction.transactionStatusID !== "" &&
      transaction.description !== "" &&
      transaction.description !== null &&
      transaction.amount !== "" &&
      transaction.amount !== null &&
      transaction.sourceAccountID !== "" &&
      transaction.sourceAccountID !== null &&
      transaction.transactionDate !== null &&
      transaction.transactionDate !== ""
    ) {
      verified += 1;
    }
  }
  if (verified == mappings.value.transactions.length) {
    return true;
  } else {
    return false;
  }
};

/**
 * `verifyTagTotal` Verifies the total of tags equals total amount.
 * @returns - Returns True if totals match
 */
const verifyTagTotal = () => {
  let verified = 0;
  for (let x = 0; x < mappings.value.transactions.length; x++) {
    const transaction = mappings.value.transactions[x];
    let tagtotal = 0;
    if (transaction.tags) {
      transaction.tags.forEach(tag => {
        tagtotal += parseFloat(tag.tag_amount);
      });
    }
    if (tagtotal == transaction.amount) {
      verified += 1;
    }
  }
  if (verified == mappings.value.transactions.length) {
    return true;
  } else {
    return false;
  }
};

/**
 * `verifyTransactionType` Verifies destination_account filled if this is transfer
 * @returns {boolean}- True if transfer and destination_account filled out
 */
const verifyTransactionType = () => {
  let verified = 0;
  for (let x = 0; x < mappings.value.transactions.length; x++) {
    const transaction = mappings.value.transactions[x];
    if (transaction.transactionTypeID == 3) {
      if (
        transaction.destinationAccountID !== null &&
        transaction.destinationAccountID !== ""
      ) {
        verified += 1;
      }
    } else {
      return true;
    }
  }
  if (verified == mappings.value.transactions.length) {
    return true;
  } else {
    return false;
  }
};

/**
 * `updateTags` Updates tags if they are updated.
 */
const updateTags = data => {
  mappings.value.transactions[data.transID].tags = data.tags;
  verifyErrors(data.transID);
  updateStep6Complete();
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
      type_id: null,
    };
    let trans_status = {
      file_status: transaction.TransactionStatus,
      status_id: null,
    };
    let source_account = {
      file_account: transaction.SourceAccount,
      account_id: null,
    };
    let destination_account = {
      file_account: transaction.DestinationAccount,
      account_id: null,
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
    let all_tags = [];
    if (transaction.Tags) {
      all_tags = transaction.Tags.split(";").map(substring =>
        substring.split(":")[0].trim(),
      );
    }
    for (let n = 0; n < all_tags.length; n++) {
      let trans_tag = {
        file_tag: all_tags[n],
        tag_id: null,
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
};

/**
 * `submitForm` Submits the mapping data and file.
 */
const submitForm = () => {
  const file = fileToImport.value[0];
  uploadFile(mappings.value, file);
  closeDialog();
};

/**
 * `isValidDateFormat` Validates a provided string is a valid date.
 */
function isValidDateFormat(dateString) {
  // Define a regular expression to match the yyyy-mm-dd format
  const dateFormatRegex = /^\d{4}-\d{2}-\d{2}$/;

  // Check if the string matches the regular expression
  if (!dateFormatRegex.test(dateString)) {
    return false; // Date format doesn't match yyyy-mm-dd
  }

  // Check if the string represents a valid date using the Date object
  const dateObject = new Date(dateString);
  if (isNaN(dateObject.getTime())) {
    return false; // Invalid date
  }

  // Check if the parsed date matches the original input
  // This step is to handle edge cases such as "2021-02-30" which the Date object may accept
  const [year, month, day] = dateString.split("-").map(Number);
  const dateObjectTZ = new Date(year, month - 1, day);
  if (
    dateObjectTZ.getFullYear() !== year ||
    dateObjectTZ.getMonth() + 1 !== month ||
    dateObjectTZ.getDate() !== day
  ) {
    return false; // Date doesn't match original input
  }

  // If all checks passed, the string is in valid yyyy-mm-dd format and represents a valid date
  return true;
}

/**
 * `tagColor` Sets the tag color based on tag type.
 * @param {int} typeID - The tag type ID.
 * @return {color} - The color of the tag.
 */
const tagColor = typeID => {
  if (typeID == 1) {
    return "red";
  } else if (typeID == 2) {
    return "green";
  } else if (typeID == 3) {
    return "grey";
  }
};

/**
 * `isValidFloat` Validates a provided value is a valid float.
 */
function isValidFloat(value) {
  return !isNaN(parseFloat(value)) && isFinite(value);
}
</script>
