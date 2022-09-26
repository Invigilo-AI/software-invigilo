<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { CRUDModalProps } from "/@src/components/partials/crud/CRUDModal.vue";
import { useApi } from "/@src/composable/useApi";
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import utc from "dayjs/plugin/utc";
import relativeTime from "dayjs/plugin/relativeTime";
import { useNotyf } from "/@src/composable/useNotyf";
import { useUserSession } from "/@src/stores/userSession";
import _get from 'lodash/get'

dayjs.extend(duration);
dayjs.extend(utc);
dayjs.extend(relativeTime);

export type Incident = {
  created_at: string;
  id: number;
  uuid: string;
  type: number[];
  camera_id: number;
  camera?: any;
  ai_mapping: number;
  location: string;
  acknowledged: boolean;
  inaccurate: boolean;
  frame: string;
  video: string;
  count: number;
  people: number;
  objects: number;
  meta: string;
  extra: string;
};

const api = useApi();
const notyf = useNotyf();

const userSession = useUserSession();
const { viewAsCompany, isSuperuser } = userSession;

const asCompany = computed(
  () => (userSession.isSuperuser && userSession.viewAsCompany) || undefined
);

const recordModalOpen = ref(false);
const recordModalOptions = ref<CRUDModalProps>({
  path: "/incidents/{id}",
  titleVar: "incident",
});

const view = (row: any) => {
  recordModalOptions.value.crudId = row.id;
  recordModalOpen.value = true;
  delete recordModalOptions.value.remove;
};

const download = async (data: any, action: any) => {
  let params: any = {
    company_id: asCompany.value,
  };
  const period = reportType.value;
  if (period === "custom") {
    params = {
      ...params,
      ...data,
      period,
    };
  } else {
    params = {
      ...params,
      created_at_from: data.created_at_from,
      period,
    };
  }

  return await api
    .get("reports/pdf", {
      params,
      responseType: "arraybuffer",
    })
    .then((response) => {
      console.log("download pdf", response);
      return {
        ...action,
        icon: "carbon:document-pdf", // TODO: fix update icon
        label: "Download",
        action: () => {
          console.log("download file and return old action", action);

          var contentDisposition = response.request.getResponseHeader(
            "content-disposition"
          );
          var contentType = response.request.getResponseHeader("content-type");
          var filename = contentDisposition.match(/filename="(.+)"/)[1];

          var file = new Blob([response.request.response], {
            type: contentType || "application/pdf",
          });
          // For Internet Explorer and Edge
          if ("msSaveOrOpenBlob" in window.navigator) {
            (window.navigator as any).msSaveOrOpenBlob(file, filename);
          }
          // For Firefox and Chrome
          else {
            // Bind blob on disk to ObjectURL
            var data = URL.createObjectURL(file);
            var a = document.createElement("a");
            a.style.display = "none";
            a.href = data;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            // For Firefox
            setTimeout(function () {
              document.body.removeChild(a);
              // Release resource on disk after triggering the download
              window.URL.revokeObjectURL(data);
            }, 100);
          }

          return action;
        },
      };
    });
};

const markAcknowledge = (incident: Incident) => {
  api
    .get(`incidents/${incident.id}/acknowledged`)
    .then(({ data }) => {
      updateTimestampFn();
    })
    .catch(({ error }) => {
      notyf.error(error.detail);
    });
};

const markInaccurate = (incident: Incident) => {
  api
    .get(`incidents/${incident.id}/inaccurate`)
    .then(({ data }) => {
      updateTimestampFn();
    })
    .catch(({ error }) => {
      notyf.error(error.detail);
    });
};

const isMarkActionAvailable = (incident: Incident) => {
  return (
    incident.inaccurate ||
    Boolean(incident.acknowledged) ||
    dayjs.utc() >=
      dayjs
        .utc(incident.created_at)
        .add(
          dayjs.duration(
            Number(import.meta.env.VITE_NOTIFICATION_TIME_WINDOW),
            "seconds"
          )
        )
  );
};

