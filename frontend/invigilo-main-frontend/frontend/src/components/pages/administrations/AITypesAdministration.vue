<script setup lang="ts">
import { ref } from "vue";
import { CRUDModalProps } from "/@src/components/partials/crud/CRUDModal.vue";

const recordModalOpen = ref(false);
const recordModalOptions = ref<CRUDModalProps>({
  path: "ai/types/{id}",
  titleVar: "AI model",
});

const create = () => {
  recordModalOpen.value = true;
  delete recordModalOptions.value.crudId;
  delete recordModalOptions.value.remove;
};

const update = (row: any) => {
  recordModalOptions.value.crudId = row.id;
  recordModalOpen.value = true;
  delete recordModalOptions.value.remove;
};

const remove = (row: any) => {
  recordModalOptions.value.crudId = row.id;
  recordModalOptions.value.remove = true;
  recordModalOpen.value = true;
};

const modalClose = () => (recordModalOpen.value = false);
const updateTimestamp = ref(Date.now());
const updateTimestampFn = () => (updateTimestamp.value = Date.now());

const tableCrudOptions = {
  path: "/ai/types",
  columns: [
    { field: "index", label: "INDEX", type: "number", sortable: true, searchable: true },
    { field: "severity", label: "Severity", type: "number", sortable: true },
    { field: "name", label: "Name", sortable: true, searchable: true },
    { field: "description", label: "Description", sortable: true, searchable: true },
  ],
  actions: [
    {
      key: "create",
      global: true,
      action: create,
      label: "AI Model",
      icon: "carbon:add",
      buttonProps: {
        color: "primary",
        elevate: true,
      },
    },
    {
      key: "update",
      action: update,
      icon: "carbon:edit",
      buttonProps: {
        color: "primary",
        outlined: true,
      },
    },
    {
      key: "delete",
      action: remove,
      icon: "carbon:delete",
      buttonProps: {
        color: "danger",
        outlined: true,
      },
    },
  ],
};
</script>

<template>
  <CRUDTable v-bind="tableCrudOptions" :updateTimestamp="updateTimestamp" />

  <CRUDModal
    :open="recordModalOpen"
    v-bind="recordModalOptions"
    @close="modalClose"
    @save="updateTimestampFn"
  >
    <template v-slot:form="formProps">
      <VField label="Index">
        <VControl :has-error="formProps.errors.index">
          <input type="number" step="1" min="1" v-model="formProps.data.index" class="input" />
        </VControl>
      </VField>
      <VField label="Severity">
        <VControl :has-error="formProps.errors.severity">
          <input type="number" step="1" min="0" max="100" placeholder="50" v-model="formProps.data.severity" class="input" />
        </VControl>
      </VField>
      <VField label="Name">
        <VControl :has-error="formProps.errors.name">
          <input type="text" v-model="formProps.data.name" class="input" />
        </VControl>
      </VField>
      <VField label="Description">
        <VControl :has-error="formProps.errors.description">
          <textarea
            class="textarea"
            rows="4"
            v-model="formProps.data.description"
          ></textarea>
        </VControl>
      </VField>
    </template>
  </CRUDModal>
</template>
