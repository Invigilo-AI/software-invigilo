<script setup lang="ts">
import { onMounted, ref } from "vue";
import { CRUDModalProps } from "/@src/components/partials/crud/CRUDModal.vue";
import { v4 as uuid } from "uuid";
import _get from "lodash/get";
import _omit from "lodash/omit";
import { useApi } from "/@src/composable/useApi";

type AI_Vertex = {
  unique_id: string;
  id?: number;
  name?: string;
  description?: string;
  source?: (string | number)[];
  destination?: (string | number)[];
};

type AI_Edge = {
  id: number;
  source_id?: number;
  destination_id?: number;
};

type FormProps = {
  data: { vertexes: AI_Vertex[]; edges?: AI_Edge[] };
  errors: { vertexes: string | undefined };
};

const omitFields = ["created_at", "updated_at"];
const omitFieldsOnSave = [...omitFields, "edges", "company"];
const recordModalOpen = ref(false);
const recordModalOptions = ref<CRUDModalProps>({
  path: {
    get: "/ai/sequences/{id}/extra",
    put: "/ai/sequences/{id}",
    post: "/ai/sequences",
  },
  titleVar: "AI sequence",
  data: {
    vertexes: [],
  },
  // set the initial `sources` and `destination`, filter duplicated edges
  transform: ({
    vertexes = [] as AI_Vertex[],
    edges = [] as AI_Edge[],
    ...data
  }) => ({
    ..._omit(data, omitFields),
    vertexes: vertexes.map((vertex: AI_Vertex) => {
      if (!vertex.source && edges) {
        const sources = edges
          .filter((edge: AI_Edge) => edge.destination_id === vertex.id)
          .map((edge: AI_Edge) => edge.source_id || "");
        vertex.source = Array.from(new Set(sources));
      }
      if (!vertex.destination && edges) {
        const destinations = edges
          .filter((edge: AI_Edge) => edge.source_id === vertex.id)
          .map((edge: AI_Edge) => edge.destination_id || "");
        if (!destinations.length) destinations.push("");
        vertex.destination = Array.from(new Set(destinations));
      }
      return {
        ..._omit(vertex, omitFields),
        unique_id: vertex.unique_id || vertex.id,
      };
    }),
  }),
  transformOnSave: (data) => ({ ..._omit(data, omitFieldsOnSave) }),
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

const aiTypeOptions = ref([]);
const api = useApi();
const getAiTypeOptions = async () => {
  api
    .get("ai/types/index")
    .then((response) => {
      aiTypeOptions.value = response.data.map(
        // @ts-ignore
        ({ index: value, name: label }) => ({ value, label })
      );
    })
    .catch(() => {
      aiTypeOptions.value = [];
    });
};

onMounted(() => {
  getAiTypeOptions();
});

const tableCrudOptions = {
  path: "/ai/sequences/extra",
  columns: [
    { field: "id", label: "ID", type: "number", sortable: true, searchable: true },
    { field: "name", label: "Name", sortable: true, searchable: true },
    { field: "description", label: "Description", sortable: true, searchable: true },
    { field: "company.name", label: "Company", sortable: 'company__name', searchable: 'company__name' },
  ],
  actions: [
    {
      key: "create",
      global: true,
      action: create,
      label: "AI Sequence",
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

const addVertex = (formProps: FormProps) => {
  formProps.data.vertexes.push({
    unique_id: uuid(),
    source: [""],
    destination: [""],
  });
};

const removeVertex = (formProps: FormProps, unique_id: string) => {
  const vertexes = formProps.data.vertexes;
  const vertex = vertexes.find((itm: AI_Vertex) => itm.unique_id === unique_id);
  // remove used `source/destination` for deleting vertex
  if (vertex) {
    vertexes.forEach((item) => {
      item.source = item.source?.filter((id) => id != vertex.unique_id);
      item.destination = item.destination?.filter(
        (id) => id != vertex.unique_id
      );
      if (!item.source?.length) item.source = ['']
      if (!item.destination?.length) item.destination = ['']
    });
    const index = vertexes.indexOf(vertex);
    vertexes.splice(index, 1);
  }
};

// TODO: edit use `edges` in combination with `vertexes`
// TODO: on edit to be possible to set edge as sequence source if it has another links
// to achieve that atm. remove all sources to add sequence entry
const vertexLinks = (formProps: FormProps, idx: number, field: string) => {
  const vertexes = formProps.data.vertexes;
  const unique_id = formProps.data.vertexes[idx].unique_id;
  let links: AI_Vertex[] = [];
  const inSources: AI_Vertex[] = [];
  const inDestinations: AI_Vertex[] = [];
  const inNone: AI_Vertex[] = [];

  vertexes.forEach((vertex, idx) => {
    const optionVertex = {...vertex}
    if (!vertex.name) {
      optionVertex.name = `Vertex (${idx + 1})`
    }
    if (vertex.source && vertex.source.includes(unique_id)) {
      inSources.push(optionVertex);
    }
    if (vertex.destination && vertex.destination.includes(unique_id)) {
      inDestinations.push(optionVertex);
    }
    if (
      !((vertex.unique_id || vertex.id) === unique_id) &&
      !(vertex.source && vertex.source.includes(unique_id)) &&
      !(vertex.destination && vertex.destination.includes(unique_id))
    ) {
      inNone.push(optionVertex);
    }
  });

  if (field === "source") {
    links = [
      { unique_id: "", name: "📥 Sequence input" },
      ...new Set([...inNone, ...inDestinations]),
    ];
  } else {
    links = [
      { unique_id: "", name: "📤 Sequence output" },
      ...new Set([...inNone, ...inSources]),
    ];
  }

  return links.map((vertex) => ({
    value: vertex.unique_id,
    label: vertex.name,
  }));
};
const vertexData = (formProps: FormProps, idx: number) =>
  formProps.data.vertexes[idx];
const vertexError = (formProps: FormProps, idx: number, field: string) =>
  Boolean(_get(formProps.errors, `vertexes.${idx}.${field}`, false));
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
        <VControl :has-error="Boolean(formProps.errors.company_id)">
          <QueryMultiSelect
            path="/companies"
            query-key="name"
            v-model="formProps.data.company_id"
          />
        </VControl>
      </VField>
      <VField label="Name">
        <VControl :has-error="Boolean(formProps.errors.name)">
          <input type="text" v-model="formProps.data.name" class="input" />
        </VControl>
      </VField>
      <VField label="Description">
        <VControl :has-error="Boolean(formProps.errors.description)">
          <textarea
            class="textarea"
            rows="2"
            v-model="formProps.data.description"
          ></textarea>
        </VControl>
      </VField>
      <br />
      <div
        class="form-section"
        :key="vertex.unique_id"
        v-for="(vertex, idx) in formProps.data.vertexes"
      >
        <VButton
          icon="carbon:misuse-outline"
          color="danger"
          fullwidth
          bold
          outlined
          @click="removeVertex(formProps, vertex.unique_id)"
          >Remove ({{idx + 1}})</VButton
        >
        <br />
        <VField horizontal>
          <VField :label="`Vertex name`">
            <VControl :has-error="vertexError(formProps, idx, 'name')">
              <input
                type="text"
                v-model="vertexData(formProps, idx).name"
                class="input"
              />
            </VControl>
          </VField>
          <VField label="AI Server">
            <VControl :has-error="vertexError(formProps, idx, 'server_id')">
              <QueryMultiSelect
                path="/ai/servers"
                query-key="name"
                v-model="vertexData(formProps, idx).server_id"
              />
            </VControl>
          </VField>
        </VField>
        <VField label="Models">
          <VControl :has-error="vertexError(formProps, idx, 'types')">
            <Multiselect
              v-model="vertexData(formProps, idx).types"
              mode="tags"
              :options="aiTypeOptions"
            />
          </VControl>
        </VField>
        <VField label="Description">
          <VControl :has-error="vertexError(formProps, idx, 'description')">
            <textarea
              class="textarea"
              rows="1"
              v-model="vertexData(formProps, idx).description"
            ></textarea>
          </VControl>
        </VField>
        <VField horizontal>
          <VField label="Source">
            <VControl :has-error="vertexError(formProps, idx, 'source')">
              <Multiselect
                v-model="vertexData(formProps, idx).source"
                mode="tags"
                placeholder="Sequence input"
                :options="vertexLinks(formProps, idx, 'source')"
              />
            </VControl>
          </VField>
          <VField label="Destination">
            <VControl :has-error="vertexError(formProps, idx, 'destination')">
              <Multiselect
                v-model="vertexData(formProps, idx).destination"
                mode="tags"
                placeholder="Sequence output"
                :options="vertexLinks(formProps, idx, 'destination')"
              />
            </VControl>
          </VField>
        </VField>
      </div>
      <VButton
        icon="carbon:add-alt"
        color="success"
        fullwidth
        bold
        outlined
        @click="addVertex(formProps)"
        >New vertex</VButton
      >
    </template>
  </CRUDModal>
</template>
