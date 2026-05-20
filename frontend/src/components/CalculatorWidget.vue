<template>
  <v-dialog :model-value="modelValue" @update:model-value="emit('update:modelValue', $event); emit('updateDialog', $event)" width="300">
    <v-card color="secondary" variant="elevated" border="md" rounded="lg">
      <v-card-text>
        <v-container>
          <v-row dense>
            <v-col
              class="text-center rounded-md ma-0 pa-0 ga-0"
              cols="10"
              style="background-color: grey; padding: 16px; border-radius: 12px"
            >
              <span class="text-caption text-grey-lighten-2 font-italic">
                {{ memoryText }}
              </span>
              <br />
              <span class="font-weight-bold text-white text-body-1">
                ${{ displayAmount }}
              </span>
            </v-col>
            <v-col
              cols="2"
              class="d-flex justify-end align-center"
              style="align-items: center"
            >
              <v-tooltip text="Send Amount to Form" location="top">
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-check-bold"
                    rounded="xl"
                    color="success"
                    block
                    size="x-small"
                    @click="clickUpdateAmount"
                    v-bind="props"
                  ></v-btn>
                </template>
              </v-tooltip>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col class="text-center" cols="9">
              <v-btn rounded="xl" block color="primary" @click="clickClear">
                CLEAR
              </v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-division"
                color="primary"
                @click="clickOperation('/')"
              ></v-btn>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col class="text-left">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-7"
                @click="appendNumber(7)"
              ></v-btn>
            </v-col>
            <v-col class="text-center">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-8"
                @click="appendNumber(8)"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-9"
                @click="appendNumber(9)"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-multiplication"
                color="primary"
                @click="clickOperation('*')"
              ></v-btn>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col class="text-left">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-4"
                @click="appendNumber(4)"
              ></v-btn>
            </v-col>
            <v-col class="text-center">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-5"
                @click="appendNumber(5)"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-6"
                @click="appendNumber(6)"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-minus"
                color="primary"
                @click="clickOperation('-')"
              ></v-btn>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col class="text-left">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-1"
                @click="appendNumber(1)"
              ></v-btn>
            </v-col>
            <v-col class="text-center">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-2"
                @click="appendNumber(2)"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-3"
                @click="appendNumber(3)"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-plus"
                color="primary"
                @click="clickOperation('+')"
              ></v-btn>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col class="text-left">
              <v-btn
                rounded="xl"
                icon="mdi-numeric-0"
                @click="appendNumber(0)"
              ></v-btn>
            </v-col>
            <v-col class="text-center">
              <v-btn
                rounded="xl"
                icon="mdi-circle-small"
                @click="appendPeriod"
                color="grey"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-backspace"
                @click="backspace"
                color="grey"
              ></v-btn>
            </v-col>
            <v-col class="text-right">
              <v-btn
                rounded="xl"
                icon="mdi-equal"
                color="accent"
                @click="performOperation"
              ></v-btn>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script setup>
  import { ref, defineEmits, defineProps, onMounted, watchEffect, watch } from "vue";

  const emit = defineEmits(["updateDialog", "updateAmount"]);

  const props = defineProps({
    modelValue: {
      type: Boolean,
      default: false,
    },
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
  const resetTriggeredByEquals = ref(false);

  const clickUpdateAmount = () => {
    emit("updateDialog", false);
    emit("update:modelValue", false);
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
    resetTriggeredByEquals.value = false;
  };

  const formatMoney = value => {
    return parseFloat(value).toFixed(2);
  };

  const appendNumber = number => {
    if (newEquation.value) {
      if (resetTriggeredByEquals.value) {
        memoryText.value = "";
      }
      displayAmount.value = String(number);
      newEquation.value = false;
      operationInProgress.value = false;
      resetTriggeredByEquals.value = false;
    } else if (operationInProgress.value) {
      displayAmount.value = String(number);
      operationInProgress.value = false;
    } else {
      const [, fractionalPart] = displayAmount.value.split(".");
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
    memoryText.value = `$${runningTotal.value} ${operation}`;
    operationInProgress.value = true;
    resetTriggeredByEquals.value = false;
  };

  const performOperation = () => {
    const currentValue = parseFloat(displayAmount.value);

    let equation = `$${runningTotal.value} ${
      operand.value || ""
    } $${currentValue}`;

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

    runningTotal.value = parseFloat(runningTotal.value.toFixed(2));
    displayAmount.value = formatMoney(runningTotal.value);
    memoryText.value = `${equation} =`;
    operand.value = null;
    operationInProgress.value = false;
    newEquation.value = true;
    resetTriggeredByEquals.value = true;
  };

  const handleKeydown = event => {
    if (!props.modelValue) return;

    const key = event.key;

    if (key >= "0" && key <= "9") {
      event.preventDefault();
      appendNumber(parseInt(key));
    } else if (key === ".") {
      event.preventDefault();
      appendPeriod();
    } else if (key === "+") {
      event.preventDefault();
      clickOperation("+");
    } else if (key === "-") {
      event.preventDefault();
      clickOperation("-");
    } else if (key === "*") {
      event.preventDefault();
      clickOperation("*");
    } else if (key === "/") {
      event.preventDefault();
      clickOperation("/");
    } else if (key === "Enter" || key === "=") {
      event.preventDefault();
      performOperation();
    } else if (key === "Backspace") {
      event.preventDefault();
      backspace();
    } else if (key === "Delete" || key === "Escape") {
      event.preventDefault();
      clickClear();
    }
  };

  watch(
    () => props.modelValue,
    open => {
      if (open) {
        document.addEventListener("keydown", handleKeydown);
      } else {
        document.removeEventListener("keydown", handleKeydown);
      }
    },
  );

  onMounted(() => {
    watchPassedAmount();
  });
</script>
