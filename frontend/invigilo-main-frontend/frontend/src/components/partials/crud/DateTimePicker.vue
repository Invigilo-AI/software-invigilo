<script setup lang="ts">
import { computed } from "vue-demi";
import _cloneDeep from "lodash/cloneDeep";

export interface DateTimePickerEmits {
  (e: "update:modelValue", value: Record<string, string>): void;
}
export interface DateTimePickerProps {
  modelValue: any;
  placeholder?: string;
  is24hr?: boolean;
  isRange?: boolean;
  mode?: "date" | "dateTime" | "time";
  modelConfig?: any;
}
const emit = defineEmits<DateTimePickerEmits>();
const props = withDefaults(defineProps<DateTimePickerProps>(), {
  mode: "date",
  is24hr: true,
  isRange: false,
});
const withTime = computed(() => props.mode.toLowerCase().includes("time"));
const withDate = computed(() => props.mode.toLowerCase().includes("date"));
const _placeholder = computed(() => {
  const modeKey = `${props.mode.toLowerCase()}${props.isRange ? "-range" : ""}`;
  const modePlaceholder = {
    date: "Select date",
    "date-range": { start: "From date", end: "To date" },
    "datetime-range": { start: "From date & time", end: "To date & time" },
    datetime: "Select date & time",
    time: "Time",
    "time-range": { start: "From time", end: "To time" },
  }[modeKey];

  return props.placeholder || modePlaceholder;
});
const inputIcon = computed(() =>
  withTime.value ? "carbon:time" : "carbon:calendar"
);
const defaultValue = computed(
  () => (props.mode === "time" && new Date()) || props.modelValue
);
const _modeClass = computed(() =>
  withTime.value ? (withDate ? "date-time" : "time") : "date"
);
const _modelConfig = computed(() => {
  let modelConfig: any = {
    type: "number",
    mask: "YYYY-MM-DD",
  };
  if (props.modelConfig) {
    modelConfig = _cloneDeep(props.modelConfig);
  } else if (withTime.value) {
    modelConfig.mask = "iso";
    modelConfig.timeAdjust = "00:00:00";
  }

  return modelConfig;
});
// TODO: set default time on open
const logPopoverEvent = (event: any) => {
  console.log(event);
};
const updateModelValue = (event: any) =>
  emit("update:modelValue", isNaN(event) ? undefined : event);
</script>

<template>
  <VDatePicker
    v-model="modelValue"
    :value="defaultValue"
    @update:modelValue="updateModelValue"
    :mode="mode"
    :is24hr="is24hr"
    :isRange="isRange"
    color="green"
    trim-weeks
    :update-on-input="false"
    :popover="{ visibility: 'focus' }"
    :modelConfig="_modelConfig"
    :timezone="'UTC'"
    @popoverWillShow="logPopoverEvent('popoverWillShow')"
    @popoverDidShow="logPopoverEvent('popoverDidShow')"
    @popoverWillHide="logPopoverEvent('popoverWillHide')"
    @popoverDidHide="logPopoverEvent('popoverDidHide')"
  >
    <template #default="{ inputValue, inputEvents, togglePopover }">
      <VField addons>
        <VControl>
          <VIconButton :icon="inputIcon" outlined @click="togglePopover" />
        </VControl>

        <VControl v-if="isRange" :class="[_modeClass]">
          <input
            :placeholder="_placeholder.start"
            :value="inputValue.start"
            class="input"
            v-on="inputEvents.start"
          />
        </VControl>
        <VControl v-else :class="[_modeClass]">
          <input
            :placeholder="_placeholder"
            :value="inputValue"
            class="input"
            v-on="inputEvents"
          />
        </VControl>

        <VControl v-if="isRange">
          <VIconButton icon="carbon:arrow-right" @click="togglePopover" />
        </VControl>
        <VControl v-if="isRange" :class="[_modeClass]">
          <input
            :placeholder="_placeholder.end"
            :value="inputValue.end"
            class="input"
            v-on="inputEvents.end"
          />
        </VControl>
      </VField>
    </template>
  </VDatePicker>
</template>
