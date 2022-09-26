<script setup lang="ts">
import { ref } from "vue";
import { CRUDModalProps } from "/@src/components/partials/crud/CRUDModal.vue";

const recordModalOpen = ref(false);
const recordModalOptions = ref<CRUDModalProps>({
  path: "/servers/{id}",
  titleVar: "server",
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
  path: "/servers/extra",
  columns: [
    {
      field: "id",
      label: "ID",
      type: "number",
      sortable: true,
      searchable: true,
    },
    { field: "name", label: "Name", sortable: true, searchable: true },
    { field: "location", label: "location", sortable: true, searchable: true },
    {
      field: "company.name",
      label: "Company",
      sortable: "company__name",
      searchable: "company__name",
    },
    { field: "is_active", label: "Active", type: "boolean", sortable: true },
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
      <VField label="Company">
        <VControl :has-error="formProps.errors.company_id">
          <QueryMultiSelect
            path="/companies"
            query-key="name"
            v-model="formProps.data.company_id"
          />
        </VControl>
      </VField>
      <VField label="Name">
        <VControl :has-error="formProps.errors.name">
          <input type="text" v-model="formProps.data.name" class="input" />
        </VControl>
      </VField>
      <VField label="Location">
        <VControl :has-error="formProps.errors.location">
          <input type="text" v-model="formProps.data.location" class="input" />
        </VControl>
      </VField>
      <VField label="Connection">
        <VControl :has-error="formProps.errors.connection">
          <input
            type="text"
            v-model="formProps.data.connection"
            class="input"
          />
        </VControl>
      </VField>
      <VField label="Access token">
        <VControl :has-error="formProps.errors.access_token">
          <input
            type="text"
            v-model="formProps.data.access_token"
            class="input"
          />
        </VControl>
      </VField>
      <VField>
        <VControl>
          <VSwitchBlock
            color="primary"
            label="Active"
            v-model="formProps.data.is_active"
          />
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
