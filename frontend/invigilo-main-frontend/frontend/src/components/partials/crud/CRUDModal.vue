<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useApi } from "/@src/composable/useApi";
import { useNotyf } from "/@src/composable/useNotyf";
import _cloneDeep from "lodash/cloneDeep";
import _cloneDeepWith from "lodash/cloneDeepWith";

export interface CRUDModalEmits {
  (e: "close"): void;
  (e: "save"): void;
}
export type PathMethod = "get" | "post" | "put" | "delete";
export type Path =
  | string
  | {
      get?: string;
      post?: string;
      put?: string;
      delete?: string;
    };
type JSONValue =
  | null
  | string
  | number
  | boolean
  | { [x: string]: JSONValue }
  | JSONValue[];

export type JSONObject = { [x: string]: JSONValue };

export interface CRUDModalProps {
  open?: boolean;
  path: string | Path;
  crudId?: string | number;
  title?: string;
  titleVar?: string;
  remove?: boolean;
  size?: "small" | "medium" | "large" | "big";
  data?: object;
  // transform?: (data: JSONObject) => JSONObject;
  transform?: (data: any) => any;
  transformOnSave?: (data: any) => any;
}
const emit = defineEmits<CRUDModalEmits>();
const props = withDefaults(defineProps<CRUDModalProps>(), {
  size: "medium",
  remove: false,
  transform: (data) => _cloneDeep(data || {}),
  transformOnSave: (data) => _cloneDeep(data || {}),
});

const modalTitle = computed(
  () =>
    props.title ||
    (props.titleVar &&
      (props.crudId
        ? props.remove
          ? `Delete ${props.titleVar}`
          : `Update ${props.titleVar}`
        : `Create ${props.titleVar}`))
);

const crudId = ref<undefined | null | string | number>(null);
const formData = ref({ ...props.data });
const formLoading = ref(false);
const formErrors = ref<any>({});
const formFieldErrors = computed(() => ({
  ..._cloneDeepWith(
    formErrors.value.fields || {},
    (value) => (typeof value === "string" && Boolean(value)) || undefined
  ),
}));

const crudMethod = computed(() =>
  props.crudId ? (props.remove ? "delete" : "put") : "post"
);

const getPath = (method: PathMethod = "get") => {
  let path: string | undefined = "";
  const methods = Object.keys(props.path).map((el) => el.toLowerCase());
  if (typeof props.path === "string") {
    path = props.path;
  } else if (methods.includes(method)) {
    path = props.path[method];
  } else if (methods.length) {
    path = props.path["put"];
  }
  // @ts-ignore
  return path.replace(
    /(\{(?:crud)?-?id\})/gi,
    String((crudId.value !== null && crudId.value) || "")
  );
};

watch(
  () => props.open,
  () => {
    crudId.value = props.crudId;

    if (!props.open) {
      // delay before reset, wait for hide animation
      setTimeout(() => {
        crudId.value = null;
        formLoading.value = false;
        formData.value = _cloneDeep(props.data || {});
        formErrors.value = {};
      }, 500);
    }
  }
);

watch(
  () => crudId.value,
  async () => {
    if (crudId.value && !props.remove) {
      formLoading.value = true;
      const data = await getCrudId();
      if (data !== null) {
        formData.value = props.transform(data);
      } else {
        close();
      }
      formLoading.value = false;
    }
  }
);

const api = useApi();
const getCrudId = async () =>
  await api
    .get(getPath())
    .then((response) => {
      return response.data;
    })
    .catch(({ error = {} }) => {
      const { fields = {}, detail = null } = error;
      formErrors.value = {
        fields,
        detail,
      };

      if (typeof detail === "string") {
        notif.error(detail);
      }
      return null;
    });

const putCrudId = async (data: object) => await api.put(getPath("put"), data);

const postCrud = async (data: object) =>
  await api.post(getPath(crudMethod.value), data);

const deleteCrud = async () => await api.delete(getPath(crudMethod.value));

const notif = useNotyf();

const save = async () => {
  formLoading.value = true;
  let apiSave = null;
  const data = props.transformOnSave(formData.value);

  if (!crudId.value) {
    apiSave = postCrud(data);
  } else if (!props.remove) {
    apiSave = putCrudId(data);
  } else {
    apiSave = deleteCrud();
  }
  await apiSave
    .then(({ data }) => {
      formData.value = data;
      emit("save");
      close();
    })
    .catch(({ error = {} }) => {
      const { fields = {}, detail = null } = error;
      formErrors.value = {
        fields,
        detail,
      };

      if (typeof detail === "string") {
        notif.error(detail);
      }
    });

  formLoading.value = false;
};

const close = () => {
  emit("close");
};
</script>
<template>
  <VModal
    :open="open"
    :title="modalTitle"
    :size="remove ? 'small' : size"
    actions="right"
    :noclose="!remove"
    noscroll
    @close="close"
  >
    <template #content>
      <div v-if="remove">
        <strong>Are you sure?</strong> This action is irreversible.
      </div>
      <VLoader size="large" :active="formLoading" translucent v-else>
        <form @submit.prevent="save">
          <slot name="form" :data="formData" :errors="formFieldErrors"></slot>
        </form>
      </VLoader>
    </template>
    <template #action>
      <VButton
        v-if="remove"
        color="danger"
        raised
        :loading="formLoading"
        @click="save"
        >Delete</VButton
      >
      <VButton
        v-else
        color="primary"
        raised
        :loading="formLoading"
        @click="save"
        >Save</VButton
      >
    </template>
  </VModal>
</template>

<style lang="scss">
.v-modal {
  .is-horizontal {
    column-gap: 20px;
    & > * {
      flex: 1 1 0;
    }
  }
  .collapse {
    margin-bottom: 0.75rem;
    .collapse-header {
      height: 38px;
      padding: 0 10px;
    }
    .collapse-content {
      padding: 0 10px;
    }
  }

  .form-section {
    background: var(--smoke-white-dark-2);
    border-top: 1px solid var(--smoke-white-dark-10);
    margin: 0 -20px;
    padding: 20px 20px 10px;
    &:last-of-type {
      border-bottom: 1px solid var(--smoke-white-dark-10);
      margin-bottom: 20px;
    }

    .field:last-child {
      margin-bottom: 0.75rem;
    }

    .is-dark & {
      background: var(--dark-sidebar-light-4);
      border-top-color: var(--dark-sidebar-light-12);
      &:last-of-type {
        border-bottom-color: var(--dark-sidebar-light-12);
      }
    }
  }
}
</style>