const modalClose = () => (recordModalOpen.value = false);
const updateTimestamp = ref(Date.now());
const updateTimestampFn = () => (updateTimestamp.value = Date.now());

const router = useRoute();
const aiTypeOptions = ref<{ value: number; label: string }[]>([]);
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

watch(
  () => userSession.viewAsCompany,
  () => {
    updateTimestampFn();
  }
);

const tableCrudOptions = {
  path: "/incidents/extra",
  columns: [
    { field: "id", label: "ID", type: "number", sortable: true },
    { field: "frame_url", label: "Frame", type: "image" },
    { field: "created_at", label: "Created", type: "datetime", sortable: true },
    {
      field: "type",
      label: "Type",
      type: (data: any[]) => {
        return data
          .map((index: number) => {
            const type = aiTypeOptions.value.find(
              (typeOption) => typeOption.value === index
            );

            return (type && type.label.replace(/^\[(.*)\].*/, "$1")) || index;
          })
          .join(", ");
      },
    },
    {
      field: "camera.name",
      label: "Camera",
      searchable: "camera__name",
      sortable: "camera__name",
    },
    { field: "location", label: "Location", searchable: true, sortable: true },
    { field: "uuid", label: "UUID", searchable: true, hidden: true },
    {
      field: "acknowledged",
      label: "Ack.",
      type: "boolean",
      sortable: true,
    },
    {
      field: "inaccurate",
      label: "Inc.",
      type: "boolean",
      sortable: true,
    },
  ],
  actions: [
    {
      key: "download",
      global: true,
      action: download,
      label: "Generate PDF",
      title: "Generate and then Download PDF",
      icon: "carbon:generate-pdf",
      buttonProps: {
        color: "primary",
        elevate: true,
      },
    },
    {
      key: "view",
      action: view,
      title: "View incident details",
      icon: "carbon:view",
      buttonProps: {
        color: "info",
        outlined: true,
      },
    },
    {
      key: "acknowledged",
      action: markAcknowledge,
      icon: "carbon:ai-status-complete",
      title: "Mark as acknowledged",
      buttonProps: {
        color: "primary",
        title: "Acknowledge",
        outlined: (incident: Incident) => !Boolean(incident.acknowledged),
        disabled: isMarkActionAvailable,
      },
    },
    {
      key: "inaccurate",
      action: markInaccurate,
      icon: "carbon:ai-status-failed",
      title: "Mark as inaccurate",
      buttonProps: {
        color: "danger",
        title: "Inaccurate",
        outlined: (incident: Incident) => !Boolean(incident.inaccurate),
        disabled: isMarkActionAvailable,
      },
    },
  ],
};
const reportType = ref();
const reportTypeOptions = [
  { value: "day", label: "Daily report" },
  { value: "week", label: "Weekly report" },
  { value: "month", label: "Monthly report" },
  { value: "custom", label: "Custom filtered report" },
];
const changeReportType = (filters: any, reload: Function) => (type: string) => {
  if (reportType.value === "custom" || type === "custom") {
    reload();
  }
};
</script>

