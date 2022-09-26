<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";

import { useApi } from "/@src/composable/useApi";
import { useNotyf } from "/@src/composable/useNotyf";

import _pick from "lodash/pick";
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import utc from "dayjs/plugin/utc";
import relativeTime from "dayjs/plugin/relativeTime";
import type { Incident } from "/@src/components/pages/incident/ReportIncident.vue";
import type { Camera } from "/@src/components/pages/incident/CamerasIncident.vue";
import { useUserSession } from "/@src/stores/userSession";

dayjs.extend(duration);
dayjs.extend(utc);
dayjs.extend(relativeTime);

const api = useApi();
const notyf = useNotyf();

const userSession = useUserSession();
const { viewAsCompany, isSuperuser } = userSession;

const asCompany = computed(
  () => (userSession.isSuperuser && userSession.viewAsCompany) || undefined
);

const groupCamera = ref(true);
const onlyServer = ref(null);
const searchBy = ref({});
const searchOptions = {
  location: "Location",
  name: "Camera",
  uuid: "UUID",
};

const incidents = ref<Incident[]>([]);
const paginate = reactive({
  skip: 0,
  limit: 9,
});
const loadMore = ref(true);

const getIncidents = async ({
  reset = false,
  loading = () => void 0,
  loaded = () => void 0,
  complete = () => void 0,
  error = () => void 0,
} = {}) => {
  if (reset) {
    paginate.skip = 0;
    loadMore.value = true;
  }
  loading();
  let path = "incidents/extra";
  let params: any = {
    company_id: asCompany.value,
    ...searchBy.value,
    ...paginate,
  };
  const parseIncidentResults = (incident: Incident) => incident;
  const parseCameraResults = (incident: Camera): Incident | null =>
    (incident.last_incident && {
      ...(incident.last_incident || {}),
      camera: _pick(incident, "id", "name", "location"),
    }) ||
    null;

  if (groupCamera.value) {
    path = "cameras/extra";
    params.with_incident_only = true;
    params.cam_server_id = onlyServer.value || undefined;
  } else {
    params.camera__cam_server_id = onlyServer.value || undefined;
  }
  await api
    .get(path, { params })
    .then((res) => {
      if (res.data.length) {
        incidents.value = (reset ? [] : incidents.value).concat(
          res.data
            .map(groupCamera.value ? parseCameraResults : parseIncidentResults)
            .filter(Boolean)
        );
        paginate.skip += paginate.limit;
        if (res.data.length === paginate.limit) {
          loaded();
        } else {
          complete();
          loadMore.value = false;
        }
      } else {
        complete();
        loadMore.value = false;
        if (reset) incidents.value = [];
      }
    })
    .catch((err) => {
      error();
    });
};

const types = ref({});

api
  .get("ai/types/")
  .then(({ data }) => {
    types.value = data.reduce(
      (acc: object, type: { index: number; name: string }) => ({
        ...acc,
        [type.index]: type.name,
      }),
      {}
    );
  })
  .catch((error) => {
    notyf.error(error.detail);
  });

onMounted(() => {
  getIncidents({ reset: true });
});

watch(
  () => onlyServer.value,
  () => {
    getIncidents({ reset: true });
  }
);

watch(
  () => searchBy.value,
  () => {
    getIncidents({ reset: true });
  }
);

watch(
  () => groupCamera.value,
  () => {
    getIncidents({ reset: true });
  }
);

watch(
  () => userSession.viewAsCompany,
  () => {
    getIncidents({ reset: true });
  }
);
</script>

