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

const displayAmount = ref("0");
const memoryAmount = ref(0);
const memoryText = ref("");
const runningTotal = ref(0);
const operand = ref(null);
const operationInProgress = ref(false);
const newEquation = ref(true);
const resetTriggeredByEquals = ref(false); // New flag

const clickUpdateAmount = () => {
  emit("updateDialog", false);
  emit("updateAmount", parseFloat(displayAmount.value));
};

const watchPassedAmount = () => {
  watchEffect(() => {
    if (props.amount) {
      resetCalculator();
      displayAmount.value = formatMoney(props.amount);
    }
  });
};

const resetCalculator = () => {
  displayAmount.value = "0";
  memoryAmount.value = 0;
  memoryText.value = "";
  runningTotal.value = 0;
  operand.value = null;
  operationInProgress.value = false;
  newEquation.value = true;
  resetTriggeredByEquals.value = false; // Reset the flag
};

const formatMoney = value => {
  // Format value to ensure two decimal places
  return parseFloat(value).toFixed(2);
};

const appendNumber = number => {
  if (newEquation.value) {
    if (resetTriggeredByEquals.value) {
      memoryText.value = ""; // Clear memory text only if '=' was pressed
    }
    displayAmount.value = String(number);
    newEquation.value = false;
    operationInProgress.value = false;
    resetTriggeredByEquals.value = false; // Reset the flag after use
  } else if (operationInProgress.value) {
    displayAmount.value = String(number);
    operationInProgress.value = false;
  } else {
    const [integerPart, fractionalPart] = displayAmount.value.split(".");
    if (!fractionalPart || fractionalPart.length < 2) {
      displayAmount.value =
        displayAmount.value === "0"
          ? String(number)
          : displayAmount.value + number;
    }
  }
};

const backspace = () => {
  displayAmount.value = displayAmount.value.slice(0, -1) || "0";
};

const appendPeriod = () => {
  if (!displayAmount.value.includes(".")) {
    displayAmount.value += ".";
  }
};

const clickClear = () => {
  resetCalculator();
};

const clickOperation = operation => {
  if (!operationInProgress.value) {
    performOperation();
  }
  operand.value = operation;
  memoryText.value = `${runningTotal.value} ${operation}`;
  operationInProgress.value = true;
  resetTriggeredByEquals.value = false; // Operation button doesn't trigger '=' behavior
};

const performOperation = () => {
  const currentValue = parseFloat(displayAmount.value);

  // Build equation string for memory text
  let equation = `${runningTotal.value} ${operand.value || ""} ${currentValue}`;

  if (!operand.value) {
    runningTotal.value = currentValue;
  } else {
    switch (operand.value) {
      case "+":
        runningTotal.value = runningTotal.value + currentValue;
        break;
      case "-":
        runningTotal.value = runningTotal.value - currentValue;
        break;
      case "*":
        runningTotal.value = runningTotal.value * currentValue;
        break;
      case "/":
        if (currentValue !== 0) {
          runningTotal.value = runningTotal.value / currentValue;
        } else {
          alert("Cannot divide by zero");
          resetCalculator();
          return;
        }
        break;
    }
  }

  // Fix JavaScript precision and format result
  runningTotal.value = parseFloat(runningTotal.value.toFixed(2));

  // Update display and memory text
  displayAmount.value = formatMoney(runningTotal.value);
  memoryText.value = `${equation} =`; // Show full equation
  operand.value = null;
  operationInProgress.value = false;
  newEquation.value = true;
  resetTriggeredByEquals.value = true; // '=' was pressed
};

onMounted(() => {
  watchPassedAmount();
});
</script>