<template>
  <CRUDTable
    v-bind="tableCrudOptions"
    :updateTimestamp="updateTimestamp"
    :filterBy="{ ...router.params }"
    :params="{ company_id: asCompany }"
  >
    <template #filters="{ data: filters }">
      <!-- <code style="flex: 1 1 100%">{{ filters }}</code> -->
      <VField horizontal>
        <VField>
          <VControl>
            <VCheckbox
              v-model="filters.acknowledged"
              solid
              label="Acknowledged"
            />
          </VControl>
        </VField>
        <VField>
          <VControl>
            <VCheckbox v-model="filters.inaccurate" solid label="Inaccurate" />
          </VControl>
        </VField>
      </VField>
      <VField label="Detection type">
        <VControl>
          <Multiselect
            v-model="filters.type"
            mode="multiple"
            :options="aiTypeOptions"
            placeholder="Incident type"
            :hide-selected="false"
            :close-on-select="false"
          />
        </VControl>
      </VField>
      <VField label="Location">
        <VControl>
          <QueryMultiSelect
            path="/servers"
            query-key="location"
            v-model="filters.camera__cam_server_id"
            placeholder="Select server"
            label-key="location"
          />
        </VControl>
      </VField>
      <VField label="Cameras" v-if="!filters.camera__cam_server_id">
        <VControl>
          <QueryMultiSelect
            path="/cameras"
            query-key="name"
            v-model="filters.camera_id"
            mode="multiple"
            placeholder="Select cameras"
          />
        </VControl>
      </VField>
      <VField horizontal>
        <VField label="From">
          <DateTimePicker v-model="filters.created_at_from" mode="dateTime" />
        </VField>
        <VField label="To">
          <DateTimePicker v-model="filters.created_at_to" mode="dateTime" />
        </VField>
      </VField>
      <!-- <VField>
        <VControl label="Period">
          <DateTimePicker 
            v-model="filters.created_at"
            isRange
            mode="dateTime"
          />
        </VControl>
      </VField> -->
    </template>
    <template #extraActions="{ data: filters, reload: reload }">
      <VField style="width: 200px" class="mr-2">
        <VControl>
          <Multiselect
            v-model="reportType"
            :options="reportTypeOptions"
            @change="changeReportType(filters, reload)($event)"
            placeholder="Report type"
          />
        </VControl>
      </VField>
    </template>
  </CRUDTable>

  <CRUDModal
    :open="recordModalOpen"
    v-bind="recordModalOptions"
    @close="modalClose"
    @save="updateTimestampFn"
  >
    <template v-slot:form="formProps">
      <VField>
        <VControl>
          <FramePlaceholder :image="formProps.data.frame_url" :video="formProps.data.video_url" />
        </VControl>
      </VField>
      <VField label="UUID">
        <VControl :has-error="formProps.errors.uuid">
          <input
            type="text"
            readonly
            v-model="formProps.data.uuid"
            class="input"
          />
        </VControl>
      </VField>
      <VField label="Location">
        <VControl :has-error="formProps.errors.location">
          <input
            type="text"
            readonly
            v-model="formProps.data.location"
            class="input"
          />
        </VControl>
      </VField>
      <VField horizontal>
        <VField label="People">
          <VControl :has-error="formProps.errors.people">
            <input
              type="number"
              readonly
              v-model="formProps.data.people"
              class="input"
            />
          </VControl>
        </VField>
        <VField label="Objects">
          <VControl :has-error="formProps.errors.objects">
            <input
              type="number"
              readonly
              v-model="formProps.data.objects"
              class="input"
            />
          </VControl>
        </VField>
      </VField>
      <VField label="Type">
        <VControl :has-error="formProps.errors.type">
          <Multiselect
            disabled
            v-model="formProps.data.type"
            mode="tags"
            :options="aiTypeOptions"
          />
        </VControl>
      </VField>
      <VField horizontal>
        <VControl>
          <VSwitchBlock
            readonly
            color="primary"
            label="Acknowledged"
            :modelValue="Boolean(formProps.data.acknowledged)"
          />
        </VControl>
        <VControl>
          <VSwitchBlock
            readonly
            color="warning"
            label="Inaccurate"
            v-model="formProps.data.inaccurate"
          />
        </VControl>
      </VField>
      <VField label="Note">
        <VControl>
          <textarea
            class="textarea"
            rows="4"
            v-model="_get(formProps, 'data.meta', {}).note"
          ></textarea>
        </VControl>
      </VField>
      <VCollapse title="Extra information" withChevron>
        <template #collapse-item-content>
          <VField label="Meta">
            <VControl :has-error="formProps.errors.meta">
              <textarea
                readonly
                class="textarea"
                rows="3"
                :value="JSON.stringify(formProps.data.meta, null, 2)"
              ></textarea>
            </VControl>
          </VField>
          <VField label="Extra">
            <VControl :has-error="formProps.errors.extra">
              <textarea
                readonly
                class="textarea"
                rows="3"
                :value="JSON.stringify(formProps.data.extra, null, 2)"
              ></textarea>
            </VControl>
          </VField>
        </template>
      </VCollapse>
    </template>
  </CRUDModal>
</template>
