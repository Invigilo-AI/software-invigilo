<script setup lang="ts">
import { ref } from "vue";
import { CRUDModalProps } from "/@src/components/partials/crud/CRUDModal.vue";

const recordModalOpen = ref(false);
const recordModalOptions = ref<CRUDModalProps>({
  path: "/users/{id}",
  titleVar: "user",
});

const userPermissions = [
  {value: 'admin', label: 'Admin'},
  {value: 'inspector', label: 'Safety Inspector'},
  // {value: 'bridge', label: 'Bridge'},
]

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
  path: "/users/",
  columns: [
    { field: "id", label: "ID", type: "number", sortable: true, searchable: true },
    { field: "full_name", label: "Full name", sortable: true, searchable: true },
    { field: "email", label: "Email", sortable: true, searchable: true },
    { field: "permissions", label: "Permission" },
    { field: "is_active", label: "Active", type: "boolean", sortable: true },
  ],
  actions: [
    {
      key: "create",
      global: true,
      action: create,
      label: "User",
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
      <VField label="Full name">
        <VControl :has-error="formProps.errors.full_name">
          <input type="text" v-model="formProps.data.full_name" class="input" />
        </VControl>
      </VField>
      <VField label="Email">
        <VControl :has-error="formProps.errors.email">
          <input type="text" v-model="formProps.data.email" class="input" />
        </VControl>
      </VField>
      <VField label="Password">
        <VControl :has-error="formProps.errors.password">
          <input
            type="password"
            v-model="formProps.data.password"
            class="input"
          />
        </VControl>
      </VField>
      <VField label="Permissions">
        <VControl :has-error="formProps.errors.permissions">
          <Multiselect
              v-model="formProps.data.permissions"
              mode="tags"
              placeholder="Access permissions"
              :options="userPermissions"
            />
        </VControl>
      </VField>
      <VField horizontal>
        <VControl>
          <VSwitchBlock
            color="primary"
            label="Active"
            v-model="formProps.data.is_active"
          />
        </VControl>
      </VField>
    </template>
  </CRUDModal>
</template>
