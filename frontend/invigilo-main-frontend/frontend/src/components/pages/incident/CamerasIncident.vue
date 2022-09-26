<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";

import { useApi } from "/@src/composable/useApi";
import type { Incident } from "/@src/components/pages/incident/ReportIncident.vue";
import { useUserSession } from "/@src/stores/userSession";

export type Camera = {
  id: number;
  name: string;
  location: string;
  is_live: boolean;
  last_frame: null | CameraFrame;
  last_incident: null | Incident
};

type CameraFrame = {
  image?: string;
};

const onlyServer = ref(null);
const searchBy = ref({});
const searchOptions = {
  name: "Name",
  location: "Location",
  description: "Description",
};

const cameras = ref<Camera[]>([]);
const paginate = reactive({
  skip: 0,
  limit: 9,
});
const loadMore = ref(true);
const api = useApi();
const userSession = useUserSession();
const { viewAsCompany, isSuperuser } = userSession;

const asCompany = computed(
  () => (userSession.isSuperuser && userSession.viewAsCompany) || undefined
);

const getCameras = async ({
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
  await api
    .get("cameras/extra", {
      params: {
        company_id: asCompany.value,
        ...searchBy.value,
        ...paginate,
        cam_server_id: onlyServer.value || undefined,
      },
    })
    .then((res) => {
      if (res.data.length) {
        cameras.value = (reset ? [] : cameras.value).concat(res.data);
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
        if (reset) cameras.value = [];
      }
    })
    .catch((err) => {
      if (reset) cameras.value = [];
      error();
    });
};

onMounted(() => {
  getCameras({ reset: true });
});

watch(
  () => onlyServer.value,
  () => {
    getCameras({ reset: true });
  }
);

watch(
  () => searchBy.value,
  () => {
    getCameras({ reset: true });
  }
);

watch(
  () => asCompany.value,
  () => {
    getCameras({ reset: true });
  }
);
</script>

<template>
  <div>
    <!-- <code>{{JSON.stringify(searchBy)}}</code> -->
    <div class="card-grid-toolbar">
      <SearchBy v-model="searchBy" :options="searchOptions" />

      <div class="buttons">
        <VField>
          <VControl>
            <QueryMultiSelect
              v-model="onlyServer"
              :searchable="false"
              path="servers"
              placeholder="Filter by server"
            />
          </VControl>
        </VField>
      </div>
    </div>

    <div class="card-grid card-grid-v3">
      <EmptyGrid :hide="Boolean(cameras.length)" />

      <TransitionGroup
        name="list"
        tag="div"
        class="columns is-multiline is-flex-tablet-p is-half-tablet-p"
      >
        <div :key="camera.id" v-for="camera in cameras" class="column is-4">
          <div class="card v-card">
            <FramePlaceholder
              class="card-image"
              :image="camera.last_frame?.image_url || ''"
              :video="camera.last_frame?.video_url || ''"
            />
            <div class="card-content">
              <VBlock
                :title="camera.name"
                :subtitle="camera.location"
                center
                narrow
              >
                <template #icon>
                  <VIconBox
                    size="medium"
                    :color="camera.is_live ? 'primary' : 'danger'"
                    rounded
                  >
                    <i
                      class="iconify"
                      :data-icon="
                        camera.is_live
                          ? 'carbon:video-filled'
                          : 'carbon:video-off-filled'
                      "
                      aria-hidden="true"
                    />
                  </VIconBox>
                </template>
                <template #action>
                  <RouterLink
                    :to="{
                      name: 'incident-report',
                      params: { camera_id: [camera.id] },
                    }"
                    v-slot="{ navigate }"
                  >
                    <VButton outlined @click="navigate" role="link"
                      >Incidents</VButton
                    >
                  </RouterLink>
                </template>
              </VBlock>

              <div class="stats">
                <div class="stat">
                  <span>
                    <VNum
                      #="{ number }"
                      :value="camera.stats.activity"
                      maximum-fraction-digits="2"
                      >{{ number }}%</VNum
                    >
                  </span>
                  <span>Activity</span>
                </div>
                <div class="separator"></div>
                <div class="stat">
                  <span>{{ camera.stats.people }}</span>
                  <span>People</span>
                </div>
                <div class="separator"></div>
                <div class="stat">
                  <span>{{ camera.stats.objects }}</span>
                  <span>Objects</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>
      <InfiniteLoading
        class="align-center"
        @infinite="getCameras"
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
