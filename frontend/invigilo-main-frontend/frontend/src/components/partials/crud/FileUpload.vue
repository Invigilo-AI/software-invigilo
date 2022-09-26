<script setup lang="ts">
import type {
  FilePond,
  FilePondFile,
  FilePondServerConfigProps,
} from "filepond";
import { onMounted, ref, watch } from "vue";
import { useApi } from "/@src/composable/useApi";

export interface FileUploadEmits {
  (e: "update:modelValue", value?: string): void;
  (e: "change", value?: { object_id: string; object_url: string }): void;
}
export interface FileUploadProps {
  uploadPath?: string;
  modelValue: any;
  id?: any;
}

const emit = defineEmits<FileUploadEmits>();
const props = withDefaults(defineProps<FileUploadProps>(), {
  uploadPath: "/uploads",
});

const filePond = ref<FilePond | null>(null);
const uploadFiles = ref<Record<string, File | null>>({});
const api = useApi();

const setModelValue = () => {
  if (filePond.value) {
    const uploadedFiles = filePond.value.getFiles();

    if (props.modelValue) {
      if (
        typeof props.modelValue === "string" &&
        (!uploadedFiles.length ||
          (uploadedFiles.length &&
            uploadedFiles[0].serverId !== props.modelValue))
      ) {
        const files = [
          {
            source: props.modelValue,
            options: {
              type: "local",
            },
          },
        ];
        filePond.value.addFiles(files as any);
      }
    } else {
      filePond.value.removeFiles();
    }
  }
};

onMounted(setModelValue);

watch(() => props.modelValue, setModelValue);

const onInput = (event: FilePondFile[]) => {
  if (event.length && event[0].serverId === null) return;

  if (event.length && event[0].serverId) {
    const object_id = event[0].serverId;
    emit("update:modelValue", object_id);
  } else {
    emit("update:modelValue");
    emit("change");
  }
};

const onInit = (instance: any) => {
  if (instance) {
    filePond.value = instance;
  }
};

const filePondOn = {
  init: onInit,
  input: onInput,
};

const filePondOptions: FilePondServerConfigProps = {
  server: {
    fetch: null,
    process: (fieldName, file, metadata, load, error, progress, abort) => {
      const formData = new FormData();
      formData.append(fieldName, file, file.name);

      const controller = new AbortController();
      api
        .post(props.uploadPath, formData, {
          signal: controller.signal,
          onUploadProgress: (e) => {
            progress(e.lengthComputable, e.loaded, e.total);
          },
        })
        .then(({ data }) => {
          const { object_id } = data;
          emit("change", data);
          load(object_id);
        })
        .catch(({ error: e }) => {
          error(e && e.detail);
        });
      return {
        abort: () => {
          controller.abort();
          abort();
        },
      };
    },
    revert: (source, load, error) => {
      api
        .delete(props.uploadPath, { params: { object_id: source } })
        .then(() => {
          emit("change");
          load();
        })
        .catch(({ error: e }) => {
          error(e && e.detail);
        });
    },
    load: (source, load, error, progress, abort) => {
      const controller = new AbortController();
      api
        .get(props.uploadPath, {
          params: { object_id: source },
          responseType: "blob",
          signal: controller.signal,
          onDownloadProgress: (e) => {
            progress(e.lengthComputable, e.loaded, e.total);
          },
        })
        .then(({ data }) => {
          emit("change", data);
          load(data);
        })
        .catch(({ error: e }) => {
          error(e && e.detail);
        });

      return {
        abort: () => {
          abort();
        },
      };
    },
  },
};
</script>
<template>
  <VFilePond
    class="filepond-rectangle-wrap"
    name="file"
    :chunk-retry-delays="[500, 1000, 3000]"
    label-idle="<i class='lnil lnil-cloud-upload'></i>"
    :accepted-file-types="['image/png', 'image/jpeg', 'image/gif']"
    :image-preview-height="140"
    :image-resize-target-width="140"
    :image-resize-target-height="140"
    style-panel-layout="compact integrated"
    style-load-indicator-position="center bottom"
    style-progress-indicator-position="right bottom"
    style-button-remove-item-position="left bottom"
    style-button-process-item-position="right bottom"
    v-bind="filePondOptions"
    v-on="filePondOn"
  />
</template>