<template>
  <div>
    <div class="card-grid-toolbar">
      <SearchBy v-model="searchBy" :options="searchOptions" />
      <VField class="h-hidden-mobile">
        <VControl style="width: 200px">
          <QueryMultiSelect
            v-model="onlyServer"
            :searchable="false"
            path="servers"
            label-key="location"
            placeholder="Filter by place"
          />
        </VControl>
      </VField>

      <div class="buttons">
        <VControl>
          <VSwitchBlock
            color="primary"
            label="Group by camera"
            v-model="groupCamera"
          />
        </VControl>
      </div>
    </div>

    <div class="card-grid card-grid-v3">
      <EmptyGrid :hide="Boolean(incidents.length)" />

      <TransitionGroup
        name="list"
        tag="div"
        class="columns is-multiline is-flex-tablet-p is-half-tablet-p"
      >
        <div
          :key="incident.id"
          v-for="incident in incidents"
          class="column is-4"
        >
          <div class="card v-card">
            <FramePlaceholder class="card-image" :image="incident.frame_url" :video="incident.video_url" />
            <div class="card-content">
              <div>
                <span
                  class="iconify"
                  data-icon="carbon:hashtag"
                  data-inline="false"
                ></span>
                {{ incident.uuid }}
              </div>
              <!-- <div>
                <span
                  class="iconify"
                  data-icon="carbon:machine-learning-model"
                  data-inline="false"
                ></span>
                {{incident.type.map(type => types[type] || type).join(', ')}}
              </div> -->
              <div>
                <span
                  class="iconify"
                  data-icon="carbon:video"
                  data-inline="false"
                ></span>
                {{ incident.camera.name }}
              </div>
              <div>
                <span
                  class="iconify"
                  data-icon="carbon:location"
                  data-inline="false"
                ></span>
                {{ incident.location }}
              </div>
              <div
                v-tooltip="
                  dayjs
                    .utc(incident.created_at)
                    .local()
                    .format('dddd, MMMM D YYYY, HH:mm:ss')
                "
              >
                <span
                  class="iconify"
                  data-icon="carbon:time"
                  data-inline="false"
                ></span>
                {{ dayjs.utc(incident.created_at).local().fromNow() }}
              </div>
              <br />
              <br />
              <div class="stats">
                <div class="stat">
                  <span>
                    {{ incident.count }}
                  </span>
                  <span>Count</span>
                </div>
                <div class="separator"></div>
                <div class="stat">
                  <span>{{ incident.people }}</span>
                  <span>People</span>
                </div>
                <div class="separator"></div>
                <div class="stat">
                  <span>{{ incident.objects }}</span>
                  <span>Objects</span>
                </div>
              </div>
              <br />
              <VTags>
                <VTag
                  v-for="type in incident.type"
                  :key="type"
                  color="solid"
                  :label="types[type] || type"
                />
              </VTags>
            </div>
          </div>
        </div>
      </TransitionGroup>
      <InfiniteLoading
        class="align-center"
        @infinite="getIncidents"
        v-if="loadMore"
        :firstLoad="false"
      />
    </div>
  </div>
</template>

<style lang="scss">
@import "../../../scss/abstracts/mixins";

.stats {
  width: 100%;
  display: flex;
  align-items: center;
  margin-right: 30px;
  justify-content: space-evenly;

  .stat {
    display: flex;
    align-items: center;
    flex-direction: column;
    text-align: center;
    color: var(--light-text);

    > span {
      font-family: var(--font);

      &:first-child {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--dark-text);
        line-height: 1.4;
      }

      &:nth-child(2) {
        text-transform: uppercase;
        font-family: var(--font-alt);
        font-size: 0.75rem;
      }
    }

    svg {
      height: 16px;
      width: 16px;
    }

    i {
      font-size: 1.4rem;
    }
  }

  .separator {
    height: 25px;
    width: 2px;
    border-right: 1px solid var(--fade-grey-dark-3);
    margin: 0 16px;
  }
}

.align-center {
  text-align: center;
}

.card-grid {
  .columns {
    margin-left: -0.5rem !important;
    margin-right: -0.5rem !important;
    margin-top: -0.5rem !important;
  }

  .column {
    padding: 0.5rem !important;
  }
}

.card-grid-v3 {
  .card-grid-item {
    @include vuero-s-card;

    position: relative;
    text-align: center;
    padding: 30px;

    .buttons {
      display: flex;
      justify-content: space-between;

      .button {
        width: calc(50% - 4px);
        color: var(--light-text);

        &:hover,
        &:focus {
          border-color: var(--fade-grey-dark-4);
          color: var(--primary);
          box-shadow: var(--light-box-shadow);
        }
      }
    }
  }
}

.is-dark {
  .card-grid-v3 {
    .card-grid-item {
      @include vuero-card--dark;
    }
  }
}
</style>
