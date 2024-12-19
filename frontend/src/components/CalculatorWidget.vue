<template>
  <v-dialog v-model="dialog" width="400"
    ><v-card
      ><v-card-text
        ><v-container>
          <v-row dense
            ><v-col class="text-center" cols="10"
              ><v-text-field
                v-model="displayAmount"
                :label="memoryText"
                variant="solo"
                suffix="$"
                type="text"
                :reverse="true"
                color="grey"
                bg-color="grey"
              ></v-text-field></v-col
            ><v-col cols="2" class="text-right"
              ><v-btn
                icon="mdi-check-bold"
                rounded="xl"
                color="success"
                block
                size="x-small"
                @click="clickUpdateAmount"
              ></v-btn></v-col
          ></v-row>
          <v-row dense
            ><v-col class="text-center" cols="9"
              ><v-btn rounded="xl" block color="secondary" @click="clickClear"
                >CLEAR</v-btn
              ></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-division"
                color="secondary"
                @click="clickOperation('/')"
              ></v-btn></v-col></v-row
          ><v-row dense
            ><v-col class="text-left"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-7"
                @click="appendNumber(7)"
              ></v-btn></v-col
            ><v-col class="text-center"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-8"
                @click="appendNumber(8)"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-9"
                @click="appendNumber(9)"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-multiplication"
                color="secondary"
                @click="clickOperation('*')"
              ></v-btn></v-col
          ></v-row>
          <v-row dense
            ><v-col class="text-left"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-4"
                @click="appendNumber(4)"
              ></v-btn></v-col
            ><v-col class="text-center"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-5"
                @click="appendNumber(5)"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-6"
                @click="appendNumber(6)"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-minus"
                color="secondary"
                @click="clickOperation('-')"
              ></v-btn></v-col
          ></v-row>
          <v-row dense
            ><v-col class="text-left"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-1"
                @click="appendNumber(1)"
              ></v-btn></v-col
            ><v-col class="text-center"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-2"
                @click="appendNumber(2)"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-3"
                @click="appendNumber(3)"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-plus"
                color="secondary"
                @click="clickOperation('+')"
              ></v-btn></v-col
          ></v-row>
          <v-row dense
            ><v-col class="text-left"
              ><v-btn
                rounded="xl"
                icon="mdi-numeric-0"
                @click="appendNumber(0)"
              ></v-btn></v-col
            ><v-col class="text-center"
              ><v-btn
                rounded="xl"
                icon="mdi-circle-small"
                @click="appendPeriod"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-backspace"
                @click="backspace"
              ></v-btn></v-col
            ><v-col class="text-right"
              ><v-btn
                rounded="xl"
                icon="mdi-equal"
                color="accent"
                @click="performOperation"
              ></v-btn></v-col
          ></v-row> </v-container></v-card-text></v-card
  ></v-dialog>
</template>
<script setup>
import { ref, defineEmits, defineProps, onMounted, watchEffect } from "vue";

// Define emits
const emit = defineEmits(["updateDialog", "updateAmount"]);

const props = defineProps({
  amount: {
    type: Number,
    default: 0,
  },
});

const displayAmount = ref(0);
const memoryAmount = ref(0);
const memoryText = ref("");
const runningTotal = ref(0);
const operand = ref(null);
const operationInProgress = ref(false);
const newEquation = ref(true);

const clickUpdateAmount = () => {
  emit("updateDialog", false);
  emit("updateAmount", displayAmount.value);
};
const watchPassedAmount = () => {
  watchEffect(() => {
    if (props.amount) {
      displayAmount.value = Number(props.amount);
      memoryText.value = "";
      memoryAmount.value = 0;
      runningTotal.value = 0;
      operand.value = null;
      operationInProgress.value = false;
      newEquation.value = true;
    }
  });
};
const appendNumber = number => {
  if (!operationInProgress.value && !newEquation.value) {
    const valueString = String(displayAmount.value);

    // Check if there is a period in the value
    const hasPeriod = valueString.includes(".");

    if (!hasPeriod) {
      // No period exists, append the number
      displayAmount.value =
        displayAmount.value !== 0 ? `${displayAmount.value}${number}` : number;
    } else {
      // Check if there is at most one digit after the period
      const fractionalPart = valueString.split(".")[1];
      if (!fractionalPart || fractionalPart.length < 2) {
        // Append the number if there's no or only one digit after the period
        displayAmount.value = `${displayAmount.value}${number}`;
      }
    }
  } else {
    operationInProgress.value = false;
    displayAmount.value = `${number}`;
    if (newEquation.value) {
      memoryAmount.value = 0;
      memoryText.value = "";
      runningTotal.value = 0;
      operand.value = null;
    }
  }
};
const backspace = () => {
  displayAmount.value = String(displayAmount.value).slice(0, -1);
  if (!displayAmount.value) {
    displayAmount.value = 0;
  }
};
function appendPeriod() {
  if (!String(displayAmount.value).includes(".")) {
    displayAmount.value = `${displayAmount.value}.`;
  }
}
const clickClear = () => {
  memoryAmount.value = 0;
  memoryText.value = "";
  displayAmount.value = 0;
  runningTotal.value = 0;
  operand.value = null;
  operationInProgress.value = false;
  newEquation.value = true;
};
const clickOperation = operation => {
  performOperation();
  newEquation.value = false;
  operand.value = operation;
  operationInProgress.value = true;
  memoryText.value = `${runningTotal.value} ${operation}`;
};

const performOperation = () => {
  operationInProgress.value = false;
  let newTotal = 0;
  if (operand.value == "+") {
    newTotal = Number(runningTotal.value) + Number(displayAmount.value);
  }
  if (!operand.value) {
    newTotal = Number(displayAmount.value);
  }
  memoryText.value = `${runningTotal.value} + ${displayAmount.value} =`;
  displayAmount.value = `${newTotal}`;
  newEquation.value = true;
  runningTotal.value = newTotal;
  operand.value = null;
};
onMounted(() => {
  // Perform actions on mount
  watchPassedAmount();
});
</script>
