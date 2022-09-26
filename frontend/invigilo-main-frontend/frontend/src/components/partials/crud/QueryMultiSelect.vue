<script setup lang="ts">
import { useDebounceFn } from "@vueuse/core";
import { ref, watch, onMounted } from "vue";
import { useApi } from "/@src/composable/useApi";

export type QueryMultiSelectValue = string | number | (string | number)[];
export interface QueryMultiSelectEmits {
  (e: "update:modelValue", value: QueryMultiSelectValue): void;
  (e: "change", value: any): void;
}
export interface QueryMultiSelectProps {
  path: string;
  limit?: number;
  modelValue?: QueryMultiSelectValue;
  placeholder?: string;
  formatOption?: Function;
  searchable?: boolean;
  mode?: "single" | "multiple" | "tags";
  valueKey?: string;
  labelKey?: string;
  queryKey?: string;
  params?: Record<string, any>;
}
export interface MultiSelectOption {
  value: any;
  label: string;
}
const emit = defineEmits<QueryMultiSelectEmits>();
const props = withDefaults(defineProps<QueryMultiSelectProps>(), {
  limit: 5,
  searchable: true,
  mode: "single",
  valueKey: "id",
  labelKey: "name",
  queryKey: "query",
});

const formatOption =
  props.formatOption ||
  ((option: any) => ({
    value: option[props.valueKey],
    label: option[props.labelKey],
  }));

const searchChange = async (query: string) => {
  multiselectProps.value.loading = true;
  queryFn(query);
};

const onOpen = () => {
  if (!multiselectProps.value.options.length || props.searchable) {
    getOptions();
  }
};

const multiselectProps = ref<{
  [key: string]: any;
  options: MultiSelectOption[];
}>({
  mode: props.mode,
  loading: false,
  searchable: props.searchable,
  hideSelected: props.mode !== "multiple",
  internalSearch: false,
  clearOnSelect: true,
  closeOnSelect: props.mode !== "multiple",
  showNoResults: false,
  limit: props.limit,
  placeholder: props.placeholder,
  options: [],
});

const multiselectEvents = ref({
  searchChange: (props.searchable && searchChange) || undefined,
  open: onOpen,
});

const withValueOption = () => {
  if (
    props.modelValue &&
    !multiselectProps.value.options.find(
      (option: MultiSelectOption) => option.value === props.modelValue
    )
  ) {
    if (Array.isArray(props.modelValue)) {
      for (const value of props.modelValue) {
        getCurrentOption(value);
      }
    } else {
      getCurrentOption(props.modelValue);
    }
  }
};

watch(() => props.modelValue, withValueOption);

onMounted(() => {
  withValueOption();
});

const selectOptionsData = ref<any[]>([]);
const api = useApi();
const getCurrentOption = (id: string | number) => {
  if (!props.path || !id) return;

  if (multiselectProps.value.options.find(({ value }) => value === id)) return;

  multiselectProps.value.loading = true;
  api
    .get(`${props.path}/${id}`)
    .then((response) => {
      multiselectProps.value.options = [formatOption(response.data)];
      selectOptionsData.value = [response.data];
    })
    .catch(() => {
      multiselectProps.value.options = [];
      selectOptionsData.value = [];
    });
  multiselectProps.value.loading = false;
};
const getOptions = async (query?: string) => {
  if (!props.path) return;

  multiselectProps.value.loading = true;
  await api
    .get(props.path, {
      params: {
        ...props.params,
        [props.queryKey]: query,
      },
    })
    .then((response) => {
      multiselectProps.value.options = response.data.map(formatOption);
      selectOptionsData.value = response.data;
    })
    .catch(() => {
      multiselectProps.value.options = [];
      selectOptionsData.value = [];
    });
  multiselectProps.value.loading = false;
};
const queryFn = useDebounceFn(getOptions, 300);
const updateModelValue = (event: QueryMultiSelectValue) => {
  const selectData = selectOptionsData.value.find(
    (option) => formatOption(option).value === event
  );
  emit("update:modelValue", event);
  emit("change", selectData);
};
</script>
<template>
  <Multiselect
    :modelValue="modelValue"
    @update:modelValue="updateModelValue"
    v-bind="multiselectProps"
    v-on="multiselectEvents"
  >
    <template v-slot:option="props">
      <slot :props="props" :option="props.option"></slot>
    </template>
  </Multiselect>
</template>
