<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import { CRUDModalProps } from "/@src/components/partials/crud/CRUDModal.vue";
import _omit from "lodash/omit";
import _get from "lodash/get";
import _pick from "lodash/pick";
import _defaultsDeep from "lodash/defaultsDeep";
import _merge from "lodash/merge";
import _set from "lodash/set";
import _isNil from "lodash/isNil";
import _negate from "lodash/negate";
import _cloneDeep from "lodash/cloneDeep";
import type { BoundaryData } from "/@src/components/partials/crud/BoundaryEditor.vue";
import { useApi } from "/@src/composable/useApi";

type AI_Mapping = {
  name?: string;
  sequence_id?: number;
  meta?: object;
};

type FormProps = {
  data: { ai_mapping: AI_Mapping[] };
  errors: { ai_mapping?: string };
};

const omitFields = ["created_at", "updated_at"];
const omitMappingFields = [...omitFields, "camera_id"];
const omitFieldsOnSave = [...omitFields, "cam_server"];
const recordModalOpen = ref(false);
const recordModalOptions = ref<CRUDModalProps>({
  path: {
    get: "/cameras/{id}/extended",
    post: "/cameras/",
    put: "/cameras/{id}",
  },
  titleVar: "camera",
  data: { ai_mapping: [] },
  transform: (data) => ({
    ..._omit(data, omitFields),
    ai_mapping: data.ai_mapping.map((map: AI_Mapping) =>
      _omit(map, omitMappingFields)
    ),
  }),
  transformOnSave: (data) => ({
    ..._omit(data, omitFieldsOnSave),
  }),
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

const cameraMapModalOpen = ref(false);
const cameraMapServerId = ref();
const cameraMapServerIdCurrent = ref();
const cameraMapData = ref<any[]>([]);
const cameraMapOptionData = ref<any | null>(null);
const cameraMapLevel = ref<null | any>(null);
const openCameraMapModal = () => {
  cameraMapModalOpen.value = true;
  cameraMapServerId.value = undefined;
  cameraMapServerIdCurrent.value = undefined;
  cameraMapData.value = [];
  cameraMapOptionData.value = null;
  changedCameraMap.value = false;
};
const closeCameraMapModal = () => {
  cameraMapModalOpen.value = false;
  cameraMapData.value = [];
  changedCameraMap.value = false;
};
const addCameraMapLevel = () => {
  const idx = (cameraMapData.value.length || 0) + 1;
  cameraMapData.value.push({ name: `Level #${idx}` });
  changedCameraMap.value = true;
  viewCameraMapLevel(idx - 1);
};
const removeCameraMapLevel = (idx: number) => {
  cameraMapData.value.splice(idx, 1);
  changedCameraMap.value = true;
  viewCameraMapLevel();
};
const viewCameraMapLevel = (idx?: number) => {
  const currentLevel =
    cameraMapLevel.value && cameraMapData.value[cameraMapLevel.value.idx];
  if (currentLevel) {
    currentLevel.cameras = [];
    _merge(
      currentLevel,
      _pick(cameraMapLevel.value, ["name", "image_url"]),
      _pick(cameraMapLevel.value.data, ["image", "cameras"])
    );
    changedCameraMap.value = true;
  }
  if (typeof idx === "undefined") {
    cameraMapLevel.value = null;
  } else {
    const level = cameraMapData.value[idx];

    cameraMapLevel.value = {
      ..._pick(level, ["name", "image_url"]),
      idx,
      data: {
        image: {
          file_name: _get(level, "image.file_name"),
          width: _get(level, "image.width"),
          height: _get(level, "image.height"),
        },
        cameras: _cloneDeep(_get(level, "cameras", [])),
      },
    };
  }
};
const onCameraMapLevelImage = (data: Record<string, string> | File) => {
  if (!data) {
    _set(cameraMapLevel.value, "data.image.file_name", undefined);
    _set(cameraMapLevel.value, "data.cameras", []);
    _set(cameraMapLevel.value, "image_url", undefined);

    changedCameraMap.value = true;
  } else if (data instanceof Blob) {
    var img = new Image();
    var blob = URL.createObjectURL(data);
    img.src = blob;
    img.onload = function () {
      const { width, height } = img;
      _set(cameraMapLevel.value, "data.image.width", width);
      _set(cameraMapLevel.value, "data.image.height", height);
    };
  } else {
    const { object_id: image, object_url: image_url } = data || {};

    if (image && image_url) {
      _set(cameraMapLevel.value, "data.image.file_name", image);
      _set(cameraMapLevel.value, "data.cameras", []);
      _set(cameraMapLevel.value, "image_url", image_url);

      changedCameraMap.value = true;

      var img = new Image();
      img.src = image_url;
      img.onload = function () {
        const { width, height } = img;
        _set(cameraMapLevel.value, "data.image.width", width);
        _set(cameraMapLevel.value, "data.image.height", height);
      };
    }
  }
};
const boundaryEditorImage = computed(
  () => cameraMapLevel.value && cameraMapLevel.value?.data?.image?.file_name
);
const boundaryEditorSize = computed(() =>
  _pick(_get(cameraMapLevel.value, "data.image"), ["width", "height"])
);
const boundaryEditorBackground = computed(
  () => cameraMapLevel.value && cameraMapLevel.value?.image_url
);
const boundaryEditorData = computed({
  get: () => cameraMapLevel.value && cameraMapLevel.value?.data,
  set: (v) => _set(cameraMapLevel.value, "data", v),
});

const onChangeMap = () => {
  changedCameraMap.value = true;
};

const onSelectServer = (option: any) => {
  if (
    cameraMapServerIdCurrent.value &&
    cameraMapServerIdCurrent.value !== cameraMapServerId.value &&
    !confirm("You change the server, unsaved data will be lose. \nContinue?")
  ) {
    nextTick(() => {
      cameraMapServerId.value = cameraMapServerIdCurrent.value;
    });
    return;
  }
  changedCameraMap.value = false;
  cameraMapServerIdCurrent.value = cameraMapServerId.value;
  cameraMapOptionData.value = option?.meta || null;
  cameraMapData.value = _cloneDeep(option?.meta?.levels) || [];

  viewCameraMapLevel(cameraMapData.value.length ? 0 : undefined);
};

const api = useApi();
const loadingCameraMap = ref(false);
const changedCameraMap = ref(false);
const saveCameraMap = async () => {
  loadingCameraMap.value = true;
  await api
    .put(`servers/${cameraMapServerId.value}/extra`, {
      meta: {
        ...cameraMapOptionData.value,
        levels: cameraMapData.value.map((level, idx) => {
          if (cameraMapLevel.value && cameraMapLevel.value.idx === idx) {
            return {
              ..._pick(cameraMapLevel.value, ["name"]),
              ..._cloneDeep(
                _pick(cameraMapLevel.value.data, ["image", "cameras"])
              ),
            };
          } else {
            return level;
          }
        }),
      },
    })
    .then(({ data }) => {
      cameraMapOptionData.value = data.meta;
      cameraMapData.value = data.meta.levels;

      if (cameraMapLevel.value) {
        cameraMapLevel.value = {
          ...cameraMapLevel.value,
          ..._pick(cameraMapData.value[cameraMapLevel.value.idx], [
            "image_url",
          ]),
          data: _cloneDeep(
            _pick(cameraMapData.value[cameraMapLevel.value.idx], [
              "image",
              "cameras",
            ])
          ),
        };
      }
    })
    .catch((error) => {
      console.error("error", error);
    });
  loadingCameraMap.value = false;
};

const modalClose = () => (recordModalOpen.value = false);
const updateTimestamp = ref(Date.now());
const updateTimestampFn = () => (updateTimestamp.value = Date.now());

const tableCrudOptions = {
  path: "/cameras/extra",
  columns: [
    { field: "id", label: "ID", type: "number", sortable: true },
    { field: "name", label: "Name", sortable: true, searchable: true },
    { field: "location", label: "location", sortable: true, searchable: true },
    {
      field: "cam_server.name",
      label: "Server",
      sortable: "cam_server__name",
      searchable: "cam_server__name",
    },
    { field: "is_active", label: "Active", type: "boolean", sortable: true },
    { field: "is_live", label: "Live", type: "status", sortable: true },
  ],
  actions: [
    {
      key: "map",
      global: true,
      action: openCameraMapModal,
      label: "Map",
      icon: "carbon:floorplan",
      buttonProps: {
        color: "info",
        outlined: true,
      },
    },
    {
      key: "create",
      global: true,
      action: create,
      label: "Camera",
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

const addMapping = (formProps: FormProps) => {
  formProps.data.ai_mapping.push({});
};
const removeMapping = (formProps: FormProps, idx: number) => {
  formProps.data.ai_mapping.splice(idx, 1);
};
const mapData = (
  formProps: FormProps,
  idx: number,
  field?: string,
  set: boolean = true
) => {
  const fieldPath = ["ai_mapping", idx, field]
    .filter(_negate(_isNil))
    .join(".");
  const data = _get(formProps.data, fieldPath);

  if (set && _isNil(data)) {
    _set(formProps.data, fieldPath, {});
  }
  return _get(formProps.data, fieldPath);
};
const mapError = (formProps: FormProps, idx: number, field: string) =>
  Boolean(
    _get(
      formProps.errors,
      ["ai_mapping", idx, field].filter(_negate(_isNil)).join("."),
      false
    )
  );

const boundaryModalOpen = ref(false);
const formDataMeta = ref<{ meta: { boundaries: BoundaryData } } | null>(null);
const boundaryData = ref({});
const boundaryBackground = ref({});
const openBoundaryModal = (frame: any, formData: any) => {
  boundaryModalOpen.value = true;

  formDataMeta.value = formData;
  if (formDataMeta.value && formDataMeta.value.meta) {
    boundaryData.value = _cloneDeep(formDataMeta.value.meta.boundaries || []);
  }

  boundaryBackground.value = frame;
};
const saveBoundaryData = () => {
  if (!formDataMeta.value) return;

  if (formDataMeta.value && formDataMeta.value.meta) {
    // @ts-ignore
    formDataMeta.value.meta.boundaries = _cloneDeep(boundaryData.value);
  } else {
    formDataMeta.value.meta = {
      // @ts-ignore
      boundaries: _cloneDeep(boundaryData.value),
    };
  }
  closeBoundaryModal();
};
const closeBoundaryModal = () => {
  boundaryModalOpen.value = false;
  boundaryData.value = {};
};
</script>

<template>
  <CRUDTable
    v-bind="tableCrudOptions"
    :updateTimestamp="updateTimestamp"
    searchable
  />

  <CRUDModal
    :open="recordModalOpen"
    v-bind="recordModalOptions"
    @close="modalClose"
    @save="updateTimestampFn"
  >
    <template v-slot:form="formProps">
      <VField label="Name">
        <VControl :has-error="formProps.errors.name">
          <input type="text" v-model="formProps.data.name" class="input" />
        </VControl>
      </VField>
      <VField label="Server">
        <VControl :has-error="formProps.errors.cam_server_id">
          <QueryMultiSelect
            path="servers"
            query-key="name"
            v-model="formProps.data.cam_server_id"
          />
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
      <br />
      <div
        class="form-section"
        :key="idx"
        v-for="(map, idx) in formProps.data.ai_mapping"
      >
        <VButton
          icon="carbon:misuse-outline"
          color="danger"
          fullwidth
          bold
          outlined
          @click="removeMapping(formProps, idx)"
          >Remove ({{ idx + 1 }})</VButton
        >
        <br />
        <VField label="Sequence name">
          <VControl :has-error="mapError(formProps, idx, 'name')">
            <input
              type="text"
              v-model="mapData(formProps, idx).name"
              class="input"
            />
          </VControl>
        </VField>
        <VField label="AI Sequence">
          <VControl :has-error="mapError(formProps, idx, 'sequence_id')">
            <QueryMultiSelect
              path="ai/sequences"
              query-key="name"
              v-model="mapData(formProps, idx).sequence_id"
              :format-option="
                ({ id: value, name: label, description }) => ({
                  value,
                  label,
                  description,
                })
              "
            >
              <template v-slot="{ option }">
                <div>
                  <strong>{{ option.label }}</strong>
                  <em v-if="option.description"> - {{ option.description }}</em>
                </div>
              </template>
            </QueryMultiSelect>
          </VControl>
        </VField>
        <VCollapse title="Settings" withChevron>
          <template #collapse-item-content>
            <!-- <code>{{ JSON.stringify(formProps.data.meta) }}</code> -->
            <VField horizontal v-if="formProps.data.last_frame">
              <VButton
                icon="carbon:map-boundary"
                color="warning"
                fullwidth
                outlined
                @click="
                  openBoundaryModal(
                    formProps.data.last_frame,
                    mapData(formProps, idx)
                  )
                "
                >Add frame boundaries</VButton
              >
            </VField>
            <VField label="Analytics FPS">
              <VControl :has-error="mapError(formProps, idx, 'meta.fps')">
                <input
                  type="number"
                  placeholder="1"
                  min="0"
                  v-model="mapData(formProps, idx, 'meta').fps"
                  class="input"
                />
              </VControl>
            </VField>
            <VField label="Meta">
              <VControl :has-error="formProps.errors.meta">
                <textarea
                  readonly
                  class="textarea"
                  rows="3"
                  :value="
                    JSON.stringify(mapData(formProps, idx, 'meta'), null, 2)
                  "
                ></textarea>
              </VControl>
            </VField>
          </template>
        </VCollapse>
      </div>
      <VButton
        icon="carbon:add-alt"
        color="success"
        fullwidth
        bold
        outlined
        @click="addMapping(formProps)"
        >Add AI sequence</VButton
      >
    </template>
  </CRUDModal>

  <VModal
    :open="boundaryModalOpen"
    title="Edit camera boundaries"
    size="large"
    actions="right"
    :noclose="true"
    noscroll
    @close="closeBoundaryModal"
  >
    <template #content>
      <BoundaryEditor
        :image="boundaryBackground?.image"
        :background="boundaryBackground.image_url"
        v-model="boundaryData"
      />
      <!-- <code>{{ JSON.stringify(boundaryData, null, 2) }}</code> -->
    </template>
    <template #action>
      <VButton color="primary" raised @click="saveBoundaryData">Save</VButton>
    </template>
  </VModal>

  <VModal
    :open="cameraMapModalOpen"
    title="Cameras map"
    size="large"
    actions="right"
    :noclose="true"
    noscroll
    @close="closeCameraMapModal"
  >
    <template #content>
      <VField label="Server">
        <VControl>
          <QueryMultiSelect
            path="servers/extra"
            labelKey="location"
            v-model="cameraMapServerId"
            placeholder="Server location"
            @change="onSelectServer"
          />
        </VControl>
      </VField>
      <template v-if="cameraMapServerId">
        <VField addons :key="idx" v-for="(level, idx) in cameraMapData">
          <VControl>
            <VIconButton
              v-if="!cameraMapLevel || cameraMapLevel.idx !== idx"
              icon="carbon:view"
              color="info"
              static
              lower
              @click="viewCameraMapLevel(idx)"
              outlined
            />
            <VIconButton
              v-else
              icon="carbon:view-filled"
              color="info"
              static
              lower
            />
          </VControl>
          <VControl expanded>
            <input type="text" class="input" v-model="level.name" />
          </VControl>
          <VControl>
            <VIconButton
              icon="carbon:delete"
              color="danger"
              static
              lower
              @click="removeCameraMapLevel(idx)"
            />
          </VControl>
        </VField>
        <VField>
          <VButton
            icon="carbon:add"
            color="success"
            outlined
            fullwidth
            @click="addCameraMapLevel"
            >Add level</VButton
          >
        </VField>
        <!-- <code>{{ JSON.stringify(boundaryEditorData, null, 2) }}</code> -->
        <template v-if="cameraMapLevel">
          <FileUpload
            v-if="cameraMapLevel?.data"
            v-model="cameraMapLevel.data.image.file_name"
            @change="onCameraMapLevelImage"
          />
          <BoundaryEditor
            v-if="boundaryEditorData"
            :image="boundaryEditorImage"
            :background="boundaryEditorBackground"
            v-model="boundaryEditorData"
            boundaryKey="cameras"
            :exclude-tool="['point', 'rect', 'ellipse', 'polygon', 'path']"
            :allow-tool="['camera']"
            @change="onChangeMap"
            responsive
          >
            <template v-slot:transform="{ shape, remove }">
              <VField horizontal v-show="shape">
                <VField addons>
                  <VControl expanded>
                    <QueryMultiSelect
                      path="cameras"
                      placeholder="Select camera"
                      :params="{ cam_server_id: cameraMapServerId }"
                      v-model="shape.config.meta"
                    />
                  </VControl>
                </VField>
                <VField addons>
                  <VControl expanded>
                    <input
                      type="number"
                      min="1"
                      max="360"
                      class="input"
                      placeholder="Angle"
                      v-model="shape.config.angle"
                    />
                  </VControl>
                  <VControl expanded>
                    <input
                      type="number"
                      min="1"
                      max="360"
                      class="input"
                      placeholder="Range"
                      v-model="shape.config.range"
                    />
                  </VControl>
                  <VControl>
                    <VButton color="danger" @click="remove(shape.id)"
                      >Delete</VButton
                    >
                  </VControl>
                </VField>
              </VField>
              <!-- <code>{{ JSON.stringify(shape.config, null, 2) }}</code> -->
            </template>
          </BoundaryEditor>
        </template>
        <!-- <code>{{ JSON.stringify(cameraMapLevel, null, 2) }}</code> -->
      </template>
      <div v-else class="p-b-100" />
    </template>
    <template #action>
      <VButton
        color="primary"
        raised
        @click="saveCameraMap"
        :loading="loadingCameraMap"
        :disabled="!changedCameraMap"
        >Save</VButton
      >
    </template>
  </VModal>
</template>
