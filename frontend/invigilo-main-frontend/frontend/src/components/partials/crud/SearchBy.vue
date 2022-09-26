<script setup lang="ts">
import { useDebounceFn } from "@vueuse/core";
import { ref, watch } from "vue";
import { computed } from "vue-demi";

export interface SearchByEmits {
  (e: "update:modelValue", value: Record<string, string>): void;
}
export interface SearchByProps {
  options?: string | Record<string, string>;
  modelValue: any;
  placeholder?: string;
}
const emit = defineEmits<SearchByEmits>();
const props = withDefaults(defineProps<SearchByProps>(), {
  placeholder: "Search...",
});

const options = computed(() => {
  if (typeof props.options === 'string') {
    return [{value: props.options, label: 'Search'}]
  } else if (typeof props.options === 'object') {
    const options = props.options

    return Object.keys(props.options).map((key) => ({
        value: key,
        label: (options[key]) || key,
      }))
  } else {
    return []
  }
});

const searchInput = ref<HTMLInputElement | null>(null);
const search = ref<string>("");
const searchBy = ref<string>(
  options.value.length ? options.value[0].value : ""
);

watch(
  () => searchBy.value,
  () => {
    search.value = props.modelValue[searchBy.value] || "";
    if (searchInput.value) searchInput.value.focus();
  }
);

watch(
  () => search.value,
  () => {
    updateModelValue();
  }
);
const updateModelValue = useDebounceFn(() => {
  const modelValue = { ...props.modelValue };
  const searchText = search.value.trim();
  if (!searchText) {
    delete modelValue[searchBy.value];
  } else {
    modelValue[searchBy.value] = searchText;
  }

  emit("update:modelValue", modelValue);
}, 300);
</script>

<template>
  <VField addons>
    <VControl expanded icon="carbon:search">
      <input
        ref="searchInput"
        v-model="search"
        class="input custom-text-filter"
        :placeholder="props.placeholder"
      />
    </VControl>
    <VControl v-if="options.length > 1">
      <span class="select">
        <select v-model="searchBy">
          <option
            :value="value"
            :key="value"
            v-for="{ value, label } in options"
          >
            {{ label }} <template v-if="props.modelValue[value]"> ✓</template>
          </option>
        </select>
      </span>
    </VControl>
  </VField>
</template>

<style lang="scss">
.control.has-icon .form-icon {
  z-index: 5;
}
</style>
