<script setup lang="ts">
import { ref } from "vue";
import { CRUDModalProps } from "/@src/components/partials/crud/CRUDModal.vue";

const recordModalOpen = ref(false);
const recordModalOptions = ref<CRUDModalProps>({
  path: "/companies/{id}",
  titleVar: "company",
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
  path: "/companies/",
  columns: [
    {
      field: "id",
      label: "ID",
      type: "number",
      sortable: true,
      searchable: true,
    },
    { field: "name", label: "Name", sortable: true, searchable: true },
    { field: "description", label: "Description", searchable: true },
  ],
  actions: [
    {
      key: "create",
      global: true,
      action: create,
      label: "Company",
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
      <VField label="Logo">
        <VControl :has-error="formProps.errors.logo">
          <FileUpload v-model="formProps.data.logo" />
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
